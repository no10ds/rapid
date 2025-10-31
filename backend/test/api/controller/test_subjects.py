from unittest.mock import patch

from api.application.services.subject_service import SubjectService
from api.common.custom_exceptions import AWSServiceError, UserError
from api.domain.subject_permissions import SubjectPermissions
from api.common.config.constants import BASE_API_PATH
from test.api.common.controller_test_utils import BaseClientTest


class TestListSubjects(BaseClientTest):
    @patch("api.controller.subjects.subject_service")
    def test_returns_list_of_all_subjects(self, mock_subject_service):
        expected = [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value1", "key2": "value2"},
        ]

        mock_subject_service.list_subjects.return_value = expected

        response = self.client.get(
            f"{BASE_API_PATH}/subjects", headers={"Authorization": "Bearer test-token"}
        )

        mock_subject_service.list_subjects.assert_called_once()

        assert response.status_code == 200
        assert response.json() == expected

    @patch("api.controller.subjects.subject_service")
    def test_returns_server_error_when_failure_in_aws(self, mock_subject_service):
        mock_subject_service.list_subjects.side_effect = AWSServiceError("The message")

        response = self.client.get(
            f"{BASE_API_PATH}/subjects", headers={"Authorization": "Bearer test-token"}
        )

        mock_subject_service.list_subjects.assert_called_once()

        assert response.status_code == 500
        assert response.json() == {"details": "The message"}


class TestModifySubjectPermissions(BaseClientTest):
    @patch.object(SubjectService, "set_subject_permissions")
    def test_update_subject_permissions(self, mock_set_subject_permissions):
        subject_id = "asdf1243kj456"
        new_permissions = ["READ_ALL", "WRITE_ALL"]

        mock_set_subject_permissions.return_value = {
            "subject_id": subject_id,
            "permissions": new_permissions,
        }

        subject_permissions = SubjectPermissions(
            subject_id=subject_id, permissions=new_permissions
        )

        response = self.client.put(
            f"{BASE_API_PATH}/subjects/permissions",
            headers={"Authorization": "Bearer test-token"},
            json={
                "subject_id": subject_permissions.subject_id,
                "permissions": subject_permissions.permissions,
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "subject_id": subject_permissions.subject_id,
            "permissions": subject_permissions.permissions,
        }
        mock_set_subject_permissions.assert_called_once_with(subject_permissions)

    @patch.object(SubjectService, "set_subject_permissions")
    def test_bad_request_when_invalid_permissions(self, mock_set_subject_permissions):
        mock_set_subject_permissions.side_effect = UserError("Invalid permissions")

        response = self.client.put(
            f"{BASE_API_PATH}/subjects/permissions",
            headers={"Authorization": "Bearer test-token"},
            json={
                "subject_id": "1234",
                "permissions": ["permission1", "permission2"],
            },
        )

        assert response.status_code == 400
        assert response.json() == {"details": "Invalid permissions"}

    @patch.object(SubjectService, "set_subject_permissions")
    def test_internal_error_when_invalid_permissions(
        self, mock_set_subject_permissions
    ):
        mock_set_subject_permissions.side_effect = AWSServiceError("Database error")

        response = self.client.put(
            f"{BASE_API_PATH}/subjects/permissions",
            headers={"Authorization": "Bearer test-token"},
            json={
                "subject_id": "1234",
                "permissions": ["permission1", "permission2"],
            },
        )

        assert response.status_code == 500
        assert response.json() == {"details": "Database error"}
