from unittest.mock import Mock

import pytest

from api.application.services.delete_service import DeleteService
from api.common.custom_exceptions import (
    AWSServiceError,
    UserError,
)
from api.domain.dataset_metadata import DatasetMetadata


class TestDeleteService:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.glue_adapter = Mock()
        self.schema_service = Mock()
        self.delete_service = DeleteService(
            self.s3_adapter, self.glue_adapter, self.schema_service
        )

    def test_delete_file(self):
        dataset_metadata = DatasetMetadata("layer", "domain", "dataset", 1)
        self.delete_service.delete_dataset_file(
            dataset_metadata,
            "2022-01-01T00:00:00-file.csv",
        )

        self.s3_adapter.find_raw_file.assert_called_once_with(
            dataset_metadata,
            "2022-01-01T00:00:00-file.csv",
        )
        self.s3_adapter.delete_dataset_files.assert_called_once_with(
            dataset_metadata,
            "2022-01-01T00:00:00-file.csv",
        )

    def test_delete_file_when_file_does_not_exist(self):
        self.s3_adapter.find_raw_file.side_effect = UserError("Some message")
        dataset_metadata = DatasetMetadata("layer", "domain", "dataset", 10)
        with pytest.raises(UserError):
            self.delete_service.delete_dataset_file(
                dataset_metadata, "2022-01-01T00:00:00-file.csv"
            )

        self.s3_adapter.find_raw_file.assert_called_once_with(
            dataset_metadata,
            "2022-01-01T00:00:00-file.csv",
        )

    @pytest.mark.parametrize(
        "filename",
        [
            "../filename.csv",
            ".",
            " ",
            "../../.",
            "../..",
            "..file",
            "hello/../domain",
            "2022-01-01T00:00:00-fiLe0192/../tf.csv",
            "2022-01-01T00:00:00-fiLe.csv/../tf.csv",
            "2022-01-01T00:00:00-fiLe.csv/..",
        ],
    )
    def test_delete_filename_error_for_bad_filenames(self, filename: str):
        with pytest.raises(UserError, match=f"Invalid file name \\[{filename}\\]"):
            self.delete_service.delete_dataset_file(
                DatasetMetadata("layer", "domain", "dataset", 1), filename
            )

    def test_delete_table(self):
        dataset = DatasetMetadata("layer", "domain", "dataset", 1)
        self.delete_service.delete_table(dataset)

        self.glue_adapter.delete_tables.assert_called_once_with(
            [dataset.glue_table_name()]
        )

    def test_delete_dataset(self):
        dataset_files = [
            {"key": "aaa"},
            {"key": "bbb"},
            {"key": "ccc"},
        ]
        tables = ["table_a", "table_b"]
        self.s3_adapter.list_dataset_files.return_value = dataset_files
        self.glue_adapter.get_tables_for_dataset.return_value = tables
        dataset_metadata = DatasetMetadata("layer", "domain", "dataset")
        self.delete_service.delete_dataset(dataset_metadata)

        self.s3_adapter.list_dataset_files.assert_called_once_with(dataset_metadata)
        self.s3_adapter.delete_dataset_files_using_key.assert_called_once_with(
            dataset_files, "layer/domain/dataset"
        )
        self.glue_adapter.get_tables_for_dataset.assert_called_once_with(
            dataset_metadata
        )
        self.glue_adapter.delete_tables.assert_called_once_with(tables)
        self.schema_service.delete_schemas.assert_called_once_with(dataset_metadata)

    def test_delete_schema_upload_success(self):
        dataset_metadata = DatasetMetadata("layer", "domain", "dataset", 1)
        self.delete_service.delete_schema_upload(dataset_metadata)

        self.glue_adapter.delete_tables.assert_called_once_with(
            [dataset_metadata.glue_table_name()]
        )
        self.schema_service.delete_schema.assert_called_once_with(dataset_metadata)

    def test_delete_schema_upload_table_delete_fails(self):
        dataset_metadata = DatasetMetadata("layer", "domain", "dataset", 1)
        self.glue_adapter.delete_tables.side_effect = AWSServiceError("Some message")

        self.delete_service.delete_schema_upload(dataset_metadata)

        self.schema_service.delete_schema.assert_called_once_with(dataset_metadata)

        self.glue_adapter.delete_tables.assert_called_once_with(
            [dataset_metadata.glue_table_name()]
        )

    def test_delete_schema_upload_schema_delete_fails(self):
        dataset_metadata = DatasetMetadata("layer", "domain", "dataset", 1)
        self.schema_service.delete_schema.side_effect = AWSServiceError("Some message")

        self.delete_service.delete_schema_upload(dataset_metadata)

        self.schema_service.delete_schema.assert_called_once_with(dataset_metadata)
        self.glue_adapter.delete_tables.assert_called_once_with(
            [dataset_metadata.glue_table_name()]
        )
