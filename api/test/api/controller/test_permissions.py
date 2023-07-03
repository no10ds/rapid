from unittest.mock import patch

from api.application.services.permissions_service import PermissionsService
from api.common.custom_exceptions import AWSServiceError
from api.common.config.constants import BASE_API_PATH
from test.api.common.controller_test_utils import BaseClientTest


class TestListPermissions(BaseClientTest):
    @patch.object(PermissionsService, "get_permissions")
    def test_returns_a_list_of_permissions(self, mock_get_permissions):
        expected_response = ["WRITE_PUBLIC", "READ_PRIVATE", "DATA_ADMIN", "USER_ADMIN"]
        mock_get_permissions.return_value = expected_response

        actual_response = self.client.get(f"{BASE_API_PATH}/permissions")

        mock_get_permissions.assert_called_once()

        assert actual_response.status_code == 200
        assert actual_response.json() == expected_response

    @patch.object(PermissionsService, "get_permissions")
    def test_returns_error_response_when_service_throws_error(
        self, mock_get_permissions
    ):
        mock_get_permissions.side_effect = AWSServiceError(
            "Error fetching permissions, please contact your system administrator"
        )

        actual_response = self.client.get(f"{BASE_API_PATH}/permissions")

        mock_get_permissions.assert_called_once()

        assert actual_response.status_code == 500
        assert actual_response.json() == {
            "details": "Error fetching permissions, please contact your system administrator"
        }


class TestListSubjectPermissions(BaseClientTest):
    @patch.object(PermissionsService, "get_subject_permissions")
    def test_returns_a_list_of_permissions(self, mock_get_subject_permissions):
        expected_response = ["WRITE_PUBLIC", "READ_PRIVATE", "DATA_ADMIN", "USER_ADMIN"]

        mock_get_subject_permissions.return_value = expected_response

        actual_response = self.client.get(f"{BASE_API_PATH}/permissions/123abc")

        mock_get_subject_permissions.assert_called_once_with("123abc")

        assert actual_response.status_code == 200
        assert actual_response.json() == expected_response

    @patch.object(PermissionsService, "get_subject_permissions")
    def test_returns_error_response_when_service_throws_error(
        self, mock_get_subject_permissions
    ):
        mock_get_subject_permissions.side_effect = AWSServiceError(
            "Error fetching permissions, please contact your system administrator"
        )

        actual_response = self.client.get(f"{BASE_API_PATH}/permissions/123abc")

        mock_get_subject_permissions.assert_called_once_with("123abc")

        assert actual_response.status_code == 500
        assert actual_response.json() == {
            "details": "Error fetching permissions, please contact your system administrator"
        }
