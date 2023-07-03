import re
from pathlib import Path
from typing import List, Any
from unittest.mock import Mock, patch, MagicMock, call

import pandas as pd
import pytest
from botocore.exceptions import ClientError

from api.application.services.data_service import (
    DataService,
)
from api.common.config.auth import SensitivityLevel
from api.common.config.constants import DATASET_QUERY_LIMIT
from api.common.custom_exceptions import (
    SchemaNotFoundError,
    CrawlerIsNotReadyError,
    SchemaValidationError,
    ConflictError,
    UserError,
    AWSServiceError,
    UnprocessableDatasetError,
    DatasetValidationError,
    CrawlerUpdateError,
    QueryExecutionError,
)
from api.domain.Jobs.QueryJob import QueryStep
from api.domain.Jobs.UploadJob import UploadStep
from api.domain.enriched_schema import (
    EnrichedSchema,
    EnrichedSchemaMetadata,
    EnrichedColumn,
)
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata
from api.domain.sql_query import SQLQuery
from api.domain.storage_metadata import StorageMetaData


class TestUploadSchema:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.glue_adapter = Mock()
        self.query_adapter = Mock()
        self.protected_domain_service = Mock()
        self.cognito_adapter = Mock()
        self.data_service = DataService(
            self.s3_adapter,
            self.glue_adapter,
            self.query_adapter,
            self.protected_domain_service,
            self.cognito_adapter,
        )
        self.valid_schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=False,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="object",
                    allow_null=True,
                ),
            ],
        )

    def test_upload_schema(self):
        self.s3_adapter.find_schema.return_value = None
        self.s3_adapter.save_schema.return_value = "some-other.json"

        result = self.data_service.upload_schema(self.valid_schema)

        self.s3_adapter.save_schema.assert_called_once_with(self.valid_schema)
        self.glue_adapter.create_crawler.assert_called_once_with(
            "some", "other", {"sensitivity": "PUBLIC", "no_of_versions": "1"}
        )
        assert result == "some-other.json"

    def test_upload_schema_uppercase_domain(self):
        self.s3_adapter.find_schema.return_value = None
        self.s3_adapter.save_schema.return_value = "some-other.json"

        schema = self.valid_schema.copy()
        schema.metadata.domain = schema.metadata.domain.upper()
        result = self.data_service.upload_schema(schema)

        self.s3_adapter.save_schema.assert_called_once_with(schema)
        self.glue_adapter.create_crawler.assert_called_once_with(
            "some", "other", {"sensitivity": "PUBLIC", "no_of_versions": "1"}
        )
        assert result == "some-other.json"

    def test_aborts_uploading_if_schema_upload_fails(self):
        self.s3_adapter.find_schema.return_value = None
        self.s3_adapter.save_schema.side_effect = ClientError(
            error_response={"Error": {"Code": "Failed"}}, operation_name="PutObject"
        )

        with pytest.raises(ClientError):
            self.data_service.upload_schema(self.valid_schema)

        self.cognito_adapter.create_user_groups.assert_not_called()
        self.glue_adapter.create_crawler.assert_not_called()

    def test_check_for_protected_domain_success(self):
        schema = Schema(
            metadata=SchemaMetadata(
                domain="domain",
                dataset="dataset",
                sensitivity="PROTECTED",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=True,
                ),
            ],
        )
        self.protected_domain_service.list_protected_domains = Mock(
            return_value=["domain", "other"]
        )

        result = self.data_service.check_for_protected_domain(schema)

        self.protected_domain_service.list_protected_domains.assert_called_once()
        assert result == "domain"

    def test_check_for_protected_domain_fails(self):
        schema = Schema(
            metadata=SchemaMetadata(
                domain="domain1",
                dataset="dataset2",
                sensitivity="PROTECTED",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=True,
                ),
            ],
        )
        self.protected_domain_service.list_protected_domains = Mock(
            return_value=["other"]
        )

        with pytest.raises(
            UserError, match="The protected domain 'domain1' does not exist."
        ):
            self.data_service.check_for_protected_domain(schema)

    def test_upload_schema_throws_error_when_schema_already_exists(self):
        self.s3_adapter.find_schema.return_value = self.valid_schema

        with pytest.raises(ConflictError, match="Schema already exists"):
            self.data_service.upload_schema(self.valid_schema)

    def test_upload_schema_throws_error_when_schema_invalid(self):
        self.s3_adapter.find_schema.return_value = None

        invalid_partition_index = -1
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=invalid_partition_index,
                    data_type="Int64",
                    allow_null=True,
                )
            ],
        )

        with pytest.raises(SchemaValidationError):
            self.data_service.upload_schema(invalid_schema)


class TestUpdateSchema:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.glue_adapter = Mock()
        self.query_adapter = Mock()
        self.protected_domain_service = Mock()
        self.cognito_adapter = Mock()
        self.delete_service = Mock()
        self.data_service = DataService(
            self.s3_adapter,
            self.glue_adapter,
            self.query_adapter,
            self.protected_domain_service,
            self.cognito_adapter,
            self.delete_service,
        )
        self.valid_schema = Schema(
            metadata=SchemaMetadata(
                domain="testdomain",
                dataset="testdataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
                key_value_tags={"key1": "val1", "testkey2": "testval2"},
                key_only_tags=["ktag1", "ktag2"],
                update_behaviour="APPEND",
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=False,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="object",
                    allow_null=True,
                ),
            ],
        )
        self.valid_updated_schema = Schema(
            metadata=SchemaMetadata(
                domain="testdomain",
                dataset="testdataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
                key_value_tags={"key1": "val1", "testkey2": "testval2"},
                key_only_tags=["ktag1", "ktag2"],
                update_behaviour="APPEND",
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Float64",
                    allow_null=False,
                ),
                Column(
                    name="colname_new",
                    partition_index=None,
                    data_type="object",
                    allow_null=True,
                ),
            ],
        )

    def test_update_schema_throws_error_when_schema_does_not_exist(self):
        self.s3_adapter.find_schema.return_value = None

        with pytest.raises(
            SchemaNotFoundError, match="Previous version of schema not found"
        ):
            self.data_service.update_schema(self.valid_schema)

    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_update_schema_throws_error_when_schema_invalid(
        self, mock_handle_version_retrieval
    ):
        invalid_partition_index = -1
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=invalid_partition_index,
                    data_type="Int64",
                    allow_null=True,
                )
            ],
        )
        self.s3_adapter.find_schema.return_value = self.valid_schema
        mock_handle_version_retrieval.return_value = 1

        with pytest.raises(SchemaValidationError):
            self.data_service.update_schema(invalid_schema)

    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_update_schema_for_protected_domain_failure(
        self, mock_handle_version_retrieval
    ):
        original_schema = self.valid_schema.copy(deep=True)
        original_schema.metadata.sensitivity = SensitivityLevel.PROTECTED.value
        new_schema = self.valid_updated_schema.copy(deep=True)
        new_schema.metadata.sensitivity = SensitivityLevel.PROTECTED.value

        self.glue_adapter.check_crawler_is_ready.return_value = None
        self.s3_adapter.find_schema.return_value = original_schema
        self.s3_adapter.save_schema.return_value = "some-other.json"
        mock_handle_version_retrieval.return_value = 1
        self.protected_domain_service.list_protected_domains.return_value = ["other"]

        with pytest.raises(
            UserError,
            match=f"The protected domain '{new_schema.get_domain()}' does not exist.",
        ):
            self.data_service.update_schema(new_schema)

    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_update_schema_when_crawler_raises_error(
        self, mock_handle_version_retrieval
    ):
        new_schema = self.valid_updated_schema
        expected_schema = self.valid_updated_schema.copy(deep=True)
        expected_schema.metadata.version = 2

        self.glue_adapter.check_crawler_is_ready.return_value = None
        self.s3_adapter.find_schema.return_value = self.valid_schema
        self.s3_adapter.save_schema.return_value = "some-other.json"
        mock_handle_version_retrieval.return_value = 1
        self.glue_adapter.set_crawler_version_tag.side_effect = CrawlerUpdateError(
            "error occurred"
        )

        with pytest.raises(CrawlerUpdateError, match="error occurred"):
            self.data_service.update_schema(new_schema)

        self.glue_adapter.check_crawler_is_ready.assert_called_once_with(
            new_schema.get_domain(), new_schema.get_dataset()
        )
        self.s3_adapter.save_schema.assert_called_once_with(expected_schema)
        self.delete_service.delete_schema.assert_called_once_with(
            expected_schema.get_domain(),
            expected_schema.get_dataset(),
            expected_schema.get_sensitivity(),
            expected_schema.get_version(),
        )

    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_update_schema_success(self, mock_handle_version_retrieval):
        original_schema = self.valid_schema
        new_schema = self.valid_updated_schema
        expected_schema = self.valid_updated_schema.copy(deep=True)
        expected_schema.metadata.version = 2

        self.glue_adapter.check_crawler_is_ready.return_value = None
        self.s3_adapter.find_schema.return_value = original_schema
        self.s3_adapter.save_schema.return_value = "some-other.json"
        mock_handle_version_retrieval.return_value = 1

        result = self.data_service.update_schema(new_schema)

        self.glue_adapter.check_crawler_is_ready.assert_called_once_with(
            new_schema.get_domain(), new_schema.get_dataset()
        )
        self.s3_adapter.save_schema.assert_called_once_with(expected_schema)
        self.glue_adapter.set_crawler_version_tag.assert_called_once_with(
            expected_schema.get_domain(),
            expected_schema.get_dataset(),
            expected_schema.metadata.version,
        )
        assert result == "some-other.json"

    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_update_schema_success_uppercase_domain(
        self, mock_handle_version_retrieval
    ):
        original_schema = self.valid_schema
        new_schema = self.valid_updated_schema.copy(deep=True)
        new_schema.metadata.domain = new_schema.metadata.domain.upper()
        expected_schema = self.valid_updated_schema.copy(deep=True)
        expected_schema.metadata.version = 2

        self.glue_adapter.check_crawler_is_ready.return_value = None
        self.s3_adapter.find_schema.return_value = original_schema
        self.s3_adapter.save_schema.return_value = "some-other.json"
        mock_handle_version_retrieval.return_value = 1

        result = self.data_service.update_schema(new_schema)
        self.glue_adapter.check_crawler_is_ready.assert_called_once_with(
            new_schema.get_domain(), new_schema.get_dataset()
        )
        self.s3_adapter.save_schema.assert_called_once_with(expected_schema)
        self.glue_adapter.set_crawler_version_tag.assert_called_once_with(
            expected_schema.get_domain(),
            expected_schema.get_dataset(),
            expected_schema.metadata.version,
        )
        assert result == "some-other.json"

    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_update_schema_maintains_original_metadata(
        self, mock_handle_version_retrieval
    ):
        original_schema = self.valid_schema
        new_schema = self.valid_updated_schema.copy(deep=True)
        new_schema.metadata.sensitivity = SensitivityLevel.PRIVATE.value
        new_schema.metadata.key_value_tags = {"new_key": "new_val"}
        new_schema.metadata.key_only_tags = ["new_k_tag"]
        new_schema.metadata.update_behaviour = "OVERWRITE"
        expected_schema = self.valid_updated_schema.copy(deep=True)
        expected_schema.metadata.version = 2

        self.glue_adapter.check_crawler_is_ready.return_value = None
        self.s3_adapter.find_schema.return_value = original_schema
        self.s3_adapter.save_schema.return_value = "some-other.json"
        mock_handle_version_retrieval.return_value = 1

        result = self.data_service.update_schema(new_schema)

        self.glue_adapter.check_crawler_is_ready.assert_called_once_with(
            new_schema.get_domain(), new_schema.get_dataset()
        )
        self.s3_adapter.save_schema.assert_called_once_with(expected_schema)
        self.glue_adapter.set_crawler_version_tag.assert_called_once_with(
            expected_schema.get_domain(),
            expected_schema.get_dataset(),
            expected_schema.metadata.version,
        )
        assert result == "some-other.json"

    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_update_schema_for_protected_domain_success(
        self, mock_handle_version_retrieval
    ):
        original_schema = self.valid_schema.copy(deep=True)
        original_schema.metadata.sensitivity = SensitivityLevel.PROTECTED.value
        new_schema = self.valid_updated_schema.copy(deep=True)
        new_schema.metadata.sensitivity = SensitivityLevel.PROTECTED.value
        expected_schema = self.valid_updated_schema.copy(deep=True)
        expected_schema.metadata.version = 2
        expected_schema.metadata.sensitivity = SensitivityLevel.PROTECTED.value

        self.glue_adapter.check_crawler_is_ready.return_value = None
        self.s3_adapter.find_schema.return_value = original_schema
        self.s3_adapter.save_schema.return_value = "some-other.json"
        mock_handle_version_retrieval.return_value = 1
        self.protected_domain_service.list_protected_domains = Mock(
            return_value=[original_schema.get_domain(), "other"]
        )

        result = self.data_service.update_schema(new_schema)

        self.glue_adapter.check_crawler_is_ready.assert_called_once_with(
            new_schema.get_domain(), new_schema.get_dataset()
        )
        self.s3_adapter.save_schema.assert_called_once_with(expected_schema)
        self.glue_adapter.set_crawler_version_tag.assert_called_once_with(
            expected_schema.get_domain(),
            expected_schema.get_dataset(),
            expected_schema.metadata.version,
        )
        assert result == "some-other.json"

    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_aborts_updating_if_schema_update_fails(
        self, mock_handle_version_retrieval
    ):
        self.s3_adapter.find_schema.return_value = self.valid_schema
        self.s3_adapter.save_schema.side_effect = ClientError(
            error_response={"Error": {"Code": "Failed"}}, operation_name="PutObject"
        )
        mock_handle_version_retrieval.return_value = 1

        with pytest.raises(ClientError):
            self.data_service.update_schema(self.valid_schema)

        self.cognito_adapter.create_user_groups.assert_not_called()
        self.glue_adapter.create_crawler.assert_not_called()


class TestUploadDataset:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.glue_adapter = Mock()
        self.query_adapter = Mock()
        self.protected_domain_service = Mock()
        self.job_service = Mock()
        self.data_service = DataService(
            self.s3_adapter,
            self.glue_adapter,
            self.query_adapter,
            self.protected_domain_service,
            None,
            None,
            self.job_service,
        )
        self.valid_schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="other",
                version="2",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=True,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="object",
                    allow_null=False,
                ),
            ],
        )

    def generator(self, data_list: List[Any]):
        for element in data_list:
            yield element

    def chunked_dataframe_values(
        self, mock_construct_chunked_dataframe, dataframes: List[pd.DataFrame]
    ):
        mock_test_file_reader = MagicMock()
        mock_construct_chunked_dataframe.return_value = mock_test_file_reader
        mock_test_file_reader.__iter__.return_value = dataframes
        return mock_test_file_reader

    # Schema retrieval -------------------------------
    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_raises_error_when_schema_does_not_exist(self, mock_get_version):
        self.s3_adapter.find_schema.return_value = None
        mock_get_version.return_value = 1

        with pytest.raises(SchemaNotFoundError):
            self.data_service.upload_dataset(
                "subject-123", "234", "some", "other", None, Path("data.csv")
            )

        self.s3_adapter.find_schema.assert_called_once_with("some", "other", 1)

    # Upload Dataset  -------------------------------------

    @patch("api.application.services.data_service.UploadJob")
    @patch("api.application.services.data_service.Thread")
    @patch("api.application.services.data_service.handle_version_retrieval")
    @patch("api.application.services.data_service.construct_chunked_dataframe")
    @patch.object(DataService, "process_upload")
    def test_upload_dataset_triggers_process_upload_and_returns_expected_data(
        self,
        mock_process_upload,
        _mock_construct_chunked_dataframe,
        mock_get_version,
        mock_thread,
        mock_upload_job,
    ):
        # GIVEN
        schema = self.valid_schema

        self.s3_adapter.find_schema.return_value = schema

        mock_get_version.return_value = 1

        self.data_service.generate_raw_file_identifier = Mock(
            return_value="123-456-789"
        )

        mock_job = Mock()
        self.job_service.create_upload_job.return_value = mock_job

        mock_job.job_id = "abc-123"
        mock_upload_job.return_value = mock_job

        # WHEN
        uploaded_raw_file = self.data_service.upload_dataset(
            "subject-123", "abc-123", "some", "other", None, Path("data.csv")
        )

        # THEN
        self.job_service.create_upload_job.assert_called_once_with(
            "subject-123", "abc-123", "data.csv", "123-456-789", "some", "other", 1
        )
        self.data_service.generate_raw_file_identifier.assert_called_once()
        mock_thread.assert_called_once_with(
            target=mock_process_upload,
            args=(mock_job, schema, Path("data.csv"), "123-456-789"),
            name="abc-123",
        )
        assert uploaded_raw_file == ("123-456-789.csv", 1, "abc-123")

    # Generate Permanent Filename ----------------------------
    @patch("api.application.services.data_service.uuid")
    def test_generates_permanent_filename(self, mock_uuid):
        # Given
        raw_file_identifier = "123-456-789"

        mock_uuid.uuid4.return_value = "111-222-333"

        # When
        result = self.data_service.generate_permanent_filename(raw_file_identifier)

        # Then
        assert result == "123-456-789_111-222-333.parquet"

    # Process Upload
    @patch.object(DataService, "wait_until_crawler_is_ready")
    @patch.object(DataService, "validate_incoming_data")
    @patch.object(DataService, "process_chunks")
    @patch("api.application.services.data_service.delete_incoming_raw_file")
    def test_process_upload_calls_relevant_methods(
        self,
        mock_delete_incoming_raw_file,
        mock_process_chunks,
        mock_validate_incoming_data,
        mock_wait_until_crawler_is_ready,
    ):
        # GIVEN
        schema = self.valid_schema
        upload_job = Mock()

        expected_update_step_calls = [
            call(upload_job, UploadStep.INITIALISATION),
            call(upload_job, UploadStep.VALIDATION),
            call(upload_job, UploadStep.RAW_DATA_UPLOAD),
            call(upload_job, UploadStep.DATA_UPLOAD),
            call(upload_job, UploadStep.CLEAN_UP),
            call(upload_job, UploadStep.NONE),
        ]

        # WHEN
        self.data_service.process_upload(
            upload_job, schema, Path("data.csv"), "123-456-789"
        )

        # THEN
        mock_wait_until_crawler_is_ready.assert_called_once_with(schema)
        mock_validate_incoming_data.assert_called_once_with(
            schema, Path("data.csv"), "123-456-789"
        )
        self.s3_adapter.upload_raw_data.assert_called_once_with(
            schema, Path("data.csv"), "123-456-789"
        )
        mock_process_chunks.assert_called_once_with(
            schema, Path("data.csv"), "123-456-789"
        )
        mock_delete_incoming_raw_file.assert_called_once_with(
            schema, Path("data.csv"), "123-456-789"
        )
        self.job_service.update_step.assert_has_calls(expected_update_step_calls)
        self.job_service.succeed.assert_called_once_with(upload_job)

    @patch("api.application.services.data_service.sleep")
    def test_wait_until_crawler_is_ready_returns_none_when_crawler_is_ready_after_waiting(
        self, mock_sleep
    ):
        # GIVEN
        schema = self.valid_schema

        self.glue_adapter.check_crawler_is_ready.side_effect = [
            CrawlerIsNotReadyError("some message"),
            None,
        ]

        # WHEN/THEN
        try:
            self.data_service.wait_until_crawler_is_ready(schema)
        except Exception as error:
            pytest.fail("Unexpected failure occurred", error)

        mock_sleep.assert_called_once_with(30)

    @patch("api.application.services.data_service.sleep")
    def test_retries_getting_crawler_state_until_retries_exhausted(self, mock_sleep):
        # GIVEN
        schema = self.valid_schema

        self.glue_adapter.check_crawler_is_ready.side_effect = [
            CrawlerIsNotReadyError("some message")
        ] * 21

        # WHEN/THEN
        with pytest.raises(CrawlerIsNotReadyError, match="some message"):
            self.data_service.wait_until_crawler_is_ready(schema)

        assert mock_sleep.call_count == 19

    @patch("api.application.services.data_service.construct_chunked_dataframe")
    def test_starts_crawler_and_updates_catalog_table_config(
        self, mock_construct_chunked_dataframe
    ):
        # Given
        schema = self.valid_schema

        mock_construct_chunked_dataframe.return_value = []

        # When
        self.data_service.process_chunks(schema, Path("data.csv"), "123-456-789")

        # Then
        self.glue_adapter.start_crawler.assert_called_once_with("some", "other")
        self.glue_adapter.update_catalog_table_config.assert_called_once_with(schema)

    @patch("api.application.services.data_service.delete_incoming_raw_file")
    @patch.object(DataService, "validate_incoming_data")
    @patch.object(DataService, "wait_until_crawler_is_ready")
    def test_deletes_incoming_file_from_disk_and_fails_job_if_any_error_during_processing(
        self,
        _mock_wait_until_crawler_is_ready,
        mock_validate_incoming_data,
        mock_delete_incoming_raw_file,
    ):
        # Given
        schema = self.valid_schema
        upload_job = Mock()

        mock_validate_incoming_data.side_effect = DatasetValidationError("some message")

        # When/Then
        with pytest.raises(DatasetValidationError, match="some message"):
            self.data_service.process_upload(
                upload_job, schema, Path("data.csv"), "123-456-789"
            )

        mock_delete_incoming_raw_file.assert_called_once_with(
            schema, Path("data.csv"), "123-456-789"
        )
        self.job_service.fail.assert_called_once_with(upload_job, ["some message"])

    # Validate dataset ---------------------------------------
    @patch("api.application.services.data_service.build_validated_dataframe")
    @patch("api.application.services.data_service.construct_chunked_dataframe")
    def test_process_upload_validates_each_chunk_of_the_dataset(
        self,
        mock_construct_chunked_dataframe,
        mock_build_validated_dataframe,
    ):
        # Given
        schema = self.valid_schema
        self.s3_adapter.find_schema.return_value = schema

        chunk1 = pd.DataFrame({})
        chunk2 = pd.DataFrame({})
        chunk3 = pd.DataFrame({})

        mock_construct_chunked_dataframe.return_value = [
            chunk1,
            chunk2,
            chunk3,
        ]

        expected_calls = [
            call(schema, chunk1),
            call(schema, chunk2),
            call(schema, chunk3),
        ]

        # When
        self.data_service.validate_incoming_data(
            schema, Path("data.csv"), "123-456-789"
        )

        mock_build_validated_dataframe.assert_has_calls(expected_calls)

    # Dataset chunk validation -------------------------------
    @patch("api.application.services.data_service.construct_chunked_dataframe")
    def test_validates_dataset_in_chunks_with_invalid_column_headers(
        self, mock_construct_chunked_dataframe
    ):
        schema = self.valid_schema

        self.s3_adapter.find_schema.return_value = schema

        self.chunked_dataframe_values(
            mock_construct_chunked_dataframe,
            [
                pd.DataFrame(
                    {"colname1": [1234, 4567], "colnamewrong": ["Carlos", "Ada"]}
                )
            ],
        )

        with pytest.raises(UnprocessableDatasetError):
            self.data_service.validate_incoming_data(
                schema, Path("data.csv"), "123-456-789"
            )

    @patch("api.application.services.data_service.construct_chunked_dataframe")
    def test_upload_dataset_in_chunks_with_invalid_data(
        self, mock_construct_chunked_dataframe
    ):
        schema = self.valid_schema

        self.s3_adapter.find_schema.return_value = schema

        self.chunked_dataframe_values(
            mock_construct_chunked_dataframe,
            [
                pd.DataFrame({"colname1": [1234, 4567], "colname2": ["Carlos", "Ada"]}),
                pd.DataFrame(
                    {"colname1": [4332, "s2134"], "colname2": ["Carlos", "Ada"]}
                ),
                pd.DataFrame(
                    {"colname1": [3543, 456743], "colname2": ["Carlos", "Ada"]}
                ),
            ],
        )

        try:
            self.data_service.upload_dataset(
                "subject-123", "abc-123", "some", "other", 2, Path("data.csv")
            )
        except DatasetValidationError as error:
            assert {
                "Failed to convert column [colname1] to type [Int64]",
                "Column [colname1] has an incorrect data type. Expected Int64, received "
                "object",
            }.issubset(error.message)

    @patch("api.application.services.data_service.construct_chunked_dataframe")
    def test_upload_dataset_in_chunks_with_invalid_data_in_multiple_chunks(
        self, mock_construct_chunked_dataframe
    ):
        schema = self.valid_schema

        self.s3_adapter.find_schema.return_value = schema

        self.chunked_dataframe_values(
            mock_construct_chunked_dataframe,
            [
                pd.DataFrame({"colname1": [1234, 4567], "colname2": ["Carlos", "Ada"]}),
                pd.DataFrame(
                    {"colname1": [4332, "s2134"], "colname2": ["Carlos", "Ada"]}
                ),
                pd.DataFrame(
                    {"colname1": [4332, "s2134"], "colname2": ["Carlos", "Ada"]}
                ),
                pd.DataFrame(
                    {"colname1": [3543, 456743], "colname2": ["Carlos", "Ada"]}
                ),
            ],
        )

        try:
            self.data_service.upload_dataset(
                "subject-123", "abc-123", "some", "other", 2, Path("data.csv")
            )
        except DatasetValidationError as error:
            assert {
                "Column [colname1] has an incorrect data type. Expected Int64, received "
                "object",
                "Failed to convert column [colname1] to type [Int64]",
            }.issubset(error.message)

    # Crawler state and trigger errors ----------------------
    def test_upload_dataset_fails_when_unable_to_get_crawler_state(self):
        schema = self.valid_schema

        self.glue_adapter.check_crawler_is_ready.side_effect = AWSServiceError(
            "Some message"
        )

        with pytest.raises(AWSServiceError, match="Some message"):
            self.data_service.wait_until_crawler_is_ready(schema)

    # Process Chunks -----------------------------------------
    @patch("api.application.services.data_service.construct_chunked_dataframe")
    def test_processes_each_dataset_chunk_with_append_behaviour(
        self, mock_construct_chunked_dataframe
    ):
        # Given
        schema = self.valid_schema

        def dataset_chunk():
            return pd.DataFrame(
                {
                    "col1": ["one", "two", "three"],
                    "col2": [1, 2, 3],
                }
            )

        chunk1 = dataset_chunk()
        chunk2 = dataset_chunk()

        mock_construct_chunked_dataframe.return_value = [
            chunk1,
            chunk2,
        ]

        self.data_service.process_chunk = Mock()

        # When
        self.data_service.process_chunks(schema, Path("data.csv"), "123-456-789")

        # Then
        expected_calls = [
            call(schema, "123-456-789", chunk1),
            call(schema, "123-456-789", chunk2),
        ]
        self.data_service.process_chunk.assert_has_calls(expected_calls)
        self.s3_adapter.list_raw_files.assert_not_called()
        self.s3_adapter.delete_dataset_files.assert_not_called()

    @patch("api.application.services.data_service.construct_chunked_dataframe")
    def test_processes_each_dataset_chunk_with_overwrite_behaviour(
        self, mock_construct_chunked_dataframe
    ):
        # Given
        schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                version=4,
                owners=[Owner(name="owner", email="owner@email.com")],
                update_behaviour="OVERWRITE",
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=True,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="object",
                    allow_null=False,
                ),
            ],
        )

        def dataset_chunk():
            return pd.DataFrame(
                {
                    "col1": ["one", "two", "three"],
                    "col2": [1, 2, 3],
                }
            )

        chunk1 = dataset_chunk()
        chunk2 = dataset_chunk()

        mock_construct_chunked_dataframe.return_value = [
            chunk1,
            chunk2,
        ]

        self.data_service.process_chunk = Mock()

        # When
        self.data_service.process_chunks(schema, Path("data.csv"), "123-456-789")

        # Then
        expected_calls = [
            call(schema, "123-456-789", chunk1),
            call(schema, "123-456-789", chunk2),
        ]
        self.data_service.process_chunk.assert_has_calls(expected_calls)
        self.s3_adapter.delete_previous_dataset_files.assert_called_once_with(
            "some", "other", 4, "123-456-789"
        )

    @patch("api.application.services.data_service.construct_chunked_dataframe")
    def test_processes_each_dataset_chunk_with_overwrite_behaviour_fails_to_delete_overidden_files(
        self, mock_construct_chunked_dataframe
    ):
        # Given
        schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                version=12,
                owners=[Owner(name="owner", email="owner@email.com")],
                update_behaviour="OVERWRITE",
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=True,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="object",
                    allow_null=False,
                ),
            ],
        )

        mock_construct_chunked_dataframe.return_value = []

        self.data_service.process_chunk = Mock()

        self.s3_adapter.delete_previous_dataset_files.side_effect = AWSServiceError(
            "something"
        )

        # When
        with pytest.raises(
            AWSServiceError,
            match=r"Overriding existing data failed for domain \[some\] and dataset \[other\]. Raw file identifier: 123-456-789",
        ):
            self.data_service.process_chunks(schema, Path("data.csv"), "123-456-789")

        # Then
        self.s3_adapter.delete_previous_dataset_files.assert_called_once_with(
            "some", "other", 12, "123-456-789"
        )

    # Process Chunks -----------------------------------------
    @patch("api.application.services.data_service.build_validated_dataframe")
    def test_validates_and_uploads_chunk(self, mock_build_validated_dataframe):
        # Given
        schema = self.valid_schema

        chunk = pd.DataFrame({})
        chunk2 = pd.DataFrame({})

        mock_build_validated_dataframe.return_value = chunk2
        self.data_service.upload_data = Mock()
        self.data_service.generate_permanent_filename = Mock(
            return_value="123-456-789_111-222-333.parquet"
        )

        # When
        self.data_service.process_chunk(schema, "123-456-789", chunk)

        # Then
        self.data_service.upload_data.assert_called_once_with(
            schema, chunk2, "123-456-789_111-222-333.parquet"
        )

    @patch("api.application.services.data_service.build_validated_dataframe")
    def test_raises_validation_error_when_validation_fails(
        self, mock_build_validated_dataframe
    ):
        # Given
        schema = self.valid_schema

        chunk = pd.DataFrame({})

        mock_build_validated_dataframe.side_effect = DatasetValidationError(
            "some error"
        )

        # When/Then
        with pytest.raises(DatasetValidationError, match="some error"):
            self.data_service.process_chunk(schema, "123-456-789", chunk)

    # Upload Data --------------------------------------------
    @patch("api.application.services.data_service.generate_partitioned_data")
    def test_partitions_and_uploads_data(self, mock_generate_partitioned_data):
        # Given
        schema = self.valid_schema

        dataframe = pd.DataFrame({})
        filename = "11111111_22222222.parquet"

        partitioned_dataframe = [
            ("some/path1", pd.DataFrame({})),
            ("some/path2", pd.DataFrame({})),
        ]
        mock_generate_partitioned_data.return_value = partitioned_dataframe

        # When
        self.data_service.upload_data(schema, dataframe, filename)

        # Then
        self.s3_adapter.upload_partitioned_data.assert_called_once_with(
            "some", "other", 2, filename, partitioned_dataframe
        )


class TestUpdateTableConfig:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.glue_adapter = Mock()
        self.data_service = DataService(
            self.s3_adapter,
            self.glue_adapter,
            None,
            None,
            None,
            None,
            None,
        )

    def test_update_table_config(self):
        schema = Schema(
            metadata=SchemaMetadata(
                domain="domain1",
                dataset="dataset1",
                version="1",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=True,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="object",
                    allow_null=False,
                ),
            ],
        )

        self.s3_adapter.find_schema.return_value = schema
        self.data_service.update_table_config("domain1", "dataset1")

        self.s3_adapter.find_schema.assert_called_once_with("domain1", "dataset1", 1)
        self.glue_adapter.update_catalog_table_config.assert_called_once_with(schema)


class TestListRawFiles:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.data_service = DataService(
            self.s3_adapter,
            None,
            None,
            None,
            None,
        )

    def test_list_raw_files_from_domain_and_dataset(self):
        self.s3_adapter.list_raw_files.return_value = [
            "2022-01-01T12:00:00-my_first_file.csv",
            "2022-02-10T15:00:00-my_second_file.csv",
            "2022-03-03T16:00:00-my_third_file.csv",
        ]
        list_raw_files = self.data_service.list_raw_files("domain", "dataset", 2)
        assert list_raw_files == [
            "2022-01-01T12:00:00-my_first_file.csv",
            "2022-02-10T15:00:00-my_second_file.csv",
            "2022-03-03T16:00:00-my_third_file.csv",
        ]
        self.s3_adapter.list_raw_files.assert_called_once_with("domain", "dataset", 2)

    def test_raises_exception_when_no_raw_files_found_for_domain_and_dataset(self):
        self.s3_adapter.list_raw_files.return_value = []
        with pytest.raises(
            UserError,
            match="There are no uploaded files for the domain \\[domain\\] or dataset \\[dataset\\]",
        ):
            self.data_service.list_raw_files("domain", "dataset", 1)

        self.s3_adapter.list_raw_files.assert_called_once_with("domain", "dataset", 1)


class TestDatasetInfoRetrieval:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.glue_adapter = Mock()
        self.query_adapter = Mock()
        self.aws_resource_adapter = Mock()
        self.protected_domain_service = Mock()
        self.valid_schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                version=2,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=False,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="object",
                    allow_null=False,
                ),
                Column(
                    name="date",
                    partition_index=None,
                    data_type="date",
                    allow_null=False,
                    format="%d/%m/%Y",
                ),
            ],
        )
        self.data_service = DataService(
            self.s3_adapter,
            self.glue_adapter,
            self.query_adapter,
            self.protected_domain_service,
            None,
        )
        self.glue_adapter.get_table_last_updated_date.return_value = (
            "2022-03-01 11:03:49+00:00"
        )

    def test_get_schema_information(self):
        expected_schema = EnrichedSchema(
            metadata=EnrichedSchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                version=2,
                owners=[Owner(name="owner", email="owner@email.com")],
                number_of_rows=48718,
                number_of_columns=3,
                last_updated="2022-03-01 11:03:49+00:00",
            ),
            columns=[
                EnrichedColumn(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=False,
                ),
                EnrichedColumn(
                    name="colname2",
                    partition_index=None,
                    data_type="object",
                    allow_null=False,
                ),
                EnrichedColumn(
                    name="date",
                    partition_index=None,
                    data_type="date",
                    allow_null=False,
                    format="%d/%m/%Y",
                    statistics={"max": "2021-07-01", "min": "2014-01-01"},
                ),
            ],
        )
        self.s3_adapter.find_schema.return_value = self.valid_schema
        self.query_adapter.query.return_value = pd.DataFrame(
            {
                "data_size": [48718],
                "max_date": ["2021-07-01"],
                "min_date": ["2014-01-01"],
            }
        )
        actual_schema = self.data_service.get_dataset_info("some", "other", 2)

        self.query_adapter.query.assert_called_once_with(
            "some",
            "other",
            2,
            SQLQuery(
                select_columns=[
                    "count(*) as data_size",
                    "max(date) as max_date",
                    "min(date) as min_date",
                ]
            ),
        )
        assert actual_schema == expected_schema
        self.glue_adapter.get_table_last_updated_date.assert_called_once_with(
            StorageMetaData("some", "other", 2).glue_table_name()
        )

    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_get_schema_information_for_multiple_dates(
        self, mock_handle_version_retrieval
    ):
        valid_schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                version=1,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=False,
                ),
                Column(
                    name="date",
                    partition_index=None,
                    data_type="date",
                    allow_null=False,
                    format="%d/%m/%Y",
                ),
                Column(
                    name="date2",
                    partition_index=None,
                    data_type="date",
                    allow_null=False,
                    format="%d/%m/%Y",
                ),
            ],
        )

        expected_schema = EnrichedSchema(
            metadata=EnrichedSchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                version=1,
                owners=[Owner(name="owner", email="owner@email.com")],
                number_of_rows=48718,
                number_of_columns=3,
                last_updated="2022-03-01 11:03:49+00:00",
            ),
            columns=[
                EnrichedColumn(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=False,
                ),
                EnrichedColumn(
                    name="date",
                    partition_index=None,
                    data_type="date",
                    allow_null=False,
                    format="%d/%m/%Y",
                    statistics={"max": "2021-07-01", "min": "2014-01-01"},
                ),
                EnrichedColumn(
                    name="date2",
                    partition_index=None,
                    data_type="date",
                    allow_null=False,
                    format="%d/%m/%Y",
                    statistics={"max": "2020-07-01", "min": "2015-01-01"},
                ),
            ],
        )
        self.s3_adapter.find_schema.return_value = valid_schema
        self.query_adapter.query.return_value = pd.DataFrame(
            {
                "data_size": [48718],
                "max_date": ["2021-07-01"],
                "min_date": ["2014-01-01"],
                "max_date2": ["2020-07-01"],
                "min_date2": ["2015-01-01"],
            }
        )

        mock_handle_version_retrieval.return_value = 1
        actual_schema = self.data_service.get_dataset_info("some", "other", None)

        self.query_adapter.query.assert_called_once_with(
            "some",
            "other",
            1,
            SQLQuery(
                select_columns=[
                    "count(*) as data_size",
                    "max(date) as max_date",
                    "max(date2) as max_date2",
                    "min(date) as min_date",
                    "min(date2) as min_date2",
                ]
            ),
        )
        mock_handle_version_retrieval.assert_called_once_with("some", "other", None)

        assert actual_schema == expected_schema

    def test_get_schema_size_for_datasets_with_no_dates(self):
        valid_schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                version=3,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=False,
                )
            ],
        )
        expected_schema = EnrichedSchema(
            metadata=EnrichedSchemaMetadata(
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                version=3,
                owners=[Owner(name="owner", email="owner@email.com")],
                number_of_rows=48718,
                number_of_columns=1,
                last_updated="2022-03-01 11:03:49+00:00",
            ),
            columns=[
                EnrichedColumn(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=False,
                )
            ],
        )
        self.s3_adapter.find_schema.return_value = valid_schema
        self.query_adapter.query.return_value = pd.DataFrame({"data_size": [48718]})

        actual_schema = self.data_service.get_dataset_info("some", "other", 3)

        self.query_adapter.query.assert_called_once_with(
            "some", "other", 3, SQLQuery(select_columns=["count(*) as data_size"])
        )

        assert actual_schema == expected_schema

    def test_raises_error_when_schema_not_found(self):
        self.s3_adapter.find_schema.return_value = None

        with pytest.raises(SchemaNotFoundError):
            self.data_service.get_dataset_info("some", "other", 1)

    def test_generates_raw_file_identifier(self):
        filename = self.data_service.generate_raw_file_identifier()
        pattern = "[\\d\\w]{8}-[\\d\\w]{4}-[\\d\\w]{4}-[\\d\\w]{4}-[\\d\\w]{12}"
        assert re.match(pattern, filename)


class TestQueryDataset:
    def setup_method(self):
        self.athena_adapter = Mock()
        self.glue_adapter = Mock()
        self.data_service = DataService(
            None,
            self.glue_adapter,
            self.athena_adapter,
            None,
            None,
        )

    def test_is_query_too_large_with_limit_under(self):
        query = SQLQuery(limit=100)

        response = self.data_service.is_query_too_large("domain1", "dataset1", 2, query)
        assert response is False

    def test_is_query_too_large_with_rows_under(self):
        query = SQLQuery()
        self.glue_adapter.get_no_of_rows.return_value = 1000

        response = self.data_service.is_query_too_large("domain1", "dataset1", 2, query)
        assert response is False

    def test_is_query_too_large_with_rows_over(self):
        query = SQLQuery()
        self.glue_adapter.get_no_of_rows.return_value = DATASET_QUERY_LIMIT + 1

        response = self.data_service.is_query_too_large("domain1", "dataset1", 2, query)
        assert response is True

    def test_query_data_success(self):
        query = SQLQuery()
        expected_response = pd.DataFrame().empty
        self.data_service.is_query_too_large = Mock(return_value=False)
        self.athena_adapter.query.return_value = expected_response

        response = self.data_service.query_data("domain1", "dataset1", 2, query)
        assert response == expected_response

        self.athena_adapter.query.assert_called_once_with(
            "domain1", "dataset1", 2, query
        )
        self.data_service.is_query_too_large.assert_called_once_with(
            "domain1", "dataset1", 2, query
        )

    def test_query_data_for_query_too_large(self):
        query = SQLQuery()
        self.data_service.is_query_too_large = Mock(return_value=True)
        with pytest.raises(UnprocessableDatasetError):
            self.data_service.query_data("domain1", "dataset1", 1, query)

        self.data_service.is_query_too_large.assert_called_once_with(
            "domain1", "dataset1", 1, query
        )
        self.athena_adapter.query.assert_not_called()

    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_query_data_for_version_not_specified(self, mock_handle_version_retrieval):
        domain = "domain1"
        dataset = "dataset1"
        version = None
        query = SQLQuery()
        self.glue_adapter.get_no_of_rows.return_value = 2343
        mock_handle_version_retrieval.return_value = 3

        self.data_service.query_data(domain, dataset, version, query)

        self.glue_adapter.get_no_of_rows.assert_called_once_with("domain1_dataset1_3")
        self.athena_adapter.query.assert_called_once_with(
            "domain1", "dataset1", 3, query
        )
        mock_handle_version_retrieval.assert_called_once_with(domain, dataset, version)


class TestQueryLargeDataset:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.athena_adapter = Mock()
        self.glue_adapter = Mock()
        self.job_service = Mock()
        self.data_service = DataService(
            self.s3_adapter,
            self.glue_adapter,
            self.athena_adapter,
            None,
            None,
            None,
            self.job_service,
        )

    @patch("api.application.services.data_service.Thread")
    def test_query_large_creates_query_job_and_triggers_async_query(self, mock_thread):
        subject_id = "subject-123"
        domain = "domain1"
        dataset = "dataset1"
        version = 4
        query = SQLQuery()
        query_job = Mock()
        query_job.job_id = "12838"
        self.job_service.create_query_job.return_value = query_job
        query_execution_id = "111-222-333"
        self.athena_adapter.query_async.return_value = query_execution_id

        response = self.data_service.query_large_data(
            subject_id, domain, dataset, version, query
        )

        assert response == "12838"
        self.job_service.create_query_job.assert_called_once_with(
            subject_id, domain, dataset, version
        )
        self.athena_adapter.query_async.assert_called_once_with(
            domain, dataset, version, query
        )

        mock_thread.assert_called_once_with(
            target=self.data_service.generate_results_download_url_async,
            args=(
                query_job,
                query_execution_id,
            ),
        )

    @patch("api.application.services.data_service.Thread")
    @patch("api.application.services.data_service.handle_version_retrieval")
    def test_query_large_data_for_version_not_specified(
        self, mock_handle_version_retrieval, mock_thread
    ):
        subject_id = "subject-123"
        domain = "domain1"
        dataset = "dataset1"
        version = None
        query = SQLQuery()
        query_job = Mock()
        query_job.job_id = "12838"
        mock_handle_version_retrieval.return_value = 3
        self.job_service.create_query_job.return_value = query_job
        query_execution_id = "111-222-333"
        self.athena_adapter.query_async.return_value = query_execution_id

        response = self.data_service.query_large_data(
            subject_id, domain, dataset, version, query
        )

        assert response == "12838"
        self.job_service.create_query_job.assert_called_once_with(
            subject_id, domain, dataset, 3
        )
        mock_handle_version_retrieval.assert_called_once_with(domain, dataset, version)
        mock_thread.assert_called_once_with(
            target=self.data_service.generate_results_download_url_async,
            args=(
                query_job,
                query_execution_id,
            ),
        )

    def test_updates_query_job_with_presigned_s3_url_when_querying_is_complete(self):
        # GIVEN
        query_job = Mock()
        query_execution_id = "111-222-333"
        download_url = "https://the-url.com"

        self.s3_adapter.generate_query_result_download_url.return_value = download_url

        expected_job_calls = [
            call(query_job, QueryStep.RUNNING),
            call(query_job, QueryStep.GENERATING_RESULTS),
        ]

        # WHEN
        self.data_service.generate_results_download_url_async(
            query_job, query_execution_id
        )

        # THEN
        self.athena_adapter.wait_for_query_to_complete.assert_called_once_with(
            query_execution_id
        )
        self.s3_adapter.generate_query_result_download_url.assert_called_once_with(
            query_execution_id
        )

        self.job_service.update_step.assert_has_calls(expected_job_calls)
        self.job_service.succeed_query.assert_called_once_with(query_job, download_url)

    def test_fails_query_job_upon_query_execution_failure(self):
        # GIVEN
        query_job = Mock()
        query_execution_id = "111-222-333"

        self.athena_adapter.wait_for_query_to_complete.side_effect = (
            QueryExecutionError("the error message")
        )

        # WHEN
        self.data_service.generate_results_download_url_async(
            query_job, query_execution_id
        )

        # THEN
        self.athena_adapter.wait_for_query_to_complete.assert_called_once_with(
            query_execution_id
        )
        self.s3_adapter.generate_query_result_download_url.assert_not_called()

        self.job_service.set_results_url.assert_not_called()
        self.job_service.fail.assert_called_once_with(query_job, ["the error message"])

    @pytest.mark.parametrize("error", [AWSServiceError, Exception])
    def test_fails_query_job_upon_any_other_error_and_raises_error(self, error):
        # GIVEN
        query_job = Mock()
        query_execution_id = "111-222-333"

        self.s3_adapter.generate_query_result_download_url.side_effect = error(
            "the error message"
        )

        expected_job_calls = [
            call(query_job, QueryStep.RUNNING),
            call(query_job, QueryStep.GENERATING_RESULTS),
        ]

        # WHEN/THEN
        with pytest.raises(error, match="the error message"):
            self.data_service.generate_results_download_url_async(
                query_job, query_execution_id
            )

        self.athena_adapter.wait_for_query_to_complete.assert_called_once_with(
            query_execution_id
        )
        self.s3_adapter.generate_query_result_download_url.assert_called_once_with(
            query_execution_id
        )

        self.job_service.update_step.assert_has_calls(expected_job_calls)
        self.job_service.set_results_url.assert_not_called()
        self.job_service.fail.assert_called_once_with(query_job, ["the error message"])
