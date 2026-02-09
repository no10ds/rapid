import os
import urllib.parse
from strenum import StrEnum
from typing import List

from api.common.config.aws import DOMAIN_NAME, RESOURCE_PREFIX, AWS_REGION
from api.common.config.constants import BASE_API_PATH
from api.common.config.layers import Layer

ALL = "ALL"

RAPID_ACCESS_TOKEN = "rat"  # nosec B105
COOKIE_MAX_AGE_IN_SECONDS = 1800  # 30 minutes

DEFAULT_PERMISSION = ["READ_PUBLIC"]

COGNITO_ALLOWED_FLOWS = ["client_credentials"]
COGNITO_RESOURCE_SERVER_ID = f"https://{DOMAIN_NAME}"
COGNITO_USER_POOL_ID = os.environ["COGNITO_USER_POOL_ID"]

ALLOWED_EMAIL_DOMAINS = os.environ["ALLOWED_EMAIL_DOMAINS"]

IDENTITY_PROVIDER_BASE_URL = (
    f"https://{RESOURCE_PREFIX}-auth.auth.{AWS_REGION}.amazoncognito.com"
)

IDENTITY_PROVIDER_TOKEN_URL = f"{IDENTITY_PROVIDER_BASE_URL}/oauth2/token"
IDENTITY_PROVIDER_AUTHORIZATION_URL = f"{IDENTITY_PROVIDER_BASE_URL}/oauth2/authorize"
IDENTITY_PROVIDER_LOGOUT_URL = f"{IDENTITY_PROVIDER_BASE_URL}/logout"

COGNITO_JWKS_URL = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

COGNITO_EXPLICIT_AUTH_FLOWS = [
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_CUSTOM_AUTH",
    "ALLOW_USER_SRP_AUTH",
]

COGNITO_USER_LOGIN_APP_CREDENTIALS_SECRETS_NAME = os.getenv(
    "COGNITO_USER_LOGIN_APP_CREDENTIALS_SECRETS_NAME", "rapid_user_secrets_cognito"
)

COGNITO_LOGOUT_URI = f"https://{DOMAIN_NAME}/login"
COGNITO_REDIRECT_URI = f"https://{DOMAIN_NAME}{BASE_API_PATH}/oauth2/success"
PROTECTED_DOMAIN_SCOPES_PARAMETER_NAME = f"{RESOURCE_PREFIX}_protected_domain_scopes"
PROTECTED_DOMAIN_PERMISSIONS_PARAMETER_NAME = (
    f"{RESOURCE_PREFIX}_protected_domain_permissions"
)


def construct_user_auth_url(client_id: str):
    redirect_uri = urllib.parse.quote_plus(COGNITO_REDIRECT_URI)
    return f"{IDENTITY_PROVIDER_AUTHORIZATION_URL}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}"


def construct_logout_url(client_id: str):
    logout_uri = urllib.parse.quote_plus(COGNITO_LOGOUT_URI)
    return (
        f"{IDENTITY_PROVIDER_LOGOUT_URL}?client_id={client_id}&logout_uri={logout_uri}"
    )


class Action(StrEnum):
    READ = "READ"
    WRITE = "WRITE"
    USER_ADMIN = "USER_ADMIN"
    DATA_ADMIN = "DATA_ADMIN"

    @staticmethod
    def admin_actions() -> List[str]:
        return [Action.USER_ADMIN, Action.DATA_ADMIN]

    @staticmethod
    def data_actions() -> List[str]:
        return [Action.READ, Action.WRITE]


# Classifications
class Sensitivity(StrEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    PROTECTED = "PROTECTED"


# Creates the possible Sensitivity Level Permissions from the existing Layer Enum
SensitivityPermissions = StrEnum(
    "SensitivityPermissions",
    dict([(sensitivity, sensitivity) for sensitivity in [*list(Sensitivity), ALL]]),
)

# Creates the possible Layer Permissions from the existing Layer Enum
LayerPermissions = StrEnum(
    "LayerPermissions",
    dict([(layer.upper(), layer.upper()) for layer in [*list(Layer), ALL]]),
)


class SubjectType(StrEnum):
    CLIENT = "CLIENT"
    USER = "USER"


class PermissionsTableItem(StrEnum):
    SUBJECT = "SUBJECT"
    PERMISSION = "PERMISSION"


class ServiceTableItem(StrEnum):
    JOB = "JOB"
