from unittest.mock import Mock, call

import pytest

from api.application.services.protected_domain_service import ProtectedDomainService
from api.common.custom_exceptions import ConflictError, UserError, DomainNotEmptyError
from api.domain.permission_item import PermissionItem
from api.domain.subject_permissions import SubjectPermissions


class TestProtectedDomainService:
    def setup_method(self):
        self.dynamodb_adapter = Mock()
        self.protected_domain_service = ProtectedDomainService(
            self.dynamodb_adapter,
        )

    def test_create_protected_domain_permission(self):
        domain = "domain"
        mock_generated_permissions = [
            PermissionItem(
                id="READ_ALL_PROTECTED_DOMAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="ALL",
            ),
            PermissionItem(
                id="WRITE_ALL_PROTECTED_DOMAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="ALL",
            ),
        ]

        existing_domain_permissions = [
            PermissionItem(
                id="READ_PROTECTED_OTHER",
                type="READ",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_OTHER",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
        ]

        self.protected_domain_service.generate_protected_permission_items = Mock(
            return_value=mock_generated_permissions
        )
        self.dynamodb_adapter.get_all_protected_permissions.return_value = (
            existing_domain_permissions
        )

        self.protected_domain_service.create_protected_domain_permission(domain)

        self.dynamodb_adapter.store_protected_permissions.assert_called_once_with(
            mock_generated_permissions, "DOMAIN"
        )

    def test_generate_protected_permission_items(self):
        expected = [
            PermissionItem(
                id="READ_RAW_PROTECTED_DOMAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="RAW",
            ),
            PermissionItem(
                id="READ_LAYER_PROTECTED_DOMAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="LAYER",
            ),
            PermissionItem(
                id="READ_ALL_PROTECTED_DOMAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="ALL",
            ),
            PermissionItem(
                id="WRITE_RAW_PROTECTED_DOMAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="RAW",
            ),
            PermissionItem(
                id="WRITE_LAYER_PROTECTED_DOMAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="LAYER",
            ),
            PermissionItem(
                id="WRITE_ALL_PROTECTED_DOMAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="ALL",
            ),
        ]

        res = self.protected_domain_service.generate_protected_permission_items(
            "DOMAIN"
        )
        assert res == expected

    def test_create_protected_domain_permission_when_permission_exists_in_db(self):
        existing_domain_permissions = [
            PermissionItem(
                id="READ_PROTECTED_OTHER",
                type="READ",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_OTHER",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
            PermissionItem(
                id="READ_PROTECTED_DOMAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain="DOMAIN",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_DOMAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="DOMAIN",
            ),
        ]
        domain = "domain"

        self.dynamodb_adapter.get_all_protected_permissions.return_value = (
            existing_domain_permissions
        )

        with pytest.raises(
            ConflictError, match=r"The protected domain, \[DOMAIN\] already exists"
        ):
            self.protected_domain_service.create_protected_domain_permission(domain)

    def test_delete_protected_domain_permission(self):
        domain = "other"
        existing_domain_permissions = [
            PermissionItem(
                id="READ_PROTECTED_OTHER",
                type="READ",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_OTHER",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
        ]

        self.dynamodb_adapter.get_all_protected_permissions.return_value = (
            existing_domain_permissions
        )

        self.dynamodb_adapter.get_latest_schemas.return_value = []

        self.protected_domain_service.delete_protected_domain_permission(domain, [])

        self.dynamodb_adapter.delete_permission.assert_has_calls(
            [
                call("READ_RAW_PROTECTED_OTHER"),
                call("READ_LAYER_PROTECTED_OTHER"),
                call("READ_ALL_PROTECTED_OTHER"),
                call("WRITE_RAW_PROTECTED_OTHER"),
                call("WRITE_LAYER_PROTECTED_OTHER"),
                call("WRITE_ALL_PROTECTED_OTHER"),
            ]
        )

    def test_delete_protected_domain_permission_when_user_subject_list_passed(self):
        domain = "other"
        existing_domain_permissions = [
            PermissionItem(
                id="READ_ALL_PROTECTED_OTHER",
                type="READ",
                sensitivity="PROTECTED",
                domain="OTHER",
                layer="ALL",
            ),
            PermissionItem(
                id="WRITE_ALL_PROTECTED_OTHER",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="OTHER",
                layer="ALL",
            ),
        ]

        self.dynamodb_adapter.get_all_protected_permissions.return_value = (
            existing_domain_permissions
        )
        self.dynamodb_adapter.get_permission_keys_for_subject.return_value = [
            "READ_ALL_PROTECTED_OTHER",
            "WRITE_ALL_PROTECTED_OTHER",
            "DATA_ADMIN",
            "USER_ADMIN",
        ]

        self.dynamodb_adapter.get_latest_schemas.return_value = []

        self.protected_domain_service.delete_protected_domain_permission(
            domain, ["xxx-yyy-zzz"]
        )

        self.dynamodb_adapter.delete_permission.assert_has_calls(
            [
                call("READ_RAW_PROTECTED_OTHER"),
                call("READ_LAYER_PROTECTED_OTHER"),
                call("READ_ALL_PROTECTED_OTHER"),
                call("WRITE_RAW_PROTECTED_OTHER"),
                call("WRITE_LAYER_PROTECTED_OTHER"),
                call("WRITE_ALL_PROTECTED_OTHER"),
            ]
        )
        self.dynamodb_adapter.update_subject_permissions.assert_called_once_with(
            subject_permissions=SubjectPermissions(
                subject_id="xxx-yyy-zzz", permissions=["DATA_ADMIN", "USER_ADMIN"]
            )
        )

    def test_delete_protected_domain_permission_when_domain_exists(self):
        domain = "domain"
        existing_domain_permissions = [
            PermissionItem(
                id="READ_PROTECTED_OTHER",
                type="READ",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_OTHER",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
        ]

        self.dynamodb_adapter.get_all_protected_permissions.return_value = (
            existing_domain_permissions
        )

        with pytest.raises(
            UserError, match=r"The protected domain, \[domain]\ does not exist."
        ):
            self.protected_domain_service.delete_protected_domain_permission(domain, [])

    def test_delete_protected_domain_permission_when_domain_not_empty(self):
        domain = "other"
        existing_domain_permissions = [
            PermissionItem(
                id="READ_PROTECTED_OTHER",
                type="READ",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_OTHER",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
        ]

        self.dynamodb_adapter.get_all_protected_permissions.return_value = (
            existing_domain_permissions
        )

        self.dynamodb_adapter.get_latest_schemas.return_value = [
            {"Dataset": "dataset"},
        ]

        with pytest.raises(
            DomainNotEmptyError,
            match=r"Cannot delete protected domain \[other\] as it is not empty. Please delete the datasets \['dataset'\].",
        ):
            self.protected_domain_service.delete_protected_domain_permission(domain, [])

    def test_list_protected_domains_from_db(self):
        expected_response = {"other", "domain"}
        domain_permissions = [
            PermissionItem(
                id="READ_PROTECTED_OTHER",
                type="READ",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_OTHER",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
            PermissionItem(
                id="READ_PROTECTED_DOMAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain="DOMAIN",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_DOMAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="DOMAIN",
            ),
        ]

        self.dynamodb_adapter.get_all_protected_permissions.return_value = (
            domain_permissions
        )

        domains = self.protected_domain_service.list_protected_domains()
        assert domains == expected_response
        self.dynamodb_adapter.get_all_protected_permissions.assert_called_once()

    def test_list_protected_domains(self):
        expected_response = {"other", "domain"}
        domain_permissions = [
            PermissionItem(
                id="READ_PROTECTED_OTHER",
                type="READ",
                sensitivity="PROTECTED",
                domain="OTHER",
            ),
            PermissionItem(
                id="READ_PROTECTED_DOMAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain="DOMAIN",
            ),
        ]
        self.dynamodb_adapter.get_all_protected_permissions.return_value = (
            domain_permissions
        )

        domains = self.protected_domain_service.list_protected_domains()

        assert domains == expected_response
        self.dynamodb_adapter.get_all_protected_permissions.assert_called_once()

    def test_delete_protected_domain(self):
        generated_permissions = [
            PermissionItem(
                id="READ_ALL_PROTECTED_DOMAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="ALL",
            ),
            PermissionItem(
                id="WRITE_ALL_PROTECTED_DOMAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="ALL",
            ),
        ]

        self.dynamodb_adapter.get_all_protected_permissions.return_value = (
            generated_permissions
        )
        self.dynamodb_adapter.get_latest_schemas.return_value = []
        self.dynamodb_adapter.get_permission_keys_for_subject.return_value = [
            "READ_ALL_PROTECTED_DOMAIN",
            "WRITE_ALL_PROTECTED_DOMAIN",
        ]

        self.protected_domain_service.delete_protected_domain_permission(
            "domain", ["xxx-yyy-zzz"]
        )

        self.dynamodb_adapter.delete_permission.assert_has_calls(
            [
                call("READ_RAW_PROTECTED_DOMAIN"),
                call("READ_LAYER_PROTECTED_DOMAIN"),
                call("READ_ALL_PROTECTED_DOMAIN"),
                call("WRITE_RAW_PROTECTED_DOMAIN"),
                call("WRITE_LAYER_PROTECTED_DOMAIN"),
                call("WRITE_ALL_PROTECTED_DOMAIN"),
            ]
        )

        self.dynamodb_adapter.update_subject_permissions.assert_called_once_with(
            subject_permissions=SubjectPermissions(
                subject_id="xxx-yyy-zzz",
                permissions=[],
            )
        )

    def test_delete_protected_domain_that_doesnt_exist(self):
        self.dynamodb_adapter.get_all_protected_permissions.return_value = []
        domain = "domain"

        with pytest.raises(
            UserError, match=r"The protected domain, \[domain\] does not exist"
        ):
            self.protected_domain_service.delete_protected_domain_permission(domain, [])

    def test_delete_protected_domain_that_is_not_empty(self):
        domain = "domain"
        generated_permissions = [
            PermissionItem(
                id="READ_PROTECTED_DOMAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain="DOMAIN",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_DOMAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="DOMAIN",
            ),
        ]
        exisiting_datasets = [
            {"Dataset": "dataset"},
            {"Dataset": "dataset_two"},
        ]

        self.dynamodb_adapter.get_all_protected_permissions.return_value = (
            generated_permissions
        )
        self.dynamodb_adapter.get_latest_schemas.return_value = exisiting_datasets

        with pytest.raises(
            DomainNotEmptyError,
            match=r"Cannot delete protected domain \[domain\] as it is not empty. Please delete the datasets \['dataset', 'dataset_two'\].",
        ):
            self.protected_domain_service.delete_protected_domain_permission(domain, [])

    def test_throws_if_invalid_domain_name(self):
        domain = "bad-domain"
        with pytest.raises(
            UserError,
            match=r"The value set for domain \[BAD-DOMAIN\] can only contain alphanumeric and underscore `_` characters and must start with an alphabetic character",
        ):
            self.protected_domain_service.create_protected_domain_permission(domain)
