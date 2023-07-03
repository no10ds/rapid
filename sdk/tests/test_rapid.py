from mock import Mock, call
from pandas import DataFrame
import pytest
from requests_mock import Mocker

from rapid import Rapid
from rapid.items.schema import Schema
from rapid.exceptions import (
    DataFrameUploadFailedException,
    JobFailedException,
    SchemaGenerationFailedException,
    SchemaAlreadyExistsException,
    SchemaCreateFailedException,
    SchemaUpdateFailedException,
    UnableToFetchJobStatusException,
    DatasetInfoFailedException,
)
from .conftest import RAPID_URL, RAPID_TOKEN

DUMMY_SCHEMA = {
    "metadata": {
        "domain": "test",
        "dataset": "rapid_sdk",
        "sensitivity": "PUBLIC",
        "owners": [{"name": "Test", "email": "test@email.com"}],
        "version": None,
        "key_value_tags": None,
        "key_only_tags": None,
    },
    "columns": [
        {
            "name": "column_a",
            "data_type": "object",
            "partition_index": None,
            "allow_null": True,
            "format": None,
        },
        {
            "name": "column_b",
            "data_type": "object",
            "partition_index": None,
            "allow_null": True,
            "format": None,
        },
    ],
}


class TestRapid:
    @pytest.mark.usefixtures("rapid")
    def test_generate_headers(self, rapid: Rapid):
        expected = {"Authorization": f"Bearer {RAPID_TOKEN}"}

        assert expected == rapid.generate_headers()

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_list_datasets(self, requests_mock: Mocker, rapid: Rapid):
        expected = {"response": "dummy"}
        requests_mock.post(f"{RAPID_URL}/datasets", json=expected)

        res = rapid.list_datasets()
        assert res == expected

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_fetch_job_progress_success(self, requests_mock: Mocker, rapid: Rapid):
        job_id = 1234
        expected = {"response": "dummy"}

        requests_mock.get(f"{RAPID_URL}/jobs/{job_id}", json=expected)
        res = rapid.fetch_job_progress(job_id)
        assert res == expected

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_fetch_job_progress_fail(self, requests_mock: Mocker, rapid: Rapid):
        job_id = 1234
        expected = {"response": "error"}
        requests_mock.get(f"{RAPID_URL}/jobs/{job_id}", status_code=400, json=expected)

        with pytest.raises(UnableToFetchJobStatusException):
            rapid.fetch_job_progress(job_id)

    @pytest.mark.usefixtures("rapid")
    def test_wait_for_job_outcome_success(self, rapid: Rapid):
        rapid.fetch_job_progress = Mock(
            side_effect=[{"status": "IN PROGRESS"}, {"status": "SUCCESS"}]
        )
        job_id = 1234

        res = rapid.wait_for_job_outcome(job_id, interval=0.01)
        assert res is None
        expected_calls = [call(job_id), call(job_id)]
        assert rapid.fetch_job_progress.call_args_list == expected_calls

    @pytest.mark.usefixtures("rapid")
    def test_wait_for_job_outcome_failure(self, rapid: Rapid):
        rapid.fetch_job_progress = Mock(
            side_effect=[{"status": "IN PROGRESS"}, {"status": "FAILED"}]
        )
        job_id = 1234

        with pytest.raises(JobFailedException):
            rapid.wait_for_job_outcome(job_id, interval=0.01)
            expected_calls = [call(job_id), call(job_id)]
            assert rapid.fetch_job_progress.call_args_list == expected_calls

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_download_dataframe_success(self, requests_mock: Mocker, rapid: Rapid):
        domain = "test_domain"
        dataset = "test_dataset"
        requests_mock.post(
            f"{RAPID_URL}/datasets/{domain}/{dataset}/query",
            json={
                "0": {"column1": "value1", "column2": "value2"},
                "2": {"column1": "value3", "column2": "value4"},
                "3": {"column1": "value5", "column2": "value6"},
            },
            status_code=200,
        )
        res = rapid.download_dataframe(domain, dataset)
        assert res.shape == (3, 2)
        assert list(res.columns) == ["column1", "column2"]

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_download_dataframe_success_with_version(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        domain = "test_domain"
        dataset = "test_dataset"
        version = "5"
        requests_mock.post(
            f"{RAPID_URL}/datasets/{domain}/{dataset}/query?version=5",
            json={
                "0": {"column1": "value1", "column2": "value2"},
                "2": {"column1": "value3", "column2": "value4"},
                "3": {"column1": "value5", "column2": "value6"},
            },
            status_code=200,
        )
        res = rapid.download_dataframe(domain, dataset, version)
        assert res.shape == (3, 2)
        assert list(res.columns) == ["column1", "column2"]

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_upload_dataframe_success_after_waiting(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        domain = "test_domain"
        dataset = "test_dataset"
        job_id = 1234
        df = DataFrame()
        requests_mock.post(
            f"{RAPID_URL}/datasets/{domain}/{dataset}",
            json={"details": {"job_id": job_id}},
            status_code=202,
        )
        rapid.wait_for_job_outcome = Mock()
        rapid.convert_dataframe_for_file_upload = Mock(return_value={})

        res = rapid.upload_dataframe(domain, dataset, df)
        assert res == "Success"
        rapid.wait_for_job_outcome.assert_called_once_with(job_id)
        rapid.convert_dataframe_for_file_upload.assert_called_once_with(df)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_upload_dataframe_success_no_waiting(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        domain = "test_domain"
        dataset = "test_dataset"
        job_id = 1234
        df = DataFrame()
        requests_mock.post(
            f"{RAPID_URL}/datasets/{domain}/{dataset}",
            json={"details": {"job_id": job_id}},
            status_code=202,
        )
        rapid.convert_dataframe_for_file_upload = Mock(return_value={})

        res = rapid.upload_dataframe(domain, dataset, df, wait_to_complete=False)
        assert res == job_id
        rapid.convert_dataframe_for_file_upload.assert_called_once_with(df)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_upload_dataframe_failure(self, requests_mock: Mocker, rapid: Rapid):
        domain = "test_domain"
        dataset = "test_dataset"
        job_id = 1234
        df = DataFrame()
        requests_mock.post(
            f"{RAPID_URL}/datasets/{domain}/{dataset}",
            json={"details": {"job_id": job_id}},
            status_code=400,
        )
        rapid.convert_dataframe_for_file_upload = Mock(return_value={})

        with pytest.raises(DataFrameUploadFailedException):
            rapid.upload_dataframe(domain, dataset, df, wait_to_complete=False)
            rapid.convert_dataframe_for_file_upload.assert_called_once_with(df)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_generate_info_success(self, requests_mock: Mocker, rapid: Rapid):
        domain = "test_domain"
        dataset = "test_dataset"
        df = DataFrame()
        mocked_response = {"data": "dummy"}
        requests_mock.post(
            f"{RAPID_URL}/datasets/{domain}/{dataset}/info",
            json=mocked_response,
            status_code=200,
        )

        res = rapid.generate_info(df, domain, dataset)
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_generate_info_failure(self, requests_mock: Mocker, rapid: Rapid):
        domain = "test_domain"
        dataset = "test_dataset"
        df = DataFrame()
        mocked_response = {"details": "dummy"}
        requests_mock.post(
            f"{RAPID_URL}/datasets/{domain}/{dataset}/info",
            json=mocked_response,
            status_code=422,
        )

        with pytest.raises(DatasetInfoFailedException):
            rapid.generate_info(df, domain, dataset)

    @pytest.mark.usefixtures("rapid")
    def test_convert_dataframe_for_file_upload(self, rapid: Rapid):
        df = DataFrame()
        res = rapid.convert_dataframe_for_file_upload(df)
        filename = res["file"][0]
        data = res["file"][1]
        assert filename.startswith("rapid-sdk") and filename.endswith(".csv")
        assert data == "\n"

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_generate_schema_success(self, requests_mock: Mocker, rapid: Rapid):
        domain = "test_domain"
        dataset = "test_dataset"
        sensitivity = "PUBLIC"
        df = DataFrame()
        mocked_response = {
            "metadata": {
                "domain": "test",
                "dataset": "rapid_sdk",
                "sensitivity": "PUBLIC",
                "owners": [{"name": "Test", "email": "test@email.com"}],
                "version": None,
                "key_value_tags": None,
                "key_only_tags": None,
            },
            "columns": [
                {
                    "name": "column_a",
                    "data_type": "object",
                    "partition_index": None,
                    "allow_null": True,
                    "format": None,
                },
                {
                    "name": "column_b",
                    "data_type": "object",
                    "partition_index": None,
                    "allow_null": True,
                    "format": None,
                },
            ],
        }
        requests_mock.post(
            f"{RAPID_URL}/schema/{sensitivity}/{domain}/{dataset}/generate",
            json=mocked_response,
            status_code=200,
        )

        res = rapid.generate_schema(df, domain, dataset, sensitivity)
        assert res.metadata.domain == "test"
        assert res.metadata.dataset == "rapid_sdk"
        assert res.columns[0].name == "column_a"
        assert res.columns[1].name == "column_b"

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_generate_schema_failure(self, requests_mock: Mocker, rapid: Rapid):
        domain = "test_domain"
        dataset = "test_dataset"
        sensitivity = "PUBLIC"
        df = DataFrame()
        mocked_response = {"data": "dummy"}
        requests_mock.post(
            f"{RAPID_URL}/schema/{sensitivity}/{domain}/{dataset}/generate",
            json=mocked_response,
            status_code=400,
        )
        with pytest.raises(SchemaGenerationFailedException):
            rapid.generate_schema(df, domain, dataset, sensitivity)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_schema_success(self, requests_mock: Mocker, rapid: Rapid):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.post(f"{RAPID_URL}/schema", json=mocked_response, status_code=200)
        res = rapid.create_schema(schema)
        assert res is None

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_schema_failure_schema_already_exists(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.post(f"{RAPID_URL}/schema", json=mocked_response, status_code=409)
        with pytest.raises(SchemaAlreadyExistsException):
            rapid.create_schema(schema)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_schema_failure(self, requests_mock: Mocker, rapid: Rapid):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.post(f"{RAPID_URL}/schema", json=mocked_response, status_code=400)
        with pytest.raises(SchemaCreateFailedException):
            rapid.create_schema(schema)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_update_schema_success(self, requests_mock: Mocker, rapid: Rapid):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.put(f"{RAPID_URL}/schema", json=mocked_response, status_code=200)
        res = rapid.update_schema(schema)
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_update_schema_failure(self, requests_mock: Mocker, rapid: Rapid):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.put(f"{RAPID_URL}/schema", json=mocked_response, status_code=400)
        with pytest.raises(SchemaUpdateFailedException):
            rapid.update_schema(schema)
