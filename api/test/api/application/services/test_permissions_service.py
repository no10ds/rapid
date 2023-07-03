from unittest.mock import Mock

from api.application.services.permissions_service import PermissionsService


class TestGetPermissions:
    def setup_method(self):
        self.dynamo_adapter = Mock()
        self.permissions_service = PermissionsService(self.dynamo_adapter)

    def test_get_permissions(self):
        expected_response = ["WRITE_PUBLIC", "READ_PRIVATE", "DATA_ADMIN", "USER_ADMIN"]
        self.dynamo_adapter.get_all_permissions.return_value = [
            "WRITE_PUBLIC",
            "READ_PRIVATE",
            "DATA_ADMIN",
            "USER_ADMIN",
        ]
        actual_response = self.permissions_service.get_permissions()

        self.dynamo_adapter.get_all_permissions.assert_called_once()
        assert actual_response == expected_response


class TestGetSubjectPermissions:
    def setup_method(self):
        self.dynamo_adapter = Mock()
        self.permissions_service = PermissionsService(self.dynamo_adapter)

    def test_get_permissions(self):
        subject_id = "123abc"
        expected_response = ["WRITE_PUBLIC", "READ_PRIVATE", "DATA_ADMIN", "USER_ADMIN"]
        self.dynamo_adapter.get_permissions_for_subject.return_value = expected_response

        actual_response = self.permissions_service.get_subject_permissions(subject_id)

        self.dynamo_adapter.get_permissions_for_subject.assert_called_once_with(
            subject_id
        )
        assert actual_response == expected_response


class TestGetUIPermissions:
    def setup_method(self):
        self.dynamo_adapter = Mock()
        self.permissions_service = PermissionsService(self.dynamo_adapter)

    def test_gets_all_permissions_for_ui(self):
        all_permissions = [
            "WRITE_ALL",
            "WRITE_PUBLIC",
            "WRITE_PRIVATE",
            "READ_PRIVATE",
            "USER_ADMIN",
            "DATA_ADMIN",
            "READ_PROTECTED_SOME_DOMAIN",
            "WRITE_PROTECTED_SOME_DOMAIN",
        ]

        self.dynamo_adapter.get_all_permissions.return_value = all_permissions

        expected = {
            "ADMIN": [
                {
                    "name": "USER_ADMIN",
                    "display_name": "User",
                    "display_name_full": "User admin",
                },
                {
                    "name": "DATA_ADMIN",
                    "display_name": "Data",
                    "display_name_full": "Data admin",
                },
            ],
            "GLOBAL_READ": [
                {
                    "name": "READ_PRIVATE",
                    "display_name": "PRIVATE",
                    "display_name_full": "Read private",
                }
            ],
            "GLOBAL_WRITE": [
                {
                    "name": "WRITE_ALL",
                    "display_name": "ALL",
                    "display_name_full": "Write all",
                },
                {
                    "name": "WRITE_PUBLIC",
                    "display_name": "PUBLIC",
                    "display_name_full": "Write public",
                },
                {
                    "name": "WRITE_PRIVATE",
                    "display_name": "PRIVATE",
                    "display_name_full": "Write private",
                },
            ],
            "PROTECTED_READ": [
                {
                    "name": "READ_PROTECTED_SOME_DOMAIN",
                    "display_name": "Some domain",
                    "display_name_full": "Read protected some domain",
                }
            ],
            "PROTECTED_WRITE": [
                {
                    "name": "WRITE_PROTECTED_SOME_DOMAIN",
                    "display_name": "Some domain",
                    "display_name_full": "Write protected some domain",
                }
            ],
        }

        result = self.permissions_service.get_all_permissions_ui()

        assert result == expected

    def test_gets_user_permissions_for_ui(self):
        all_permissions = [
            "WRITE_ALL",
            "WRITE_PUBLIC",
            "WRITE_PRIVATE",
            "READ_PRIVATE",
            "USER_ADMIN",
            "DATA_ADMIN",
            "READ_PROTECTED_SOME_DOMAIN",
            "WRITE_PROTECTED_SOME_DOMAIN",
        ]

        self.dynamo_adapter.get_all_permissions.return_value = all_permissions

        expected = {
            "ADMIN": [
                {
                    "name": "USER_ADMIN",
                    "display_name": "User",
                    "display_name_full": "User admin",
                },
                {
                    "name": "DATA_ADMIN",
                    "display_name": "Data",
                    "display_name_full": "Data admin",
                },
            ],
            "GLOBAL_READ": [
                {
                    "name": "READ_PRIVATE",
                    "display_name": "PRIVATE",
                    "display_name_full": "Read private",
                }
            ],
            "GLOBAL_WRITE": [
                {
                    "name": "WRITE_ALL",
                    "display_name": "ALL",
                    "display_name_full": "Write all",
                },
                {
                    "name": "WRITE_PUBLIC",
                    "display_name": "PUBLIC",
                    "display_name_full": "Write public",
                },
                {
                    "name": "WRITE_PRIVATE",
                    "display_name": "PRIVATE",
                    "display_name_full": "Write private",
                },
            ],
            "PROTECTED_READ": [
                {
                    "name": "READ_PROTECTED_SOME_DOMAIN",
                    "display_name": "Some domain",
                    "display_name_full": "Read protected some domain",
                }
            ],
            "PROTECTED_WRITE": [
                {
                    "name": "WRITE_PROTECTED_SOME_DOMAIN",
                    "display_name": "Some domain",
                    "display_name_full": "Write protected some domain",
                }
            ],
        }

        result = self.permissions_service.get_all_permissions_ui()

        assert result == expected
