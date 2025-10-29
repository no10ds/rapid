from unittest.mock import patch

from api.application.services.subject_service import SubjectService
from api.common.custom_exceptions import UserError, AWSServiceError
from api.domain.client import ClientResponse, ClientRequest
from api.common.config.constants import BASE_API_PATH
from test.api.common.controller_test_utils import BaseClientTest


class TestClientCreation(BaseClientTest):
    @patch.object(SubjectService, "create_client")
    def test_returns_client_information_when_valid_request(self, mock_create_client):
        expected_response = ClientResponse(
            client_name="my_client",
            client_id="some-client-id",
            client_secret="some-client-secret",  # pragma: allowlist secret
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )

        mock_create_client.return_value = expected_response

        client_request = ClientRequest(
            client_name="my_client", permissions=["WRITE_PUBLIC", "READ_PRIVATE"]
        )

        response = self.client.post(
            f"{BASE_API_PATH}/client",
            headers={"Authorization": "Bearer test-token"},
            json={
                "client_name": "my_client",
                "permissions": ["WRITE_PUBLIC", "READ_PRIVATE"],
            },
        )

        mock_create_client.assert_called_once_with(client_request)

        assert response.status_code == 201
        assert response.json() == expected_response.model_dump()

    @patch.object(SubjectService, "create_client")
    def test_accepts_empty_permissions(self, mock_create_client):
        expected_response = ClientResponse(
            client_name="my_client",
            client_id="some-client-id",
            client_secret="some-client-secret",  # pragma: allowlist secret
            permissions=["READ_PUBLIC"],
        )

        mock_create_client.return_value = expected_response

        client_request = ClientRequest(
            client_name="my_client", permissions=["READ_PUBLIC"]
        )

        response = self.client.post(
            f"{BASE_API_PATH}/client",
            headers={"Authorization": "Bearer test-token"},
            json={"client_name": "my_client"},
        )

        mock_create_client.assert_called_once_with(client_request)

        assert response.status_code == 201
        assert response.json() == expected_response.model_dump()

    def test_throws_an_exception_when_client_is_empty(self):
        response = self.client.post(
            f"{BASE_API_PATH}/client",
            headers={"Authorization": "Bearer test-token"},
            json={"permissions": ["WRITE_PUBLIC", "READ_PRIVATE"]},
        )

        assert response.status_code == 400
        assert response.json() == {"details": ["client_name -> Field required"]}

    @patch.object(SubjectService, "create_client")
    def test_bad_request_when_invalid_permissions(self, mock_create_client):
        mock_create_client.side_effect = UserError(
            "One or more of the provided permissions do not exist"
        )

        response = self.client.post(
            f"{BASE_API_PATH}/client",
            headers={"Authorization": "Bearer test-token"},
            json={"client_name": "my_client", "permissions": ["INVALID_SCOPE"]},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": "One or more of the provided permissions do not exist"
        }

    @patch.object(SubjectService, "create_client")
    def test_internal_error_when_client_creation_fails(self, mock_create_client):
        mock_create_client.side_effect = AWSServiceError(
            "The client 'my_client' could not be created"
        )

        response = self.client.post(
            f"{BASE_API_PATH}/client",
            headers={"Authorization": "Bearer test-token"},
            json={"client_name": "my_client", "permissions": ["INVALID_SCOPE"]},
        )

        assert response.status_code == 500
        assert response.json() == {
            "details": "The client 'my_client' could not be created"
        }


class TestClientDeletion(BaseClientTest):
    @patch.object(SubjectService, "delete_client")
    def test_returns_client_information_when_valid_request(self, mock_delete_client):
        expected_response = {"details": "The client 'my-client-id' has been deleted"}

        response = self.client.delete(
            f"{BASE_API_PATH}/client/my-client-id",
            headers={"Authorization": "Bearer test-token"},
        )

        mock_delete_client.assert_called_once_with("my-client-id")

        assert response.status_code == 200
        assert response.json() == expected_response

    @patch.object(SubjectService, "delete_client")
    def test_bad_request_when_client_does_not_exist(self, mock_delete_client):
        mock_delete_client.side_effect = UserError(
            "The client 'my-client-id' does not exist cognito"
        )

        response = self.client.delete(
            f"{BASE_API_PATH}/client/my-client-id",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": "The client 'my-client-id' does not exist cognito"
        }

    @patch.object(SubjectService, "delete_client")
    def test_internal_error_when_client_deletion_fails(self, mock_delete_client):
        mock_delete_client.side_effect = AWSServiceError(
            "Something went wrong. Please Contact your administrator."
        )

        response = self.client.delete(
            f"{BASE_API_PATH}/client/my-client-id",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 500
        assert response.json() == {
            "details": "Something went wrong. Please Contact your administrator."
        }
