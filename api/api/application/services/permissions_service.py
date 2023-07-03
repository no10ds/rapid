from typing import List, Dict

from api.adapter.dynamodb_adapter import DynamoDBAdapter


class PermissionsService:
    def __init__(self, dynamodb_adapter=DynamoDBAdapter()):
        self.dynamodb_adapter = dynamodb_adapter
        self.ADMIN_SUFFIX = "_ADMIN"
        self.READ_PERMISSIONS = ["READ_ALL", "READ_PUBLIC", "READ_PRIVATE"]
        self.WRITE_PERMISSIONS = ["WRITE_ALL", "WRITE_PUBLIC", "WRITE_PRIVATE"]
        self.READ_PROTECTED_PREFIX = "READ_PROTECTED"
        self.WRITE_PROTECTED_PREFIX = "WRITE_PROTECTED"

    def get_permissions(self):
        return self.dynamodb_adapter.get_all_permissions()

    def get_subject_permissions(self, subject_id: str) -> List[str]:
        return self.dynamodb_adapter.get_permissions_for_subject(subject_id)

    def get_all_permissions_ui(self) -> Dict[str, List[Dict[str, str]]]:
        all_permissions = self.dynamodb_adapter.get_all_permissions()
        return self._ui_permissions_structure(all_permissions)

    def get_user_permissions_ui(
        self, subject_id: str
    ) -> Dict[str, List[Dict[str, str]]]:
        user_permissions = self.dynamodb_adapter.get_permissions_for_subject(subject_id)
        return self._ui_permissions_structure(user_permissions)

    def _ui_permissions_structure(
        self, permissions: List[str]
    ) -> Dict[str, List[Dict[str, str]]]:
        return {
            "ADMIN": [
                self._for_ui(permission)
                for permission in permissions
                if permission.endswith(self.ADMIN_SUFFIX)
            ],
            "GLOBAL_READ": [
                self._for_ui(permission)
                for permission in permissions
                if permission in self.READ_PERMISSIONS
            ],
            "GLOBAL_WRITE": [
                self._for_ui(permission)
                for permission in permissions
                if permission in self.WRITE_PERMISSIONS
            ],
            "PROTECTED_READ": [
                self._for_ui(permission)
                for permission in permissions
                if permission.startswith(self.READ_PROTECTED_PREFIX)
            ],
            "PROTECTED_WRITE": [
                self._for_ui(permission)
                for permission in permissions
                if permission.startswith(self.WRITE_PROTECTED_PREFIX)
            ],
        }

    def _for_ui(self, permission: str):
        return {
            "display_name": self._construct_display_name(permission),
            "display_name_full": self._construct_display_full_name(permission),
            "name": permission,
        }

    def _construct_display_name(self, permission: str) -> str:
        if self.ADMIN_SUFFIX in permission:
            split = permission.split("_")
            return split[0].capitalize()
        if (
            self.READ_PROTECTED_PREFIX in permission
            or self.WRITE_PROTECTED_PREFIX in permission
        ):
            return (
                permission.replace("READ_PROTECTED_", " ")
                .replace("WRITE_PROTECTED_", " ")
                .replace("_", " ")
                .strip()
                .lower()
                .capitalize()
            )
        if permission in self.READ_PERMISSIONS or permission in self.WRITE_PERMISSIONS:
            split = permission.split("_")
            return split[1].upper()
        return permission

    def _construct_display_full_name(self, permission: str) -> str:
        return permission.replace("_", " ").strip().lower().capitalize()
