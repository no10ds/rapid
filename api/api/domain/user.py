import re
from typing import Optional, List
from pydantic import BaseModel

from api.common.config.auth import DEFAULT_PERMISSION, ALLOWED_EMAIL_DOMAINS
from api.common.config.constants import (
    EMAIL_REGEX,
    USERNAME_REGEX,
    CUSTOM_USER_NAME_REGEX,
)
from api.common.custom_exceptions import UserError


class UserRequest(BaseModel):
    username: str
    email: str
    permissions: Optional[List[str]] = DEFAULT_PERMISSION

    def get_validated_username(self):
        """
        We restrict further beyond Cognito limits:
        https://docs.aws.amazon.com/cognito/latest/developerguide/limits.html
        """
        if self.username is not None and re.fullmatch(USERNAME_REGEX, self.username):
            if CUSTOM_USER_NAME_REGEX is None:
                return self.username
            else:
                if re.fullmatch(CUSTOM_USER_NAME_REGEX, self.username):
                    return self.username
                raise UserError(
                    "Your username does not match the requirements specified by your organisation."
                )
        raise UserError(
            "This username is invalid. Please check the username and try again"
        )

    def get_permissions(self) -> List[str]:
        return self.permissions

    def get_validated_email(self):
        if (
            self._is_not_empty()
            and self._is_valid_email()
            and self._has_allowed_domain()
        ):
            return self.email
        raise UserError("Invalid email provided")

    def _is_not_empty(self):
        return self.email is not None

    def _is_valid_email(self):
        email_regex = re.compile(EMAIL_REGEX)
        return re.fullmatch(email_regex, self.email)

    def _has_allowed_domain(self):
        return self.email.split("@")[1] in ALLOWED_EMAIL_DOMAINS


class UserResponse(BaseModel):
    username: str
    email: str
    permissions: List[str]
    user_id: str


class UserDeleteRequest(BaseModel):
    username: str
    user_id: str
