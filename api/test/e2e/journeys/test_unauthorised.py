from http import HTTPStatus

import requests
import pytest
from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
)
import os
from jinja2 import Template
from strenum import StrEnum
import json


class SchemaVersion(StrEnum):
    V1 = "v1"
    V2 = "v2"


class TestUnauthorisedJourney(BaseAuthenticatedJourneyTest):
    dataset = None

    def client_name(self) -> str:
        return "E2E_TEST_CLIENT_WRITE_ALL"

    @classmethod
    def setup_class(cls):
        cls.dataset = cls.create_schema("unauthorised")

    @classmethod
    def teardown_class(cls):
        cls.delete_dataset(cls.dataset)

    def read_schema_version(self, version: SchemaVersion) -> dict:
        with open(
            os.path.join(self.schema_directory, f"test_e2e-schema_{version}.json.tpl")
        ) as file:
            template = Template(file.read())
            contents = template.render(name=self.dataset)
            return json.loads(contents)

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
            json={
                "username": "johnDoe",
                "email": "johndoe@no10.gov.uk",
                "permissions": ["READ_ALL", "WRITE_DEFAULT_PUBLIC"],
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_user_when_not_user_admin(self):
        response = requests.delete(
            self.user_url(),
            headers=self.generate_auth_headers(),
            json={
                "username": "johnDoe",
                "email": "johndoe@no10.gov.uk",
                "permissions": ["READ_ALL", "WRITE_DEFAULT_PUBLIC"],
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_client_when_not_user_admin(self):
        response = requests.post(
            self.client_url(),
            headers=self.generate_auth_headers(),
            json={
                "username": "johnDoe",
                "email": "johndoe@no10.gov.uk",
                "permissions": ["READ_ALL", "WRITE_DEFAULT_PUBLIC"],
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_client_when_not_user_admin(self):
        response = requests.delete(
            f"{self.client_url()}/placeholder_id",
            headers=self.generate_auth_headers(),
            json={
                "client_name": "john_doe_client",
                "permissions": ["READ_ALL", "WRITE_DEFAULT_PUBLIC"],
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_schema_when_not_user_admin(self):
        response = requests.delete(
            self.user_url(),
            headers=self.generate_auth_headers(),
            json={
                "username": "johnDoe",
                "email": "johndoe@no10.gov.uk",
                "permissions": ["READ_ALL", "WRITE_DEFAULT_PUBLIC"],
            },
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
            json={"domain_name": "test_domain"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_protected_domain_when_not_data_admin(self):
        response = requests.delete(
            self.protected_domain_url(),
            headers=self.generate_auth_headers(),
            json={"domain_name": "test_domain"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_list_datasets_when_not_authorised(self):
        response = requests.post(
            self.list_datasets_url(),
            headers=self.generate_auth_headers(),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_query_large_dataset_when_not_authorised(self):
        url = self.query_large_dataset_url(
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
            json={"subject_id": "abc123", "permissions": ["READ_ALL"]},
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
