from mock import Mock, call
import pytest
import io
import pandas as pd
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
    InvalidPermissionsException,
    SubjectNotFoundException,
    SubjectAlreadyExistsException,
    DatasetNotFoundException,
    InvalidDomainNameException,
    DomainConflictException,
    ClientDoesNotHaveUserAdminPermissionsException,
    ClientDoesNotHaveDataAdminPermissionsException,
)
from .conftest import RAPID_URL, RAPID_TOKEN

DUMMY_SCHEMA = {
    "metadata": {
        "layer": "raw",
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
            "unique": True,
        },
        {
            "name": "column_b",
            "data_type": "object",
            "partition_index": None,
            "allow_null": True,
            "format": None,
            "unique": True,
        },
    ],
}


class TestRapid:
    @pytest.mark.usefixtures("rapid")
    def test_generate_headers(self, rapid: Rapid):
        expected = {
            "Authorization": f"Bearer {RAPID_TOKEN}",
            "Content-Type": "application/json",
        }

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
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        requests_mock.post(
            f"{RAPID_URL}/datasets/{layer}/{domain}/{dataset}/query",
            json={
                "0": {"column1": "value1", "column2": "value2"},
                "2": {"column1": "value3", "column2": "value4"},
                "3": {"column1": "value5", "column2": "value6"},
            },
            status_code=200,
        )
        res = rapid.download_dataframe(layer, domain, dataset)
        assert res.shape == (3, 2)
        assert list(res.columns) == ["column1", "column2"]

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_download_dataframe_success_with_version(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        version = "5"
        requests_mock.post(
            f"{RAPID_URL}/datasets/{layer}/{domain}/{dataset}/query?version=5",
            json={
                "0": {"column1": "value1", "column2": "value2"},
                "2": {"column1": "value3", "column2": "value4"},
                "3": {"column1": "value5", "column2": "value6"},
            },
            status_code=200,
        )
        res = rapid.download_dataframe(layer, domain, dataset, version)
        assert res.shape == (3, 2)
        assert list(res.columns) == ["column1", "column2"]

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_upload_dataframe_success_after_waiting(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        job_id = 1234
        df = pd.DataFrame()
        requests_mock.post(
            f"{RAPID_URL}/datasets/{layer}/{domain}/{dataset}",
            json={"details": {"job_id": job_id}},
            status_code=202,
        )
        rapid.wait_for_job_outcome = Mock()
        rapid.convert_dataframe_for_file_upload = Mock(return_value={})

        res = rapid.upload_dataframe(layer, domain, dataset, df)
        assert res == "Success"
        rapid.wait_for_job_outcome.assert_called_once_with(job_id)
        rapid.convert_dataframe_for_file_upload.assert_called_once_with(df)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_upload_dataframe_success_no_waiting(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        job_id = 1234
        df = pd.DataFrame()
        requests_mock.post(
            f"{RAPID_URL}/datasets/{layer}/{domain}/{dataset}",
            json={"details": {"job_id": job_id}},
            status_code=202,
        )
        rapid.convert_dataframe_for_file_upload = Mock(return_value={})

        res = rapid.upload_dataframe(layer, domain, dataset, df, wait_to_complete=False)
        assert res == job_id
        rapid.convert_dataframe_for_file_upload.assert_called_once_with(df)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_upload_dataframe_failure(self, requests_mock: Mocker, rapid: Rapid):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        job_id = 1234
        df = pd.DataFrame()
        requests_mock.post(
            f"{RAPID_URL}/datasets/{layer}/{domain}/{dataset}",
            json={"details": {"job_id": job_id}},
            status_code=400,
        )
        rapid.convert_dataframe_for_file_upload = Mock(return_value={})

        with pytest.raises(DataFrameUploadFailedException):
            rapid.upload_dataframe(layer, domain, dataset, df, wait_to_complete=False)
            rapid.convert_dataframe_for_file_upload.assert_called_once_with(df)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_fetch_dataset_info_success(self, requests_mock: Mocker, rapid: Rapid):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        mocked_response = {"data": "dummy"}
        requests_mock.get(
            f"{RAPID_URL}/datasets/{layer}/{domain}/{dataset}/info",
            json=mocked_response,
            status_code=200,
        )

        res = rapid.fetch_dataset_info(layer, domain, dataset)
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_fetch_dataset_info_failure(self, requests_mock: Mocker, rapid: Rapid):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        mocked_response = {"details": "dummy"}
        requests_mock.get(
            f"{RAPID_URL}/datasets/{layer}/{domain}/{dataset}/info",
            json=mocked_response,
            status_code=422,
        )

        with pytest.raises(DatasetInfoFailedException):
            rapid.fetch_dataset_info(layer, domain, dataset)

    @pytest.mark.usefixtures("rapid")
    def test_convert_dataframe_for_file_upload(self, rapid: Rapid):
        df = pd.DataFrame()
        res = rapid.convert_dataframe_for_file_upload(df)
        filename = res["file"][0]
        data = io.BytesIO(res["file"][1])
        df = pd.read_parquet(data)

        assert filename.startswith("rapid-sdk") and filename.endswith(".parquet")
        assert len(df) == 0

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_generate_schema_success(self, requests_mock: Mocker, rapid: Rapid):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        sensitivity = "PUBLIC"
        df = pd.DataFrame()
        mocked_response = {
            "metadata": {
                "layer": "raw",
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
            f"{RAPID_URL}/schema/{layer}/{sensitivity}/{domain}/{dataset}/generate",
            json=mocked_response,
            status_code=200,
        )

        res = rapid.generate_schema(df, layer, domain, dataset, sensitivity)
        assert res.metadata.layer == "raw"
        assert res.metadata.domain == "test"
        assert res.metadata.dataset == "rapid_sdk"
        assert res.columns[0].name == "column_a"
        assert res.columns[1].name == "column_b"

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_generate_schema_failure(self, requests_mock: Mocker, rapid: Rapid):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        sensitivity = "PUBLIC"
        df = pd.DataFrame()
        mocked_response = {"data": "dummy"}
        requests_mock.post(
            f"{RAPID_URL}/schema/{layer}/{sensitivity}/{domain}/{dataset}/generate",
            json=mocked_response,
            status_code=400,
        )
        with pytest.raises(SchemaGenerationFailedException):
            rapid.generate_schema(df, layer, domain, dataset, sensitivity)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_schema_success(self, requests_mock: Mocker, rapid: Rapid):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.post(f"{RAPID_URL}/schema", json=mocked_response, status_code=201)
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

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_client_success(self, requests_mock: Mocker, rapid: Rapid):
        mocked_response = {
            "client_name": "client",
            "permissions": ["READ_ALL"],
            "client_id": "xxx-yyy-zzz",
            "client_secret": "1234567",
        }
        requests_mock.post(f"{RAPID_URL}/client", json=mocked_response, status_code=201)
        res = rapid.create_client("client", ["READ_ALL"])
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_client_failure(self, requests_mock: Mocker, rapid: Rapid):
        mocked_response = {"data": "dummy"}
        requests_mock.post(f"{RAPID_URL}/client", json=mocked_response, status_code=400)
        with pytest.raises(SubjectAlreadyExistsException):
            rapid.create_client("client", ["READ_ALL"])

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_delete_client_success(self, requests_mock: Mocker, rapid: Rapid):
        mocked_response = {"data": "dummy"}
        requests_mock.delete(
            f"{RAPID_URL}/client/xxx-yyy-zzz", json=mocked_response, status_code=200
        )
        res = rapid.delete_client("xxx-yyy-zzz")
        assert res is None

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_delete_client_failure(self, requests_mock: Mocker, rapid: Rapid):
        mocked_response = {"data": "dummy"}
        requests_mock.delete(
            f"{RAPID_URL}/client/xxx-yyy-zzz", json=mocked_response, status_code=400
        )
        with pytest.raises(SubjectNotFoundException):
            rapid.delete_client("xxx-yyy-zzz")

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_update_subject_permissions_success(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        mocked_response = {"data": "dummy"}
        requests_mock.put(
            f"{RAPID_URL}/subject/permissions", json=mocked_response, status_code=200
        )
        res = rapid.update_subject_permissions("xxx-yyy-zzz", ["READ_ALL"])
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_update_subject_permissions_failure(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        mocked_response = {"data": "dummy"}
        requests_mock.put(
            f"{RAPID_URL}/subject/permissions", json=mocked_response, status_code=400
        )
        with pytest.raises(InvalidPermissionsException):
            rapid.update_subject_permissions("xxx-yyy-zzz", ["READ_ALL"])

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_protected_domain_invalid_name_failure(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        mocked_response = {
            "details": "The value set for domain [dummy] can only contain alphanumeric and underscore `_` characters and must start with an alphabetic character"
        }
        requests_mock.post(
            f"{RAPID_URL}/protected_domains/dummy",
            json=mocked_response,
            status_code=400,
        )
        with pytest.raises(InvalidDomainNameException) as exc_info:
            rapid.create_protected_domain("dummy")

        assert (
            str(exc_info.value)
            == "The value set for domain [dummy] can only contain alphanumeric and underscore `_` characters and must start with an alphabetic character"
        )

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_protected_domain_conflict_failure(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        mocked_response = {"details": "The protected domain, [dummy] already exists"}
        requests_mock.post(
            f"{RAPID_URL}/protected_domains/dummy",
            json=mocked_response,
            status_code=409,
        )
        with pytest.raises(DomainConflictException) as exc_info:
            rapid.create_protected_domain("dummy")

        assert str(exc_info.value) == "The protected domain, [dummy] already exists"

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_protected_domain_success(self, requests_mock: Mocker, rapid: Rapid):
        mocked_response = {"data": "dummy"}
        requests_mock.post(
            f"{RAPID_URL}/protected_domains/dummy",
            json=mocked_response,
            status_code=201,
        )
        res = rapid.create_protected_domain("dummy")
        assert res is None

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_user_success(self, requests_mock: Mocker, rapid: Rapid):
        mocked_response = {
            "username": "user",
            "email": "user",
            "permissions": ["READ_ALL"],
            "user_id": "xxx-yyy-zzz",
        }
        requests_mock.post(f"{RAPID_URL}/user", json=mocked_response, status_code=201)
        res = rapid.create_user("user", "user@user.com", ["READ_ALL"])
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_user_failure_subjectalreadyexists(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        mocked_response = {
            "details": "The user 'user' or email 'user@user.com' already exist"
        }
        requests_mock.post(f"{RAPID_URL}/user", json=mocked_response, status_code=400)
        with pytest.raises(SubjectAlreadyExistsException):
            rapid.create_user("user", "user@user.com", ["READ_ALL"])

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_user_failure_invalidpermissions(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        mocked_response = {
            "details": "One or more of the provided permissions is invalid or duplicated"
        }
        requests_mock.post(f"{RAPID_URL}/user", json=mocked_response, status_code=400)
        with pytest.raises(InvalidPermissionsException):
            rapid.create_user("user", "user@user.com", ["READ_ALL"])

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_create_user_failure_ClientDoesNotHaveUserAdminPermissions(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        mocked_response = {"details": "data"}
        requests_mock.post(f"{RAPID_URL}/user", json=mocked_response, status_code=401)
        with pytest.raises(ClientDoesNotHaveUserAdminPermissionsException):
            rapid.create_user("user", "user@user.com", ["READ_ALL"])

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_delete_user_success(self, requests_mock: Mocker, rapid: Rapid):
        mocked_response = {"username": "user", "user_id": "xxx-yyy-zzz"}
        requests_mock.delete(f"{RAPID_URL}/user", json=mocked_response, status_code=200)
        res = rapid.delete_user("user", "xxx-yyy-zzz")
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_delete_user_failure_SubjectNotFound(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        mocked_response = {"data": "dummy"}
        requests_mock.delete(f"{RAPID_URL}/user", json=mocked_response, status_code=400)
        with pytest.raises(SubjectNotFoundException):
            rapid.delete_user("user", "xxx-yyy-zzz")

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_delete_user_failure_ClientDoesNotHaveUserAdminPermissions(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        mocked_response = {
            "details": "User xxx-yyy-zzz does not have permissions that grant access to the endpoint scopes [<Action.USER_ADMIN: 'USER_ADMIN'>]"
        }
        requests_mock.delete(f"{RAPID_URL}/user", json=mocked_response, status_code=401)
        with pytest.raises(ClientDoesNotHaveUserAdminPermissionsException):
            rapid.delete_user("user", "xxx-yyy-zzz")

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_list_subjects_success(self, requests_mock: Mocker, rapid: Rapid):
        expected = {"response": "dummy"}
        requests_mock.get(f"{RAPID_URL}/subjects", json=expected)

        res = rapid.list_subjects()
        assert res == expected

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_list_subjects_failure_ClientDoesNotHaveUserAdminPermissions(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        expected = {
            "details": "User xxx-yyy-zzz does not have permissions that grant access to the endpoint scopes [<Action.USER_ADMIN: 'USER_ADMIN'>]"
        }
        requests_mock.get(f"{RAPID_URL}/subjects", json=expected, status_code=401)
        with pytest.raises(ClientDoesNotHaveUserAdminPermissionsException):
            rapid.list_subjects()

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_list_layers(self, requests_mock: Mocker, rapid: Rapid):
        expected = {"response": "dummy"}
        requests_mock.get(f"{RAPID_URL}/layers", json=expected)

        res = rapid.list_layers()
        assert res == expected

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_list_protected_domains(self, requests_mock: Mocker, rapid: Rapid):
        expected = {
            "details": "User xxx-yyy-zzz does not have permissions that grant access to the endpoint scopes [<Action.USER_ADMIN: 'USER_ADMIN'>]"
        }
        requests_mock.get(f"{RAPID_URL}/protected_domains", json=expected)

        res = rapid.list_protected_domains()
        assert res == expected

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_list_protected_domains_failure_ClientDoesNotHaveUserAdminPermissions(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        expected = {
            "details": "User xxx-yyy-zzz does not have permissions that grant access to the endpoint scopes [<Action.USER_ADMIN: 'USER_ADMIN'>]"
        }
        requests_mock.get(
            f"{RAPID_URL}/protected_domains", json=expected, status_code=401
        )
        with pytest.raises(ClientDoesNotHaveUserAdminPermissionsException):
            rapid.list_protected_domains()

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_delete_dataset_success(self, requests_mock: Mocker, rapid: Rapid):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        mocked_response = {"details": "{dataset} has been deleted."}
        requests_mock.delete(
            f"{RAPID_URL}/datasets/{layer}/{domain}/{dataset}",
            json=mocked_response,
            status_code=202,
        )
        res = rapid.delete_dataset(layer, domain, dataset)
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_delete_dataset_failure_DatasetNotFound(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        mocked_response = {"response": "dummy"}
        requests_mock.delete(
            f"{RAPID_URL}/datasets/{layer}/{domain}/{dataset}",
            json=mocked_response,
            status_code=400,
        )
        with pytest.raises(DatasetNotFoundException):
            rapid.delete_dataset(layer, domain, dataset)

    @pytest.mark.usefixtures("requests_mock", "rapid")
    def test_delete_dataset_failure_ClientDoesNotHaveDataAdminPermissions(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        mocked_response = {
            "details": "User xxx-yyy-zzz does not have permissions that grant access to the endpoint scopes [<Action.DATA_ADMIN: 'DATA_ADMIN'>]"
        }
        requests_mock.delete(
            f"{RAPID_URL}/datasets/{layer}/{domain}/{dataset}",
            json=mocked_response,
            status_code=401,
        )
        with pytest.raises(ClientDoesNotHaveDataAdminPermissionsException):
            rapid.delete_dataset(layer, domain, dataset)
