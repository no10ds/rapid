from http import HTTPStatus
import requests

from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
    RESOURCE_PREFIX,
)
import json
import pytest


@pytest.mark.focus
class TestSubjectJourneys(BaseAuthenticatedJourneyTest):
    subject_id = None

    client_id = None

    def client_name(self) -> str:
        return "E2E_TEST_CLIENT_USER_ADMIN"

    def test_lists_all_permissions_contains_all_default_permissions(self):
        response = requests.get(
            self.permissions_url(), headers=self.generate_auth_headers()
        )

        expected_permissions = [
            "READ_ALL",
            "WRITE_ALL",
            "READ_ALL_PUBLIC",
            "WRITE_ALL_PUBLIC",
            "READ_ALL_PRIVATE",
            "WRITE_ALL_PRIVATE",
            "READ_DEFAULT_PUBLIC",
            "WRITE_DEFAULT_PUBLIC",
            "READ_DEFAULT_PRIVATE",
            "WRITE_DEFAULT_PRIVATE",
            "DATA_ADMIN",
            "USER_ADMIN",
        ]

        response_json = response.json()
        assert response.status_code == HTTPStatus.OK
        for permission in expected_permissions:
            assert permission in response_json

    def test_lists_subject_permissions(self):
        # Fetch subject_id
        response = requests.get(
            self.subjects_url(),
            headers=self.generate_auth_headers(),
        )
        subjects = response.json()
        subject = [
            subject
            for subject in subjects
            if self.client_name().lower() in subject["subject_name"]
        ][0]

        # Get subject permissions
        response = requests.get(
            f"{self.permissions_url()}/{subject['subject_id']}",
            headers=self.generate_auth_headers(),
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == [
            {
                "id": "USER_ADMIN",
                "type": "USER_ADMIN",
                "sensitivity": None,
                "domain": None,
                "layer": None,
            },
        ]

    def test_list_all_subjects(self):
        response = requests.get(
            self.subjects_url(),
            headers=self.generate_auth_headers(),
        )

        minimum_expected_names = [
            f"{RESOURCE_PREFIX}_ui_test_user",
            f"{RESOURCE_PREFIX}_e2e_test_client_read_and_write",
            f"{RESOURCE_PREFIX}_e2e_test_client_data_admin",
            f"{RESOURCE_PREFIX}_e2e_test_client_write_all",
            f"{RESOURCE_PREFIX}_e2e_test_client_user_admin",
        ]

        assert response.status_code == HTTPStatus.OK
        returned_subject_names = [
            subject["subject_name"] for subject in response.json()
        ]
        assert all(
            [
                expected_name in returned_subject_names
                for expected_name in minimum_expected_names
            ]
        )

    @pytest.mark.order(1)
    def test_create_user(self):
        username_payload = self.generate_username_payload()
        response = requests.post(
            self.user_url(), headers=self.generate_auth_headers(), json=username_payload
        )

        assert response.status_code == HTTPStatus.CREATED
        self.__class__.subject_id = response.json()["user_id"]
        self.__class__.subject_name = response.json()["username"]

    @pytest.mark.order(2)
    def test_list_user(self):
        response = requests.get(
            self.subjects_url(),
            headers=self.generate_auth_headers(),
        )

        user_list = [subject["subject_id"] for subject in response.json()]
        self.subject_id in user_list

    @pytest.mark.order(3)
    def test_delete_user(self):
        username_payload = self.generate_username_payload(self.subject_name)
        response = requests.delete(
            self.user_url(),
            headers=self.generate_auth_headers(),
            data=json.dumps(
                {
                    "username": username_payload["username"],
                    "user_id": self.subject_id,
                }
            ),
        )

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.order(1)
    def test_create_client(self):
        client_payload = self.generate_client_payload()
        response = requests.post(
            self.client_url(),
            headers=self.generate_auth_headers(),
            json=client_payload,
        )
        assert response.status_code == HTTPStatus.CREATED
        self.__class__.client_id = response.json()["client_id"]

    @pytest.mark.order(2)
    def test_list_client(self):
        response = requests.get(
            self.subjects_url(),
            headers=self.generate_auth_headers(),
        )

        user_list = [subject["subject_id"] for subject in response.json()]
        assert self.client_id in user_list

    @pytest.mark.order(3)
    def test_delete_client(self):
        response = requests.delete(
            f"{self.client_url()}/{self.client_id}",
            headers=self.generate_auth_headers(),
        )

        assert response.status_code == HTTPStatus.OK

    def test_invalid_user_email_creation(self):
        username_payload = self.generate_username_payload()
        username_payload["email"] = "invalid!email@fakedomain.com"
        response = requests.post(
            self.user_url(), headers=self.generate_auth_headers(), json=username_payload
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_invalid_user_permissions(self):
        username_payload = self.generate_username_payload()
        username_payload["permissions"] = ["READ_ALL1", "WRITE_DEFAULT_PUBLIC"]
        response = requests.post(
            self.user_url(),
            headers=self.generate_auth_headers(),
            json=username_payload,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_invalid_client_name_creation(self):
        client_payload = self.generate_client_payload()
        client_payload["client_name"] = "[]!@#$%^&*()_test_client"
        response = requests.post(
            self.user_url(), headers=self.generate_auth_headers(), json=client_payload
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_invalid_client_permissions_creation(self):
        client_payload = self.generate_client_payload()
        client_payload["permissions"] = ["READ_ALL1", "WRITE_DEFAULT_PUBLIC"]
        response = requests.post(
            self.user_url(),
            headers=self.generate_auth_headers(),
            json=client_payload,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
