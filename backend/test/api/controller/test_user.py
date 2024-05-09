from unittest.mock import patch

from api.application.services.subject_service import SubjectService
from api.common.custom_exceptions import UserError, AWSServiceError
from api.domain.user import UserResponse, UserRequest, UserDeleteRequest
from api.common.config.constants import BASE_API_PATH
from test.api.common.controller_test_utils import BaseClientTest


class TestUserCreation(BaseClientTest):
    @patch.object(SubjectService, "create_user")
    def test_returns_user_information_when_valid_request(self, mock_create_user):
        expected_response = UserResponse(
            username="user-name",
            email="user-name@some-email.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
            user_id="some-uu-id-b226-e5fd18c59b85",
        )

        mock_create_user.return_value = expected_response

        user_request = UserRequest(
            username="user-name",
            email="user-name@some-email.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )

        response = self.client.post(
            f"{BASE_API_PATH}/user",
            headers={"Authorization": "Bearer test-token"},
            json={
                "username": "user-name",
                "email": "user-name@some-email.com",
                "permissions": ["WRITE_PUBLIC", "READ_PRIVATE"],
            },
        )

        mock_create_user.assert_called_once_with(user_request)

        assert response.status_code == 201
        assert response.json() == expected_response.dict()

    @patch.object(SubjectService, "create_user")
    def test_accepts_empty_permissions_and_uses_default_permissions(
        self, mock_create_user
    ):
        expected_response = UserResponse(
            username="user-name",
            email="user-name@some-email.com",
            permissions=["READ_PUBLIC"],
            user_id="some-uu-id-b226-e5fd18c59b85",
        )

        mock_create_user.return_value = expected_response

        user_request = UserRequest(
            username="user-name",
            email="user-name@some-email.com",
            permissions=["READ_PUBLIC"],
        )

        response = self.client.post(
            f"{BASE_API_PATH}/user",
            headers={"Authorization": "Bearer test-token"},
            json={
                "username": "user-name",
                "email": "user-name@some-email.com",
            },
        )

        mock_create_user.assert_called_once_with(user_request)

        assert response.status_code == 201
        assert response.json() == expected_response.dict()

    def test_throws_an_exception_when_user_is_empty(self):
        response = self.client.post(
            f"{BASE_API_PATH}/user",
            headers={"Authorization": "Bearer test-token"},
            json={"permissions": ["WRITE_PUBLIC", "READ_PRIVATE"]},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": ["username -> field required", "email -> field required"]
        }

    @patch.object(SubjectService, "create_user")
    def test_bad_request_when_invalid_permissions(self, mock_create_user):
        mock_create_user.side_effect = UserError(
            "One or more of the provided permissions do not exist"
        )

        response = self.client.post(
            f"{BASE_API_PATH}/user",
            headers={"Authorization": "Bearer test-token"},
            json={
                "username": "my_user",
                "email": "email@email.com",
                "permissions": ["INVALID_PERMISSION"],
            },
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": "One or more of the provided permissions do not exist"
        }

    @patch.object(SubjectService, "create_user")
    def test_internal_error_when_user_creation_fails(self, mock_create_user):
        mock_create_user.side_effect = AWSServiceError(
            "The user 'my_user' could not be created"
        )

        response = self.client.post(
            f"{BASE_API_PATH}/user",
            headers={"Authorization": "Bearer test-token"},
            json={
                "username": "my_user",
                "email": "email@email.com",
                "permissions": ["INVALID_SCOPE"],
            },
        )

        assert response.status_code == 500
        assert response.json() == {"details": "The user 'my_user' could not be created"}


class TestUserDeletion(BaseClientTest):
    @patch.object(SubjectService, "delete_user")
    def test_returns_user_information_when_valid_request(self, mock_create_user):
        expected_response = {"details": "The user 'my_user' has been deleted"}
        delete_request = UserDeleteRequest(
            username="my_user", user_id="some-uu-id-b226-e5fd18c59b85"
        )

        response = self.client.request(
            method="delete",
            url=f"{BASE_API_PATH}/user",
            headers={"Authorization": "Bearer test-token"},
            json={
                "username": "my_user",
                "user_id": "some-uu-id-b226-e5fd18c59b85",
            },
        )

        mock_create_user.assert_called_once_with(delete_request)

        assert response.status_code == 200
        assert response.json() == expected_response

    @patch.object(SubjectService, "delete_user")
    def test_bad_request_when_user_does_not_exist(self, mock_delete_user):
        mock_delete_user.side_effect = UserError(
            "The user 'my_user' does not exist cognito"
        )

        response = self.client.request(
            method="delete",
            url=f"{BASE_API_PATH}/user",
            headers={"Authorization": "Bearer test-token"},
            json={
                "username": "my_user",
                "user_id": "some-uu-id-b226-e5fd18c59b85",
            },
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": "The user 'my_user' does not exist cognito"
        }

    @patch.object(SubjectService, "delete_user")
    def test_internal_error_when_user_deletion_fails(self, mock_delete_user):
        mock_delete_user.side_effect = AWSServiceError(
            "Something went wrong. Please Contact your administrator."
        )

        response = self.client.request(
            method="delete",
            url=f"{BASE_API_PATH}/user",
            headers={"Authorization": "Bearer test-token"},
            json={
                "username": "my_user",
                "user_id": "some-uu-id-b226-e5fd18c59b85",
            },
        )

        assert response.status_code == 500
        assert response.json() == {
            "details": "Something went wrong. Please Contact your administrator."
        }
