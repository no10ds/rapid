from time import sleep
from typing import Dict, List

import boto3
from botocore.exceptions import ClientError

from api.common.config.aws import (
    AWS_REGION,
    GLUE_CATALOGUE_DB_NAME,
    GLUE_TABLE_PRESENCE_CHECK_INTERVAL,
    GLUE_TABLE_PRESENCE_CHECK_RETRY_COUNT,
)
from api.common.custom_exceptions import (
    AWSServiceError,
    TableAlreadyExistsError,
    TableCreationError,
    TableDoesNotExistError,
)
from api.common.logger import AppLogger
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.schema import Schema


class GlueAdapter:
    def __init__(
        self,
        glue_client=boto3.client("glue", region_name=AWS_REGION),
        glue_catalogue_db_name=GLUE_CATALOGUE_DB_NAME,
    ):
        self.glue_client = glue_client
        self.glue_catalogue_db_name = glue_catalogue_db_name

    def create_table(self, schema: Schema):
        try:
            self.glue_client.create_table(
                DatabaseName=self.glue_catalogue_db_name,
                TableInput={
                    "Name": schema.dataset_metadata.glue_table_name(),
                    "Owner": "hadoop",
                    "StorageDescriptor": {
                        "Columns": schema.get_non_partition_columns_for_glue(),
                        "Location": schema.dataset_metadata.s3_file_location(),
                        "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                        "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                        "Compressed": False,
                        "SerdeInfo": {
                            "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                            "Parameters": {"serialization.format": "1"},
                        },
                        "NumberOfBuckets": -1,
                        "StoredAsSubDirectories": False,
                    },
                    "PartitionKeys": schema.get_partition_columns_for_glue(),
                    "TableType": "EXTERNAL_TABLE",
                    "Parameters": {
                        "classification": "parquet",
                        "typeOfData": "file",
                        "compressionType": "none",
                        "EXTERNAL": "TRUE",
                    },
                },
                PartitionIndexes=[
                    {
                        "Keys": [
                            col["Name"]
                            for col in schema.get_partition_columns_for_glue()
                        ],
                        "IndexName": "rapid-creation-partition",
                    },
                ]
                if schema.get_partition_columns_for_glue()
                else [],
            )
        except ClientError as error:
            self._handle_table_create_error(error)

    def _handle_table_create_error(self, error: ClientError):
        if error.response["Error"]["Code"] == "AlreadyExistsException":
            raise TableAlreadyExistsError("Table already exists with same name")
        else:
            raise TableCreationError("Table creation error")

    def get_table_when_created(self, table_name: str) -> Dict:
        for _ in range(GLUE_TABLE_PRESENCE_CHECK_RETRY_COUNT):
            try:
                return self._get_table(table_name)
            except TableDoesNotExistError:
                AppLogger.info(
                    f"Waiting {GLUE_TABLE_PRESENCE_CHECK_INTERVAL}s for table [{table_name}] to be created"
                )
                sleep(GLUE_TABLE_PRESENCE_CHECK_INTERVAL)
                continue
        raise AWSServiceError(
            f"[{table_name}] was not created after {GLUE_TABLE_PRESENCE_CHECK_RETRY_COUNT * GLUE_TABLE_PRESENCE_CHECK_INTERVAL}s"
        )  # noqa: E501

    def get_tables_for_dataset(self, dataset: DatasetMetadata) -> List[str]:
        tables = [
            item["Name"] for item in self._search_tables(dataset.glue_table_prefix())
        ]
        return tables

    def delete_tables(self, table_names: List[str]):
        try:
            self.glue_client.batch_delete_table(
                DatabaseName=GLUE_CATALOGUE_DB_NAME, TablesToDelete=table_names
            )
        except ClientError:
            raise AWSServiceError("Failed to delete tables")

    def _get_table(self, table_name: str) -> Dict:
        try:
            table = self.glue_client.get_table(
                DatabaseName=self.glue_catalogue_db_name, Name=table_name
            )
            return table
        except ClientError as error:
            if error.response["Error"]["Code"] == "EntityNotFoundException":
                raise TableDoesNotExistError(f"The table [{table_name}] does not exist")

    def _search_tables(self, search_term: str) -> Dict:
        try:
            paginator = self.glue_client.get_paginator("get_tables")
            page_iterator = paginator.paginate(
                DatabaseName=GLUE_CATALOGUE_DB_NAME,
            )
            tables = []
            for page in page_iterator:
                tables.extend(page["TableList"])

            return [table for table in tables if table["Name"].startswith(search_term)]
        except ClientError:
            raise AWSServiceError(f"Failed to search tables with term={search_term}")
