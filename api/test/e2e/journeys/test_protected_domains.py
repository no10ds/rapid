from functools import reduce
from http import HTTPStatus
from typing import List

import boto3
from boto3.dynamodb.conditions import Key, Attr, Or
from botocore.exceptions import ClientError
import requests
import pytest
from api.common.config.aws import AWS_REGION

from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
    DYNAMO_PERMISSIONS_TABLE_NAME,
    RESOURCE_PREFIX,
)
from test.e2e.utils import get_secret


@pytest.mark.focus
class TestProtectedDomainJourneys(BaseAuthenticatedJourneyTest):
    dataset = None
    cognito_client_id = None

    def client_name(self) -> str:
        return "E2E_TEST_CLIENT_DATA_ADMIN"

    @classmethod
    def setup_class(cls):
        # Fetch cognito client id
        data_admin_credentials = get_secret(
            secret_name=f"{RESOURCE_PREFIX}_E2E_TEST_CLIENT_DATA_ADMIN"  # pragma: allowlist secret
        )
        cls.cognito_client_id = data_admin_credentials["CLIENT_ID"]

        # Create schema
        cls.dataset = cls.create_schema("protected")

        # Upload file
        files = {
            "file": (cls.csv_filename, open("./test/e2e/" + cls.csv_filename, "rb"))
        }
        upload_url = cls.upload_dataset_url(
            cls, cls.layer, "test_e2e_protected", cls.dataset
        )
        response = requests.post(
            upload_url,
            headers=cls.generate_auth_headers(
                cls, "E2E_TEST_CLIENT_READ_ALL_WRITE_ALL"
            ),
            files=files,
        )

        assert response.status_code == HTTPStatus.ACCEPTED

    @classmethod
    def teardown_class(cls):
        """Deletes the protected domain permissions"""
        # Delete the dataset
        response = requests.delete(
            cls.upload_dataset_url(cls, cls.layer, "test_e2e_protected", cls.dataset),
            headers=cls.generate_auth_headers(cls, "E2E_TEST_CLIENT_DATA_ADMIN"),
        )
        assert response.status_code == HTTPStatus.ACCEPTED

    def assume_permissions(self, permissions: List[str]):
        modification_url = self.modify_subjects_permissions_url()
        payload = {
            "subject_id": self.cognito_client_id,
            "permissions": ["USER_ADMIN", "DATA_ADMIN", *permissions],
        }

        response = requests.put(
            modification_url, headers=self.generate_auth_headers(), json=payload
        )
        assert response.status_code == HTTPStatus.OK

    def reset_permissions(self):
        self.assume_permissions([])

    @pytest.mark.order(4)
    def test_create_protected_domain(self):
        self.reset_permissions()
        # Create protected domain
        create_url = self.protected_domain_url("test_e2e")
        response = requests.post(create_url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.CREATED

        # Lists created protected domain
        list_url = self.list_protected_domain_url()
        response = requests.get(list_url, headers=self.generate_auth_headers())
        assert "test_e2e" in response.json()

        # Not authorised to access existing protected domain
        url = self.query_dataset_url(
            layer=self.layer, domain="test_e2e_protected", dataset=self.dataset
        )
        response = requests.post(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.order(5)
    def test_allows_access_to_protected_domain_when_granted_permission(self):
        self.assume_permissions(["READ_DEFAULT_PROTECTED_TEST_E2E_PROTECTED"])

        url = self.query_dataset_url(self.layer, "test_e2e_protected", self.dataset)
        response = requests.post(url, headers=self.generate_auth_headers())

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "0": {
                "year": "2017",
                "month": "7",
                "destination": "Leeds",
                "arrival": "London",
                "type": "regular",
                "status": "completed",
            },
            "1": {
                "year": "2017",
                "month": "7",
                "destination": "Darlington",
                "arrival": "Durham",
                "type": "regular",
                "status": "completed",
            },
        }

        self.reset_permissions()

    @pytest.mark.order(6)
    def test_delete_protected_domain(self):
        # Delete protected domain
        delete_url = self.protected_domain_url("test_e2e")
        response = requests.delete(delete_url, headers=self.generate_auth_headers())
        print("RESPONSE CONTENT", response.content)
        assert response.status_code == HTTPStatus.ACCEPTED

        # Lists protected domain
        list_url = self.list_protected_domain_url()
        response = requests.get(list_url, headers=self.generate_auth_headers())
        assert "test_e2e" not in response.json()
