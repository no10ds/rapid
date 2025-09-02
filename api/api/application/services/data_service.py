import uuid
from pathlib import Path
from threading import Thread
from typing import Tuple, Dict

import pandas as pd

from api.adapter.athena_adapter import AthenaAdapter
from api.adapter.glue_adapter import GlueAdapter
from api.adapter.s3_adapter import S3Adapter
from api.application.services.dataset_validation import build_validated_dataframe
from api.application.services.job_service import JobService
from api.application.services.partitioning_service import generate_partitioned_data
from api.application.services.schema_service import SchemaService
from api.common.config.constants import (
    DATASET_ROWS_QUERY_LIMIT,
    DATASET_SIZE_QUERY_LIMIT,
)
from api.common.custom_exceptions import (
    AWSServiceError,
    DatasetValidationError,
    QueryExecutionError,
    UnprocessableDatasetError,
    UserError,
)
from api.common.data_handlers import (
    construct_chunked_dataframe,
    delete_incoming_raw_file,
    get_dataframe_from_chunk_type,
)
from api.common.logger import AppLogger
from api.common.utilities import build_error_message_list
from api.domain.data_types import DateType
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.enriched_schema import (
    EnrichedSchema,
    EnrichedColumn
)
from api.domain.Jobs.QueryJob import QueryJob, QueryStep
from api.domain.Jobs.UploadJob import UploadJob, UploadStep
from api.domain.schema import Schema
from api.domain.sql_query import SQLQuery


class DataService:
    def __init__(
        self,
        s3_adapter=S3Adapter(),
        glue_adapter=GlueAdapter(),
        athena_adapter=AthenaAdapter(),
        job_service=JobService(),
        schema_service=SchemaService(),
    ):
        self.s3_adapter = s3_adapter
        self.glue_adapter = glue_adapter
        self.athena_adapter = athena_adapter
        self.job_service = job_service
        self.schema_service = schema_service

    def list_raw_files(self, dataset: DatasetMetadata) -> list[str]:
        raw_files = self.s3_adapter.list_raw_files(dataset)
        if len(raw_files) == 0:
            raise UserError(
                f"There are no uploaded files for the {dataset.string_representation()}"
            )
        else:
            return raw_files

    def generate_raw_file_identifier(self) -> str:
        return str(uuid.uuid4())

    def generate_permanent_filename(self, raw_file_identifier: str) -> str:
        return f"{raw_file_identifier}_{uuid.uuid4()}.parquet"

    def upload_dataset(
        self,
        subject_id: str,
        job_id: str,
        dataset: DatasetMetadata,
        file_path: Path,
    ) -> Tuple[str, int, str]:
        schema = self.schema_service.get_schema(dataset)
        raw_file_identifier = self.generate_raw_file_identifier()
        upload_job = self.job_service.create_upload_job(
            subject_id, job_id, file_path.name, raw_file_identifier, dataset
        )

        Thread(
            target=self.process_upload,
            args=(upload_job, schema, file_path, raw_file_identifier),
            name=upload_job.job_id,
        ).start()

        return f"{raw_file_identifier}.csv", dataset.version, upload_job.job_id

    def process_upload(
        self, job: UploadJob, schema: Schema, file_path: Path, raw_file_identifier: str
    ) -> None:
        try:
            self.job_service.update_step(job, UploadStep.VALIDATION)
            self.validate_incoming_data(schema, file_path, raw_file_identifier)
            self.job_service.update_step(job, UploadStep.RAW_DATA_UPLOAD)
            self.s3_adapter.upload_raw_data(
                schema.dataset_metadata, file_path, raw_file_identifier
            )
            self.job_service.update_step(job, UploadStep.DATA_UPLOAD)
            self.process_chunks(schema, file_path, raw_file_identifier)
            self.job_service.update_step(job, UploadStep.LOAD_PARTITIONS)
            self.load_partitions(schema)
            self.job_service.update_step(job, UploadStep.CLEAN_UP)
            delete_incoming_raw_file(schema, file_path, raw_file_identifier)
            self.job_service.update_step(job, UploadStep.NONE)
            self.job_service.succeed(job)
        except Exception as error:
            AppLogger.error(
                f"Processing upload failed for layer [{schema.get_layer()}], domain [{schema.get_domain()}], dataset [{schema.get_dataset()}], and version [{schema.get_version()}]: {error}"
            )
            delete_incoming_raw_file(schema, file_path, raw_file_identifier)
            self.job_service.fail(job, build_error_message_list(error))
            raise error

    def validate_incoming_data(
        self, schema: Schema, file_path: Path, raw_file_identifier: str
    ) -> None:
        AppLogger.info(
            f"Validating dataset for {schema.get_layer()}/{schema.get_domain()}/{schema.get_dataset()}"
        )
        dataset_errors = set()
        for chunk in construct_chunked_dataframe(file_path):
            dataframe = get_dataframe_from_chunk_type(chunk)
            try:
                build_validated_dataframe(schema, dataframe)
            except DatasetValidationError as error:
                dataset_errors.update(error.message)
        if dataset_errors:
            delete_incoming_raw_file(schema, file_path, raw_file_identifier)
            raise DatasetValidationError(list(dataset_errors))

    def process_chunks(
        self, schema: Schema, file_path: Path, raw_file_identifier: str
    ) -> None:
        AppLogger.info(
            f"Processing chunks for {schema.get_layer()}/{schema.get_domain()}/{schema.get_dataset()}/{schema.get_version()}"
        )
        for chunk in construct_chunked_dataframe(file_path):
            dataframe = get_dataframe_from_chunk_type(chunk)
            self.process_chunk(schema, raw_file_identifier, dataframe)

        if schema.has_overwrite_behaviour():
            self.remove_existing_data(schema, raw_file_identifier)

        AppLogger.info(
            f"Processing chunks for {schema.get_layer()}/{schema.get_domain()}/{schema.get_dataset()}/{schema.get_version()} completed"
        )

    def process_chunk(
        self, schema: Schema, raw_file_identifier: str, chunk: pd.DataFrame
    ) -> None:
        validated_dataframe = build_validated_dataframe(schema, chunk)
        permanent_filename = self.generate_permanent_filename(raw_file_identifier)
        self.upload_data(schema, validated_dataframe, permanent_filename)

    def remove_existing_data(self, schema: Schema, raw_file_identifier: str) -> None:
        AppLogger.info(
            f"Overwriting existing data for layer [{schema.get_layer()}], domain [{schema.get_domain()}] and dataset [{schema.get_dataset()}]"
        )
        try:
            self.s3_adapter.delete_previous_dataset_files(
                schema.dataset_metadata,
                raw_file_identifier,
            )
        except IndexError:
            AppLogger.warning(
                f"No data to override for domain [{schema.get_domain()}] and dataset [{schema.get_dataset()}]"
            )
        except AWSServiceError as error:
            AppLogger.error(
                f"Overriding existing data failed for layer [{schema.get_layer()}], domain [{schema.get_domain()}] and dataset [{schema.get_dataset()}]. Raw file identifier: {raw_file_identifier}. {error}"
            )
            raise AWSServiceError(
                f"Overriding existing data failed for layer [{schema.get_layer()}], domain [{schema.get_domain()}] and dataset [{schema.get_dataset()}]. Raw file identifier: {raw_file_identifier}"
            )

    def get_last_updated_time(self, metadata: DatasetMetadata) -> str:
        last_updated = self.s3_adapter.get_last_updated_time(
            metadata.dataset_location()
        )
        return last_updated or "Never updated"

    def get_dataset_info(self, dataset: DatasetMetadata) -> EnrichedSchema:
        schema = self.schema_service.get_schema(dataset)
        statistics_dataframe = self.athena_adapter.query(
            dataset, self._build_query(schema)
        )
        last_updated = self.get_last_updated_time(dataset)
        return self._enrich_schema(
            schema, statistics_dataframe, last_updated
        )

    def upload_data(
        self,
        schema: Schema,
        validated_dataframe: pd.DataFrame,
        filename: str,
    ):
        partitions = generate_partitioned_data(schema, validated_dataframe)
        self.s3_adapter.upload_partitioned_data(schema, filename, partitions)

    def load_partitions(self, schema: Schema):
        partition_columns = schema.get_partition_columns()
        if partition_columns:
            query_id = self.athena_adapter.query_sql_async(
                f"MSCK REPAIR TABLE `{schema.dataset_metadata.glue_table_name()}`;"
            )
            self.athena_adapter.wait_for_query_to_complete(query_id)

    def is_query_too_large(self, dataset: DatasetMetadata, query: SQLQuery):
        if query.limit:
            if int(query.limit) <= DATASET_ROWS_QUERY_LIMIT:
                return False

        size_of_datasets = self.s3_adapter.get_folder_size(dataset.s3_file_location())
        return size_of_datasets > DATASET_SIZE_QUERY_LIMIT

    def query_data(
        self,
        dataset: DatasetMetadata,
        query: SQLQuery,
    ) -> pd.DataFrame:
        if not self.is_query_too_large(dataset, query):
            return self.athena_adapter.query(dataset, query)
        else:
            raise UnprocessableDatasetError("Dataset too large for this endpoint")

    def query_large_data(
        self,
        subject_id: str,
        dataset: DatasetMetadata,
        query: SQLQuery,
    ) -> str:
        query_job = self.job_service.create_query_job(subject_id, dataset)
        query_execution_id = self.athena_adapter.query_async(dataset, query)
        Thread(
            target=self.generate_results_download_url_async,
            args=(
                query_job,
                query_execution_id,
            ),
        ).start()
        return query_job.job_id

    def generate_results_download_url_async(
        self, query_job: QueryJob, query_execution_id: str
    ) -> None:
        try:
            self.job_service.update_step(query_job, QueryStep.RUNNING)
            self.athena_adapter.wait_for_query_to_complete(query_execution_id)
            self.job_service.update_step(query_job, QueryStep.GENERATING_RESULTS)
            url = self.s3_adapter.generate_query_result_download_url(query_execution_id)
            self.job_service.succeed_query(query_job, url)
        except QueryExecutionError as error:
            self.job_service.fail(query_job, build_error_message_list(error))
        except (AWSServiceError, Exception) as error:
            AppLogger.error(f"Large query failed: {error}")
            self.job_service.fail(query_job, build_error_message_list(error))
            raise error

    def _build_query(self, schema: Schema) -> SQLQuery:
        date_column_names = schema.get_column_names_by_type(DateType)
        date_range_queries = [
            *[
                f"cast(max({column_name}) as date) as max_{column_name}"
                for column_name in date_column_names
            ],
            *[
                f"cast(min({column_name}) as date) as min_{column_name}"
                for column_name in date_column_names
            ],
        ]
        columns_to_query = [
            "count(*) as data_size",
            *date_range_queries,
        ]
        return SQLQuery(select_columns=columns_to_query)

    def _enrich_schema(
        self, schema: Schema, statistics_dataframe: pd.DataFrame, last_updated: str
    ) -> EnrichedSchema:
        dataset_size = statistics_dataframe.at[0, "data_size"]
        return EnrichedSchema(
            dataset_metadata=schema.dataset_metadata,
            sensitivity=schema.get_sensitivity(),
            owners=schema.get_owners(),
            columns=self._enrich_columns(schema, statistics_dataframe),
            number_of_rows=dataset_size,
            number_of_columns=len(schema.columns.values()),
            last_updated=last_updated,
        )

    def _enrich_columns(
        self, schema: Schema, statistics_dataframe: pd.DataFrame
    ) -> Dict[str, EnrichedColumn]:
        strftime_format = "%Y-%m-%d"
        enriched_columns = {}
        date_column_names = schema.get_column_names_by_type(DateType)
        for name, column in schema.columns.items():
            statistics = None
            if name in date_column_names:
                statistics = {
                    "max": statistics_dataframe.at[0, f"max_{name}"].strftime(
                        strftime_format
                    ),
                    "min": statistics_dataframe.at[0, f"min_{name}"].strftime(
                        strftime_format
                    ),
                }

            enriched_columns[name] = EnrichedColumn(
                dtype=column.dtype,
                nullable=column.nullable,
                partition_index=column.partition_index,
                format=column.format,
                unique=getattr(column, 'unique', False),
                statistics=statistics
            )

        return enriched_columns
