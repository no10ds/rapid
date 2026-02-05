import re
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch, MagicMock, call

import pandas as pd
import pytest

from api.application.services.data_service import (
    DataService,
)
from api.common.custom_exceptions import (
    UserError,
    AWSServiceError,
    UnprocessableDatasetError,
    DatasetValidationError,
    QueryExecutionError,
)
from api.domain.Jobs.QueryJob import QueryStep
from api.domain.Jobs.UploadJob import UploadStep
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata
from rapid.items.query import Query


class TestUploadDataset:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.athena_adapter = Mock()
        self.job_service = Mock()
        self.schema_service = Mock()
        self.subject_service = Mock()
        self.data_service = DataService(
            self.s3_adapter,
            None,
            self.athena_adapter,
            self.job_service,
            self.schema_service,
            self.subject_service,
        )
        self.valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
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
                    data_type="int",
                    allow_null=True,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="string",
                    allow_null=False,
                ),
            ],
        )

    def chunked_dataframe_values(
        self, mock_construct_chunked_dataframe, dataframes: List[pd.DataFrame]
    ):
        mock_test_file_reader = MagicMock()
        mock_construct_chunked_dataframe.return_value = mock_test_file_reader
        mock_test_file_reader.__iter__.return_value = dataframes
        return mock_test_file_reader

    # Upload Dataset  -------------------------------------

    @patch("api.application.services.data_service.UploadJob")
    @patch("api.application.services.data_service.Thread")
    @patch("api.application.services.data_service.construct_chunked_dataframe")
    @patch.object(DataService, "process_upload")
    def test_upload_dataset_triggers_process_upload_and_returns_expected_data(
        self,
        mock_process_upload,
        _mock_construct_chunked_dataframe,
        mock_thread,
        mock_upload_job,
    ):
        # GIVEN
        schema = self.valid_schema

        self.schema_service.get_schema.return_value = schema

        self.data_service.generate_raw_file_identifier = Mock(
            return_value="123-456-789"
        )

        mock_job = Mock()
        self.job_service.create_upload_job.return_value = mock_job

        mock_job.job_id = "abc-123"
        mock_upload_job.return_value = mock_job

        # WHEN
        uploaded_raw_file = self.data_service.upload_dataset(
            "subject-123",
            "abc-123",
            DatasetMetadata("raw", "some", "other", 1),
            Path("data.csv"),
        )

        # THEN
        self.job_service.create_upload_job.assert_called_once_with(
            "subject-123",
            "abc-123",
            "data.csv",
            "123-456-789",
            DatasetMetadata("raw", "some", "other", 1),
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
    @patch.object(DataService, "validate_incoming_data")
    @patch.object(DataService, "process_chunks")
    @patch("api.application.services.data_service.delete_incoming_raw_file")
    @patch.object(DataService, "load_partitions")
    def test_process_upload_calls_relevant_methods(
        self,
        mock_load_partitions,
        mock_delete_incoming_raw_file,
        mock_process_chunks,
        mock_validate_incoming_data,
    ):
        # GIVEN
        schema = self.valid_schema
        upload_job = Mock()

        expected_update_step_calls = [
            call(upload_job, UploadStep.VALIDATION),
            call(upload_job, UploadStep.RAW_DATA_UPLOAD),
            call(upload_job, UploadStep.DATA_UPLOAD),
            call(upload_job, UploadStep.LOAD_PARTITIONS),
            call(upload_job, UploadStep.CLEAN_UP),
            call(upload_job, UploadStep.NONE),
        ]

        # WHEN
        self.data_service.process_upload(
            upload_job, schema, Path("data.csv"), "123-456-789"
        )

        # THEN
        mock_validate_incoming_data.assert_called_once_with(
            schema, Path("data.csv"), "123-456-789"
        )
        self.s3_adapter.upload_raw_data.assert_called_once_with(
            schema.metadata, Path("data.csv"), "123-456-789"
        )
        mock_process_chunks.assert_called_once_with(
            schema, Path("data.csv"), "123-456-789"
        )
        mock_delete_incoming_raw_file.assert_called_once_with(
            schema, Path("data.csv"), "123-456-789"
        )
        mock_load_partitions.assert_called_once_with(schema)

        self.job_service.update_step.assert_has_calls(expected_update_step_calls)
        self.job_service.succeed.assert_called_once_with(upload_job)

    @patch("api.application.services.data_service.delete_incoming_raw_file")
    @patch.object(DataService, "validate_incoming_data")
    def test_deletes_incoming_file_from_disk_and_fails_job_if_any_error_during_processing(
        self,
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
        self.schema_service.get_schema.return_value = schema

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

        self.schema_service.get_schema.return_value = schema

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

        self.schema_service.get_schema.return_value = schema

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
                "subject-123",
                "abc-123",
                DatasetMetadata("raw", "some", "other", 2),
                Path("data.csv"),
            )
        except DatasetValidationError as error:
            assert {
                "Failed to convert column [colname1] to type [integer]",
                "Column [colname1] has an incorrect data type. Expected integer, received "
                "string",
            }.issubset(error.message)

    @patch("api.application.services.data_service.construct_chunked_dataframe")
    def test_upload_dataset_in_chunks_with_invalid_data_in_multiple_chunks(
        self, mock_construct_chunked_dataframe
    ):
        schema = self.valid_schema

        self.schema_service.get_schema.return_value = schema

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
                "subject-123",
                "abc-123",
                DatasetMetadata("raw", "some", "other", 2),
                Path("data.csv"),
            )
        except DatasetValidationError as error:
            assert {
                "Column [colname1] has an incorrect data type. Expected integer, received "
                "string",
                "Failed to convert column [colname1] to type [integer]",
            }.issubset(error.message)

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
                layer="raw",
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
                    data_type="int",
                    allow_null=True,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="string",
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
            schema.metadata, "123-456-789"
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
            schema,
            filename,
            partitioned_dataframe,
        )

    def test_load_partitions(self):
        self.athena_adapter.query_sql_async.return_value = "query_id"

        self.data_service.load_partitions(self.valid_schema)
        self.athena_adapter.query_sql_async.assert_called_once_with(
            "MSCK REPAIR TABLE `raw_some_other_2`;"
        )
        self.athena_adapter.wait_for_query_to_complete.assert_called_once_with(
            "query_id"
        )


class TestListRawFiles:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.data_service = DataService(
            self.s3_adapter,
            None,
            None,
            None,
        )

    def test_list_raw_files_from_domain_and_dataset(self):
        dataset_metadata = DatasetMetadata("raw", "domain", "dataset", 2)
        self.s3_adapter.list_raw_files.return_value = [
            "2022-01-01T12:00:00-my_first_file.csv",
            "2022-02-10T15:00:00-my_second_file.csv",
            "2022-03-03T16:00:00-my_third_file.csv",
        ]
        list_raw_files = self.data_service.list_raw_files(dataset_metadata)
        assert list_raw_files == [
            "2022-01-01T12:00:00-my_first_file.csv",
            "2022-02-10T15:00:00-my_second_file.csv",
            "2022-03-03T16:00:00-my_third_file.csv",
        ]
        self.s3_adapter.list_raw_files.assert_called_once_with(dataset_metadata)

    def test_raises_exception_when_no_raw_files_found_for_domain_and_dataset(self):
        self.s3_adapter.list_raw_files.return_value = []
        dataset_metadata = DatasetMetadata("raw", "domain", "dataset", 1)
        with pytest.raises(
            UserError,
            match="There are no uploaded files for the layer \\[raw\\], domain \\[domain\\], dataset \\[dataset\\] and version \\[1\\]",
        ):
            self.data_service.list_raw_files(dataset_metadata)

        self.s3_adapter.list_raw_files.assert_called_once_with(dataset_metadata)


class TestDatasetInfoRetrieval:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.athena_adapter = Mock()
        self.job_service = Mock()
        self.schema_service = Mock()
        self.subject_service = Mock()
        self.valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
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
                    data_type="int",
                    allow_null=False,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="string",
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
            None,
            self.athena_adapter,
            self.job_service,
            self.schema_service,
            self.subject_service,
        )
        self.s3_adapter.get_last_updated_time.return_value = "2022-03-01 11:03:49+00:00"

    def test_get_last_updated_time(self):
        time = "2022-03-01 11:03:49+00:00"
        self.s3_adapter.get_last_updated_time.return_value = time

        last_updated_time = self.data_service.get_last_updated_time(
            self.valid_schema.metadata
        )
        assert last_updated_time == "2022-03-01 11:03:49+00:00"
        self.s3_adapter.get_last_updated_time.assert_called_once_with(
            self.valid_schema.metadata.dataset_location()
        )

    def test_get_last_updated_time_empty(self):
        self.s3_adapter.get_last_updated_time.return_value = None

        last_updated_time = self.data_service.get_last_updated_time(
            self.valid_schema.metadata
        )
        assert last_updated_time == "Never updated"
        self.s3_adapter.get_last_updated_time.assert_called_once_with(
            self.valid_schema.metadata.dataset_location()
        )

    def test_get_last_uploader_returns_subject_name(self):
        dataset_metadata = DatasetMetadata("raw", "some", "other", 2)
        self.job_service.db_adapter.get_latest_successful_upload_job.return_value = {
            "sk2": "subject-123"
        }
        self.subject_service.get_subject_name_by_id.return_value = "test_user"

        last_uploader = self.data_service.get_last_uploader(dataset_metadata)

        assert last_uploader == "test_user"
        self.subject_service.get_subject_name_by_id.assert_called_once_with("subject-123")

    def test_get_last_uploader_returns_unknown_when_no_job(self):
        dataset_metadata = DatasetMetadata("raw", "some", "other", 2)
        self.job_service.db_adapter.get_latest_successful_upload_job.return_value = None

        last_uploader = self.data_service.get_last_uploader(dataset_metadata)

        assert last_uploader == "Unknown"
        self.subject_service.get_subject_name_by_id.assert_not_called()

    def test_get_last_uploader_returns_unknown_when_subject_not_found(self):
        dataset_metadata = DatasetMetadata("raw", "some", "other", 2)
        self.job_service.db_adapter.get_latest_successful_upload_job.return_value = {
            "sk2": "subject-123"
        }
        self.subject_service.get_subject_name_by_id.side_effect = Exception("Subject not found")

        last_uploader = self.data_service.get_last_uploader(dataset_metadata)

        assert last_uploader == "Unknown"

    def test_generates_raw_file_identifier(self):
        filename = self.data_service.generate_raw_file_identifier()
        pattern = "[\\d\\w]{8}-[\\d\\w]{4}-[\\d\\w]{4}-[\\d\\w]{4}-[\\d\\w]{12}"
        assert re.match(pattern, filename)


class TestQueryDataset:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.athena_adapter = Mock()
        self.job_service = Mock()
        self.data_service = DataService(
            self.s3_adapter,
            None,
            self.athena_adapter,
            None,
            self.job_service,
        )

    def test_is_query_too_large_with_limit_under(self):
        query = Query(limit=100)

        response = self.data_service.is_query_too_large(
            DatasetMetadata("raw", "domain1", "dataset1", 2), query
        )
        assert response is False

    def test_is_query_too_large_with_dataset_size_under(self):
        query = Query()
        self.s3_adapter.get_folder_size.return_value = 100

        dataset = DatasetMetadata("raw", "domain1", "dataset1", 2)
        response = self.data_service.is_query_too_large(dataset, query)
        assert response is False
        self.s3_adapter.get_folder_size.assert_called_once_with(
            dataset.s3_file_location()
        )

    def test_is_query_too_large_with_dataset_size_over(self):
        query = Query()
        self.s3_adapter.get_folder_size.return_value = 1_000_000_000

        dataset = DatasetMetadata("raw", "domain1", "dataset1", 2)
        response = self.data_service.is_query_too_large(dataset, query)
        assert response is True
        self.s3_adapter.get_folder_size.assert_called_once_with(
            dataset.s3_file_location()
        )

    def test_query_data_success(self):
        query = Query()
        expected_response = pd.DataFrame().empty
        self.data_service.is_query_too_large = Mock(return_value=False)
        self.athena_adapter.query.return_value = expected_response
        dataset_metadata = DatasetMetadata("raw", "domain1", "dataset1", 2)

        response = self.data_service.query_data(dataset_metadata, query)
        assert response == expected_response

        self.athena_adapter.query.assert_called_once_with(dataset_metadata, query)
        self.data_service.is_query_too_large.assert_called_once_with(
            dataset_metadata, query
        )

    def test_query_data_for_query_too_large(self):
        query = Query()
        self.data_service.is_query_too_large = Mock(return_value=True)
        dataset_metadata = DatasetMetadata("raw", "domain1", "dataset1", 1)

        with pytest.raises(UnprocessableDatasetError):
            self.data_service.query_data(dataset_metadata, query)

        self.data_service.is_query_too_large.assert_called_once_with(
            dataset_metadata, query
        )
        self.athena_adapter.query.assert_not_called()


class TestQueryLargeDataset:
    def setup_method(self):
        self.s3_adapter = Mock()
        self.athena_adapter = Mock()
        self.job_service = Mock()
        self.data_service = DataService(
            self.s3_adapter,
            None,
            self.athena_adapter,
            self.job_service,
            self.job_service,
        )

    @patch("api.application.services.data_service.Thread")
    def test_query_large_creates_query_job_and_triggers_async_query(self, mock_thread):
        subject_id = "subject-123"
        dataset_metadata = DatasetMetadata("raw", "domain1", "dataset1", 4)
        query = Query()
        query_job = Mock()
        query_job.job_id = "12838"
        self.job_service.create_query_job.return_value = query_job
        query_execution_id = "111-222-333"
        self.athena_adapter.query_async.return_value = query_execution_id

        response = self.data_service.query_large_data(
            subject_id, dataset_metadata, query
        )

        assert response == "12838"
        self.job_service.create_query_job.assert_called_once_with(
            subject_id, dataset_metadata
        )
        self.athena_adapter.query_async.assert_called_once_with(dataset_metadata, query)

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
        with pytest.raises(error):
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
