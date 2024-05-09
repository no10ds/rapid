import re

from api.adapter.glue_adapter import GlueAdapter
from api.adapter.s3_adapter import S3Adapter
from api.application.services.schema_service import SchemaService
from api.common.config.constants import FILENAME_WITH_TIMESTAMP_REGEX
from api.common.custom_exceptions import AWSServiceError, UserError
from api.common.logger import AppLogger
from api.domain.dataset_metadata import DatasetMetadata


class DeleteService:
    def __init__(
        self,
        s3_adapter=S3Adapter(),
        glue_adapter=GlueAdapter(),
        schema_service=SchemaService(),
    ):
        self.s3_adapter = s3_adapter
        self.glue_adapter = glue_adapter
        self.schema_service = schema_service

    def delete_schemas(self, metadata: type[DatasetMetadata]):
        self.schema_service.delete_schemas(metadata)

    def delete_schema_upload(self, metadata: type[DatasetMetadata]):
        """Deletes the resources associated with a schema upload or update"""
        try:
            self.delete_table(metadata)
        except AWSServiceError as error:
            AppLogger.error(
                f"Failed to delete table for schema upload: {error.message}"
            )

        try:
            self.schema_service.delete_schema(metadata)
        except AWSServiceError as error:
            AppLogger.error(f"Failed to delete uploaded schema: {error.message}")

    def delete_dataset_file(self, dataset: DatasetMetadata, filename: str):
        self._validate_filename(filename)
        self.s3_adapter.find_raw_file(dataset, filename)
        self.s3_adapter.delete_dataset_files(dataset, filename)

    def delete_table(self, dataset: DatasetMetadata):
        self.glue_adapter.delete_tables([dataset.glue_table_name()])

    def delete_dataset(self, dataset: DatasetMetadata):
        # Given a domain and a dataset, delete all rAPId contents for this domain & dataset
        # 1. Generate a list of file keys from S3 to delete, raw_data & data
        # 2. Remove keys
        # 3. Delete Glue Tables
        # 4. Delete Schemas
        dataset_files = self.s3_adapter.list_dataset_files(dataset)
        self.s3_adapter.delete_dataset_files_using_key(
            dataset_files, f"{dataset.layer}/{dataset.domain}/{dataset.dataset}"
        )
        tables = self.glue_adapter.get_tables_for_dataset(dataset)
        self.glue_adapter.delete_tables(tables)
        self.schema_service.delete_schemas(dataset)

    def _validate_filename(self, filename: str):
        if not re.match(FILENAME_WITH_TIMESTAMP_REGEX, filename):
            raise UserError(f"Invalid file name [{filename}]")
