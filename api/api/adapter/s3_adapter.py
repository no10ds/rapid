import os
from pathlib import Path
from typing import Dict, List, Optional, Type, Union

import boto3
from botocore.exceptions import ClientError
from botocore.response import StreamingBody

from api.application.services.partitioning_service import Partition
from api.common.config.aws import (
    AWS_REGION,
    DATA_BUCKET,
    OUTPUT_QUERY_BUCKET,
)
from api.common.config.constants import (
    CONTENT_ENCODING,
    QUERY_RESULTS_LINK_EXPIRY_SECONDS,
)
from api.common.custom_exceptions import AWSServiceError, UserError
from api.common.logger import AppLogger
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.schema import Schema


class S3Adapter:
    def __init__(
        self,
        s3_client=boto3.client(
            "s3",
            region_name=AWS_REGION,
            config=boto3.session.Config(signature_version="s3v4"),
        ),
        s3_bucket=DATA_BUCKET,
    ):
        self.__s3_client = s3_client
        self.__s3_bucket = s3_bucket

    def store_data(self, object_full_path: str, object_content: bytes):
        self._validate_file(object_content, object_full_path)

        self.__s3_client.put_object(
            Bucket=self.__s3_bucket, Key=object_full_path, Body=object_content
        )

    def retrieve_data(self, key: str) -> StreamingBody:
        response: Dict = self.__s3_client.get_object(Bucket=self.__s3_bucket, Key=key)
        return response.get("Body")

    def find_raw_file(self, dataset: DatasetMetadata, filename: str):
        try:
            self.retrieve_data(dataset.raw_data_path(filename))
        except ClientError as error:
            if error.response["Error"]["Code"] == "NoSuchKey":
                raise UserError(f"The file [{filename}] does not exist")

    def upload_partitioned_data(
        self,
        schema: Schema,
        filename: str,
        partitions: List[Partition],
    ):
        for partition in partitions:
            upload_path = self._construct_partitioned_data_path(
                partition.path, filename, schema.dataset_metadata
            )
            data_content = partition.df.to_parquet(
                compression="gzip", index=False, schema=schema.generate_storage_schema()
            )
            self.store_data(upload_path, data_content)

    def upload_raw_data(
        self, dataset_metadata: DatasetMetadata, file_path: Path, raw_file_identifier: str
    ):
        AppLogger.info(
            f"Raw data upload for {dataset_metadata.raw_data_location()} started"
        )
        filename = f"{raw_file_identifier}.csv"
        raw_data_path = dataset_metadata.raw_data_path(filename)
        self.__s3_client.upload_file(
            Filename=file_path.name, Bucket=self.__s3_bucket, Key=raw_data_path
        )
        AppLogger.info(
            f"Raw data upload for {dataset_metadata.glue_table_name()} completed"
        )

    def list_raw_files(self, dataset: DatasetMetadata) -> List[str]:
        object_list = self.list_files_from_path(dataset.raw_data_location())
        return self._map_object_list_to_filename(object_list)

    def list_dataset_files(self, dataset: DatasetMetadata) -> List[Dict]:
        return [
            *self.list_files_from_path(
                dataset.construct_raw_dataset_uploads_location()
            ),
            *self.list_files_from_path(dataset.dataset_location(with_version=False)),
        ]

    def get_last_updated_time(self, file_path: str) -> Optional[str]:
        """
        :return: Returns the last updated time for the dataset
        """
        paginator = self.__s3_client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=self.__s3_bucket, Prefix=file_path)
        try:
            return str(
                max(
                    [
                        item["LastModified"]
                        for page in page_iterator
                        for item in page["Contents"]
                    ]
                )
            )
        except KeyError:
            return None

    def get_folder_size(self, file_path: str) -> int:
        """
        :return: Returns the size in bytes.
        """
        try:
            paginator = self.__s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(
                Bucket=self.__s3_bucket, Prefix=file_path
            )
            return sum(
                [item["Size"] for page in page_iterator for item in page["Contents"]]
            )
        except KeyError:
            return 0

    def delete_dataset_files(
        self, dataset: DatasetMetadata, raw_data_filename: str
    ) -> None:
        """
        Deletes the raw file and the corresponding data file
        """
        files = self.list_files_from_path(dataset.dataset_location())
        raw_file_identifier = self._clean_filename(raw_data_filename)

        files_to_delete = [
            {"Key": data_file}
            for data_file in files
            if self._clean_filename(data_file).startswith(raw_file_identifier)
        ]

        self._delete_objects(files_to_delete, raw_data_filename)

    def delete_previous_dataset_files(
        self, dataset: Type[DatasetMetadata], raw_file_identifier: str
    ):
        files = self.list_files_from_path(dataset.dataset_location())
        files_to_delete = [
            file
            for file in files
            if not self._extract_filename(file).startswith(raw_file_identifier)
        ]
        for file in files_to_delete:
            self._delete_data(file)

    def delete_dataset_files_using_key(self, keys: List[str], filename: str):
        files_to_delete = [{"Key": key} for key in keys]
        self._delete_objects(files_to_delete, filename)

    def delete_raw_dataset_files(
        self,
        dataset: DatasetMetadata,
        raw_data_filename: str,
    ):
        files_to_delete = [{"Key": dataset.raw_data_path(raw_data_filename)}]

        self._delete_objects(files_to_delete, raw_data_filename)

    def generate_query_result_download_url(self, query_execution_id: str) -> str:
        try:
            return self.__s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": OUTPUT_QUERY_BUCKET,
                    "Key": f"{query_execution_id}.csv",
                },
                HttpMethod="GET",
                ExpiresIn=QUERY_RESULTS_LINK_EXPIRY_SECONDS,
            )
        except ClientError as error:
            AppLogger.error(
                f"Unable to generate pre-signed URL for execution ID {query_execution_id}, {error}"
            )
            raise AWSServiceError("Unable to generate download URL")

    def _clean_filename(self, file_key: str) -> str:
        return file_key.rsplit("/", 1)[-1].split(".")[0]

    def _construct_partitioned_data_path(
        self, partition_path: str, filename: str, dataset: Type[DatasetMetadata]
    ) -> str:
        return os.path.join(dataset.dataset_location(), partition_path, filename)

    def _delete_objects(self, files_to_delete: List[Dict], filename: str):
        if files_to_delete:
            response = self.__s3_client.delete_objects(
                Bucket=self.__s3_bucket, Delete={"Objects": files_to_delete}
            )
            self._handle_deletion_response(filename, response)
        else:
            AppLogger.info(f"No files to delete for: {filename}")

    def _handle_deletion_response(self, filename, response):
        if "Deleted" in response:
            AppLogger.info(
                f'Files deleted: {[item["Key"] for item in response["Deleted"]]}'
            )
        if "Errors" in response:
            message = "\n".join([str(error) for error in response["Errors"]])
            AppLogger.error(f"Error during file deletion [{filename}]: \n{message}")
            raise AWSServiceError(
                f"The item [{filename}] could not be deleted. Please contact your administrator."
            )

    def list_files_from_path(self, file_path: str) -> List[Dict]:
        try:
            paginator = self.__s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(
                Bucket=self.__s3_bucket, Prefix=file_path
            )
            return [item["Key"] for page in page_iterator for item in page["Contents"]]
        except KeyError:
            return []

    def _map_object_list_to_filename(self, object_list) -> List[str]:
        if len(object_list) > 0:
            return [
                self._extract_filename(item)
                for item in object_list
                if self._extract_filename(item)
            ]
        return object_list

    def _extract_filename(self, item: str) -> str:
        return item.rsplit("/", 1)[-1]

    def _convert_to_bytes(self, data: str):
        return bytes(data.encode(CONTENT_ENCODING))

    def _validate_file(self, object_content, object_full_path):
        if not self._valid_object_name(object_full_path):
            raise UserError("File path is invalid")
        if not self._valid_object_content(object_content):
            raise UserError("File content is invalid")

    def _valid_object_name(self, object_name: str) -> bool:
        return self._has_content(object_name)

    def _valid_object_content(self, object_content: bytes) -> bool:
        return self._has_content(object_content)

    def _has_content(self, element: Union[str, bytes]) -> bool:
        return element is not None and len(element) > 0

    def _delete_data(self, object_full_path: str):
        self.__s3_client.delete_object(Bucket=self.__s3_bucket, Key=object_full_path)
