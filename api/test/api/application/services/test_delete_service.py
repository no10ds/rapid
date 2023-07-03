from unittest.mock import Mock

import pytest

from api.application.services.delete_service import DeleteService
from api.common.custom_exceptions import (
    CrawlerIsNotReadyError,
    CrawlerStartFailsError,
    UserError,
)
from api.common.config.auth import SensitivityLevel


class TestDeleteService:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.glue_adapter = Mock()
        self.delete_service = DeleteService(self.s3_adapter, self.glue_adapter)

    def test_delete_schema(self):
        self.delete_service.delete_schema("domain", "dataset", "PUBLIC", 2)

        self.s3_adapter.delete_schema.assert_called_once_with(
            "domain", "dataset", "PUBLIC", 2
        )

    def test_delete_file_when_crawler_is_ready(self):
        self.delete_service.delete_dataset_file(
            "domain",
            "dataset",
            1,
            "2022-01-01T00:00:00-file.csv",
        )
        self.s3_adapter.find_raw_file.assert_called_once_with(
            "domain", "dataset", 1, "2022-01-01T00:00:00-file.csv"
        )
        self.glue_adapter.check_crawler_is_ready.assert_called_once_with(
            "domain", "dataset"
        )
        self.s3_adapter.delete_dataset_files.assert_called_once_with(
            "domain", "dataset", 1, "2022-01-01T00:00:00-file.csv"
        )
        self.glue_adapter.start_crawler.assert_called_once_with("domain", "dataset")

    def test_delete_file_when_file_does_not_exist(self):
        self.s3_adapter.find_raw_file.side_effect = UserError("Some message")

        with pytest.raises(UserError):
            self.delete_service.delete_dataset_file(
                "domain", "dataset", 10, "2022-01-01T00:00:00-file.csv"
            )

        self.s3_adapter.find_raw_file.assert_called_once_with(
            "domain", "dataset", 10, "2022-01-01T00:00:00-file.csv"
        )

    def test_delete_file_when_crawler_is_not_ready_before_deletion(self):
        self.glue_adapter.check_crawler_is_ready.side_effect = CrawlerIsNotReadyError(
            "Not ready, try later"
        )

        with pytest.raises(CrawlerIsNotReadyError):
            self.delete_service.delete_dataset_file(
                "domain", "dataset", 2, "2022-01-01T00:00:00-file.csv"
            )

        self.s3_adapter.find_raw_file.assert_called_once_with(
            "domain", "dataset", 2, "2022-01-01T00:00:00-file.csv"
        )

        self.glue_adapter.check_crawler_is_ready.assert_called_once_with(
            "domain", "dataset"
        )
        assert (
            not self.s3_adapter.delete_dataset_files.called
        ), "The delete method should not be called due to crawler fail error"

    def test_delete_file_when_crawler_is_not_ready_after_deletion(self):
        self.glue_adapter.start_crawler.side_effect = CrawlerStartFailsError(
            "Not ready, try later"
        )

        with pytest.raises(CrawlerStartFailsError):
            self.delete_service.delete_dataset_file(
                "domain", "dataset", 11, "2022-01-01T00:00:00-file.csv"
            )

        self.s3_adapter.find_raw_file.assert_called_once_with(
            "domain", "dataset", 11, "2022-01-01T00:00:00-file.csv"
        )
        self.glue_adapter.check_crawler_is_ready.assert_called_once_with(
            "domain", "dataset"
        )
        self.s3_adapter.delete_dataset_files.assert_called_once_with(
            "domain", "dataset", 11, "2022-01-01T00:00:00-file.csv"
        )
        self.glue_adapter.start_crawler.assert_called_once_with("domain", "dataset")

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
            self.delete_service.delete_dataset_file("domain", "dataset", 1, filename)

    def test_delete_dataset(self):
        dataset_files = [
            {"key": "aaa"},
            {"key": "bbb"},
            {"key": "ccc"},
        ]
        tables = ["table_a", "table_b"]
        self.s3_adapter.get_dataset_sensitivity.return_value = (
            SensitivityLevel.from_string("PUBLIC")
        )
        self.s3_adapter.list_dataset_files.return_value = dataset_files
        self.glue_adapter.get_tables_for_dataset.return_value = tables

        self.delete_service.delete_dataset("domain", "dataset")

        self.s3_adapter.get_dataset_sensitivity.assert_called_once_with(
            "domain", "dataset"
        )
        self.s3_adapter.list_dataset_files.assert_called_once_with(
            "domain", "dataset", "PUBLIC"
        )
        self.s3_adapter.delete_dataset_files_using_key.assert_called_once_with(
            dataset_files, "domain/dataset"
        )
        self.glue_adapter.get_tables_for_dataset.assert_called_once_with(
            "domain", "dataset"
        )
        self.glue_adapter.delete_tables.assert_called_once_with(tables)
        self.glue_adapter.delete_crawler.assert_called_once_with("domain", "dataset")
