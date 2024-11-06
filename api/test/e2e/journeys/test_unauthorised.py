from http import HTTPStatus
import requests
from test.e2e.journeys.base_journey import BaseAuthenticatedJourneyTest, SchemaVersion
from jinja2 import Template
from strenum import StrEnum
import os
import pytest

RESOURCE_PREFIX = os.environ["E2E_RESOURCE_PREFIX"]


class TestUnauthorisedJourney(BaseAuthenticatedJourneyTest):
    dataset = None
    test_subject_id = None
    test_job_id = None

    def client_name(self) -> str:
        return "E2E_TEST_CLIENT_WRITE_ALL"

    @classmethod
    def setup_class(cls):
        cls.dataset = cls.create_schema("unauthorised")
        cls.test_subject_id = cls.get_subject_id("e2e_test_client_base_permissions")
        cls.test_job_id = cls.fetch_job_id()

    @classmethod
    def teardown_class(cls):
        cls.delete_dataset(cls.dataset)

    @classmethod
    def fetch_job_id(cls):
        response = requests.get(
            cls.jobs_url(cls),
            headers=cls.generate_auth_headers(
                cls, "E2E_TEST_CLIENT_READ_ALL_WRITE_ALL"
            ),
        )
        assert response.status_code == HTTPStatus.OK
        return response.json()[0]["job_id"]

    @classmethod
    def get_subject_id(cls, subject_name: str) -> str:
        subject_name = "f{RESOURCE_PREFIX}_{subject_name}"
        response = requests.get(
            f"{cls.subjects_url(cls)}",
            headers=cls.generate_auth_headers(cls, "E2E_TEST_CLIENT_DATA_ADMIN"),
        )
        assert response.status_code == HTTPStatus.OK

        subjects = response.json()
        for subject in subjects:
            if subject["subject_name"] == subject_name:
                return subject["subject_id"]
        if len(subjects) == 0:
            raise ValueError("No subjects found")

    def test_query_existing_dataset_when_not_authorised_to_read(self):
        url = self.query_dataset_url(self.layer, self.e2e_test_domain, self.dataset)
        response = requests.post(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_existing_dataset_info_when_not_authorised_to_read(self):
        url = self.info_dataset_url(self.layer, self.e2e_test_domain, self.dataset)
        response = requests.get(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_list_permissions_when_not_user_admin(self):
        response = requests.get(
            self.permissions_url(), headers=self.generate_auth_headers()
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_user_when_not_user_admin(self):
        response = requests.post(
            self.user_url(),
            headers=self.generate_auth_headers(),
            json=self.generate_username_payload(),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_user_when_not_user_admin(self):
        response = requests.delete(
            self.user_url(),
            headers=self.generate_auth_headers(),
            json=self.generate_username_payload(),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_client_when_not_user_admin(self):
        response = requests.post(
            self.client_url(),
            headers=self.generate_auth_headers(),
            json=self.generate_client_payload(),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_client_when_not_user_admin(self):
        response = requests.delete(
            f"{self.client_url()}/placeholder_id",
            headers=self.generate_auth_headers(),
            json=self.generate_client_payload(),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_schema_when_not_user_admin(self):
        schema_v1 = self.read_schema_version(SchemaVersion.V1)
        response = requests.post(
            self.schema_endpoint,
            headers=self.generate_auth_headers(),
            json=schema_v1,
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_upload_data_when_unauthorised(self):
        files = {
            "file": (self.csv_filename, open("./test/e2e/" + self.csv_filename, "rb"))
        }
        upload_url = self.upload_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset
        )
        response = requests.post(
            upload_url,
            headers=self.generate_auth_headers("E2E_TEST_CLIENT_DATA_ADMIN"),
            files=files,
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_protected_domain_when_not_data_admin(self):
        response = requests.post(
            self.protected_domain_url(),
            headers=self.generate_auth_headers(),
            json={"domain_name": "test_e2e_protected_new"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_protected_domain_when_not_data_admin(self):
        response = requests.delete(
            self.protected_domain_url(),
            headers=self.generate_auth_headers(),
            json={"domain_name": "test_e2e_protected"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_list_datasets_when_not_authorised(self):
        response = requests.post(
            self.list_datasets_url(),
            headers=self.generate_auth_headers(),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_query_large_dataset_when_not_authorised(self):
        url = self.query_dataset_url_large(
            self.layer, self.e2e_test_domain, self.dataset
        )
        response = requests.post(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_update_schema_when_not_authorised(self):
        schema = self.read_schema_version(SchemaVersion.V1)
        response = requests.put(
            self.schema_url(),
            headers=self.generate_auth_headers(),
            json=schema,
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_subject_permissions_when_not_authorised(self):
        response = requests.get(
            f"{self.subjects_url()}", headers=self.generate_auth_headers()
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_update_subject_permissions_when_not_authorised(self):
        response = requests.put(
            f"{self.subjects_url()}/permissions",
            headers=self.generate_auth_headers(),
            json={"subject_id": self.test_subject_id, "permissions": ["READ_ALL"]},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_all_jobs_when_not_authorised(self):
        response = requests.get(
            self.jobs_url(),
            headers=self.generate_auth_headers("E2E_TEST_CLIENT_DATA_ADMIN"),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_job_when_not_authorised(self):
        response = requests.get(
            f"{self.jobs_url()}/placeholder_id",
            headers=self.generate_auth_headers("E2E_TEST_CLIENT_DATA_ADMIN"),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
