from unittest.mock import patch

from api.application.services.permissions_service import PermissionsService
from api.common.custom_exceptions import AWSServiceError
from api.common.config.constants import BASE_API_PATH
from api.domain.permission_item import PermissionItem
from test.api.common.controller_test_utils import BaseClientTest


class TestListPermissions(BaseClientTest):
    @patch.object(PermissionsService, "get_permissions")
    def test_returns_a_list_of_permissions(self, mock_get_permissions):
        mock_response = [
            PermissionItem(
                id="DATA_ADMIN",
                type="DATA_ADMIN",
            ),
            PermissionItem(id="READ_ALL", type="READ", layer="ALL", sensitivity="ALL"),
        ]
        expected_response = [
            {
                "id": "DATA_ADMIN",
                "type": "DATA_ADMIN",
                "layer": None,
                "sensitivity": None,
                "domain": None,
            },
            {
                "id": "READ_ALL",
                "type": "READ",
                "layer": "ALL",
                "sensitivity": "ALL",
                "domain": None,
            },
        ]
        mock_get_permissions.return_value = mock_response

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
        mock_response = [
            PermissionItem(
                id="DATA_ADMIN",
                type="DATA_ADMIN",
            ),
            PermissionItem(id="READ_ALL", type="READ", layer="ALL", sensitivity="ALL"),
        ]
        expected_response = [
            {
                "id": "DATA_ADMIN",
                "type": "DATA_ADMIN",
                "layer": None,
                "sensitivity": None,
                "domain": None,
            },
            {
                "id": "READ_ALL",
                "type": "READ",
                "layer": "ALL",
                "sensitivity": "ALL",
                "domain": None,
            },
        ]
        mock_get_subject_permissions.return_value = mock_response

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
