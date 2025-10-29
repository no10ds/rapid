from typing import Optional, List, Union

from fastapi import Depends, HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security import SecurityScopes
from fastapi.security.utils import get_authorization_scheme_param
from jwt.exceptions import InvalidTokenError, DecodeError
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from api.adapter.s3_adapter import S3Adapter
from api.application.services.authorisation.token_utils import parse_token
from api.application.services.authorisation.dataset_access_evaluator import (
    DatasetAccessEvaluator,
)
from api.application.services.permissions_service import PermissionsService
from api.common.config.auth import (
    IDENTITY_PROVIDER_TOKEN_URL,
    RAPID_ACCESS_TOKEN,
    Action,
)
from api.common.config.layers import Layer
from api.common.custom_exceptions import (
    AuthorisationError,
    CredentialsUnavailableError,
    NotAuthorisedToViewPageError,
    AuthenticationError,
)
from api.common.logger import AppLogger
from api.domain.token import Token
from api.domain.dataset_metadata import DatasetMetadata


class OAuth2ClientCredentials(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str = None,
        allowed_scopes: dict = None,
        auto_error: bool = True,
    ):
        if not allowed_scopes:
            allowed_scopes = {}
        flows = OAuthFlowsModel(
            clientCredentials={"tokenUrl": token_url, "scopes": allowed_scopes}
        )
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        return get_client_token(request)


class OAuth2UserCredentials:
    async def __call__(self, request: Request) -> Optional[str]:
        return get_user_token(request)


oauth2_scheme = OAuth2ClientCredentials(token_url=IDENTITY_PROVIDER_TOKEN_URL)
oauth2_user_scheme = OAuth2UserCredentials()
s3_adapter = S3Adapter()
permission_service = PermissionsService()
dataset_access_evaluator = DatasetAccessEvaluator()


def is_browser_request(request: Request) -> bool:
    accept_type = request.headers.get("Accept")
    return accept_type.startswith("text/html")


def user_logged_in(request: Request) -> bool:
    token = request.cookies.get(RAPID_ACCESS_TOKEN, None)
    return token is not None


def validate_token(
    browser_request: bool = Depends(is_browser_request),
    client_token: Optional[str] = Depends(oauth2_scheme),
    user_token: Optional[str] = Depends(oauth2_user_scheme),
) -> Token:
    check_credentials_availability(browser_request, client_token, user_token)
    token = client_token if client_token else user_token
    return parse_token(token)


def handle_authorisation_error(
    user_token: Optional[str], error: Union[AuthorisationError, InvalidTokenError]
):
    if isinstance(error, InvalidTokenError):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=str(error))
    else:
        if user_token:
            raise NotAuthorisedToViewPageError()
        else:
            raise error


def secure_endpoint(
    security_scopes: SecurityScopes,
    browser_request: bool = Depends(is_browser_request),
    client_token: Optional[str] = Depends(oauth2_scheme),
    user_token: Optional[str] = Depends(oauth2_user_scheme),
):
    try:
        token = validate_token(browser_request, client_token, user_token)
        check_permissions(token.subject, security_scopes.scopes)
    except (InvalidTokenError, AuthorisationError) as error:
        handle_authorisation_error(user_token, error)


def secure_dataset_endpoint(
    security_scopes: SecurityScopes,
    browser_request: bool = Depends(is_browser_request),
    client_token: Optional[str] = Depends(oauth2_scheme),
    user_token: Optional[str] = Depends(oauth2_user_scheme),
    layer: Optional[Layer] = None,
    domain: Optional[str] = None,
    dataset: Optional[str] = None,
):
    try:
        token = validate_token(browser_request, client_token, user_token)
        metadata = process_dataset_metadata(layer, domain, dataset)
        dataset_access_evaluator.can_access_dataset(
            metadata, token.subject, security_scopes.scopes
        )
    except (InvalidTokenError, AuthorisationError) as error:
        handle_authorisation_error(user_token, error)


def process_dataset_metadata(layer, domain, dataset) -> DatasetMetadata:
    if all([layer, domain, dataset]):
        return DatasetMetadata(layer, domain, dataset)
    else:
        AppLogger.info(
            "Cannot retrieve dataset metadata if all values are not provided"
        )
        raise AuthenticationError("You are not authorised to perform this action")


def get_client_token(request: Request) -> Optional[str]:
    authorization: str = request.headers.get("Authorization")
    scheme, jwt_token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        return None
    return jwt_token


def get_user_token(request: Request) -> Optional[str]:
    return request.cookies.get(RAPID_ACCESS_TOKEN, None)


def get_token(request: Request) -> Optional[str]:
    client_token = get_client_token(request)
    user_token = get_user_token(request)
    return client_token if client_token else user_token


def get_subject_id(request: Request):
    token = get_token(request)
    try:
        parsed_token = parse_token(token)
    except DecodeError:
        raise CredentialsUnavailableError("Could not fetch user credentials")
    return parsed_token.subject if token else None


def check_credentials_availability(
    browser_request: bool,
    client_token: Optional[str],
    user_token: Optional[str],
) -> None:
    if not have_credentials(client_token, user_token):
        if browser_request:
            AppLogger.info("Cannot retrieve user credentials if no user token provided")
            raise CredentialsUnavailableError()
        else:
            AppLogger.info(
                "Cannot retrieve client credentials if no client token provided"
            )
            raise AuthenticationError(
                message="You are not authorised to perform this action"
            )


def have_credentials(client_token: str, user_token: str) -> bool:
    return bool(user_token or client_token)


def check_permissions(subject_id: str, endpoint_scopes: List[Action]):
    """
    Ensure that at least one of the endpoint_scopes exists in the users permissions.
    Raising an AuthorisationError if not.
    """
    if not endpoint_scopes:
        return True

    permissions = permission_service.get_subject_permissions(subject_id)
    if any([permission.type in endpoint_scopes for permission in permissions]):
        return True

    raise AuthorisationError(
        f"User {subject_id} does not have permissions that grant access to the endpoint scopes {endpoint_scopes}"
    )
