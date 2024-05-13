from http import HTTPStatus

import requests

from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
    RESOURCE_PREFIX,
)


class TestSubjectJourneys(BaseAuthenticatedJourneyTest):
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

    # TODO: Test the create/delete client flow
    # TODO: Test the create/delete user flow
