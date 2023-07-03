from unittest.mock import patch, Mock

from api.application.services.protected_domain_service import ProtectedDomainService
from api.application.services.subject_service import SubjectService
from api.common.config.constants import BASE_API_PATH
from test.api.common.controller_test_utils import BaseClientTest


class TestCreateProtectedDomains(BaseClientTest):
    @patch.object(ProtectedDomainService, "create_protected_domain_permission")
    def test_scopes_creation(self, create_protected_domain_permission: Mock):
        response = self.client.post(
            f"{BASE_API_PATH}/protected_domains/new",
            headers={"Authorization": "Bearer test-token"},
        )

        create_protected_domain_permission.assert_called_once_with("new")

        assert response.status_code == 201
        assert response.json() == {
            "details": "Successfully created protected domain for new"
        }


class TestListProtectedDomains(BaseClientTest):
    @patch.object(ProtectedDomainService, "list_protected_domains")
    def test_list_protected_domains(self, list_protected_domains: Mock):
        list_protected_domains.return_value = ["test"]

        response = self.client.get(
            f"{BASE_API_PATH}/protected_domains",
            headers={"Authorization": "Bearer test-token"},
        )

        list_protected_domains.assert_called_once()

        assert response.status_code == 200
        assert response.json() == ["test"]


class TestDeleteProtectedDomains(BaseClientTest):
    @patch.object(ProtectedDomainService, "delete_protected_domain_permission")
    @patch.object(SubjectService, "list_subjects")
    def test_returns_202_when_protected_domain_is_deleted(
        self, mock_list_subjects, mock_delete_protected_domain_permission
    ):
        mock_list_subjects.return_value = [
            {"subject_id": "xxx-yyy-zzz", "type": "USER"},
            {"subject_id": "aaa-bbb-ccc", "type": "CLIENT"},
        ]

        response = self.client.delete(
            f"{BASE_API_PATH}/protected_domains/mydomain",
            headers={"Authorization": "Bearer test-token"},
        )

        mock_delete_protected_domain_permission.assert_called_once_with(
            "mydomain", ["xxx-yyy-zzz", "aaa-bbb-ccc"]
        )

        assert response.status_code == 202
        assert response.json() == {"details": "mydomain has been deleted."}
