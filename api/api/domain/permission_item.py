from typing import Optional

from pydantic import BaseModel
from api.common.config.auth import Action, LayerPermissions, SensitivityPermisisons


class PermissionItem(BaseModel):
    id: str
    type: Action
    sensitivity: Optional[str] = None
    domain: Optional[str] = None
    layer: Optional[LayerPermissions] = None

    def __hash__(self):
        return hash(self.id)

    def is_protected_permission(self) -> bool:
        return self.sensitivity == SensitivityPermisisons.PROTECTED

    def is_global_data_permission(self) -> bool:
        return self.sensitivity in [
            SensitivityPermisisons.PUBLIC,
            SensitivityPermisisons.PRIVATE,
            SensitivityPermisisons.ALL,
        ]

    def is_admin_permission(self) -> bool:
        return self.type in Action.admin_actions()
