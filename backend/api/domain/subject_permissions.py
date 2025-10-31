from typing import Optional, List

from pydantic import BaseModel

from api.common.config.auth import DEFAULT_PERMISSION


class SubjectPermissions(BaseModel):
    subject_id: str
    permissions: Optional[List[str]] = DEFAULT_PERMISSION
