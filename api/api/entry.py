from typing import Dict, List
import os

from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException, Security, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_401_UNAUTHORIZED

from api.application.services.authorisation.authorisation_service import (
    get_client_token,
    get_user_token,
    secure_endpoint,
    RAPID_ACCESS_TOKEN,
    user_logged_in,
)
from api.application.services.authorisation.token_utils import parse_token
from api.application.services.permissions_service import PermissionsService
from api.application.services.authorisation.dataset_access_evaluator import (
    DatasetAccessEvaluator,
)
from api.common.config.auth import IDENTITY_PROVIDER_BASE_URL, Action
from api.common.config.docs import custom_openapi_docs_generator, COMMIT_SHA, VERSION
from api.common.config.constants import BASE_API_PATH
from api.common.logger import AppLogger, init_logger
from api.common.custom_exceptions import UserError, AWSServiceError
from api.common.utilities import strtobool
from api.controller.auth import auth_router
from api.controller.client import client_router
from api.controller.datasets import datasets_router
from api.controller.jobs import jobs_router
from api.controller.layers import layers_router
from api.controller.permissions import permissions_router
from api.controller.protected_domain import protected_domain_router
from api.controller.schema import schema_router
from api.controller.subjects import subjects_router
from api.controller.user import user_router
from api.exception_handler import add_exception_handlers

try:
    load_dotenv()
except OSError:
    pass

PROJECT_NAME = os.environ.get("PROJECT_NAME", None)
PROJECT_DESCRIPTION = os.environ.get("PROJECT_DESCRIPTION", None)
PROJECT_URL = os.environ.get("DOMAIN_NAME", None)
PROJECT_CONTACT = os.environ.get("PROJECT_CONTACT", None)
PROJECT_ORGANISATION = os.environ.get("PROJECT_ORGANISATION", None)
CATALOG_DISABLED = strtobool(os.environ.get("CATALOG_DISABLED", "False"))

permissions_service = PermissionsService()
upload_service = DatasetAccessEvaluator()

app = FastAPI(
    openapi_url=f"{BASE_API_PATH}/openapi.json", docs_url=f"{BASE_API_PATH}/docs"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.openapi = custom_openapi_docs_generator(app)
add_exception_handlers(app)
app.include_router(auth_router)
app.include_router(permissions_router)
app.include_router(datasets_router)
app.include_router(schema_router)
app.include_router(client_router)
app.include_router(user_router)
app.include_router(protected_domain_router)
app.include_router(subjects_router)
app.include_router(jobs_router)
app.include_router(layers_router)


@app.on_event("startup")
async def startup_event():
    init_logger()


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    query_params = request.url.include_query_params()
    subject_id = _get_subject_id(request)
    AppLogger.info(
        f"    Request started: {request.method} {query_params} by subject: {subject_id}"
    )
    return await call_next(request)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    _set_security_headers(response)
    return response


@app.get(f"{BASE_API_PATH}/status", tags=["Status"])
def status(request: Request):
    """The endpoint used for service health check"""
    return {
        "status": "deployed",
        "sha": COMMIT_SHA,
        "version": VERSION,
        "root_path": request.scope.get("root_path"),
    }


@app.get(f"{BASE_API_PATH}/apis", tags=["Info"])
def info():
    """The endpoint used for a service information check"""
    if PROJECT_NAME is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Path not found")

    return {
        "api-version": "api.gov.uk/v1alpha",
        "apis": [
            {
                "api-version": "api.gov.uk/v1alpha",
                "data": {
                    "name": PROJECT_NAME,
                    "description": PROJECT_DESCRIPTION,
                    "url": PROJECT_URL,
                    "contact": PROJECT_CONTACT,
                    "organisation": PROJECT_ORGANISATION,
                    "documentation-url": "https://github.com/no10ds/rapid-api",
                },
            }
        ],
    }


@app.get(
    f"{BASE_API_PATH}/auth",
    status_code=HTTP_200_OK,
    include_in_schema=False,
)
async def get_auth(request: Request):
    if user_logged_in(request):
        return {"detail": "success"}
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=str("fail"))


@app.get(
    f"{BASE_API_PATH}/methods",
    status_code=HTTP_200_OK,
    dependencies=[Depends(secure_endpoint)],
    include_in_schema=False,
)
async def methods(request: Request):
    allowed_actions = {}
    error_message = None
    default_error_message = "You have not been granted relevant permissions. Please speak to your system administrator."

    try:
        subject_id = parse_token(request.cookies.get(RAPID_ACCESS_TOKEN)).subject
        subject_permissions = permissions_service.get_subject_permission_keys(
            subject_id
        )
        allowed_actions = _determine_user_ui_actions(subject_permissions)
        if not any([action_allowed for action_allowed in allowed_actions.values()]):
            error_message = default_error_message
    except UserError:
        error_message = default_error_message
    except AWSServiceError as error:
        error_message = error.message

    return {"error_message": error_message, **allowed_actions}


@app.get(
    f"{BASE_API_PATH}/permissions_ui",
    status_code=HTTP_200_OK,
    dependencies=[Security(secure_endpoint, scopes=[Action.USER_ADMIN])],
    include_in_schema=False,
)
async def get_permissions_ui():
    return permissions_service.get_all_permissions_ui()


@app.get(
    f"{BASE_API_PATH}/datasets_ui/{{action}}",
    status_code=HTTP_200_OK,
    dependencies=[Security(secure_endpoint, scopes=[Action.WRITE, Action.READ])],
    include_in_schema=False,
)
async def get_datasets_ui(action: Action, request: Request):
    subject_id = parse_token(request.cookies.get(RAPID_ACCESS_TOKEN)).subject

    datasets = upload_service.get_authorised_datasets(subject_id, action)
    return [dataset.to_dict() for dataset in datasets]


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


def _get_subject_id(request: Request):
    client_token = get_client_token(request)
    user_token = get_user_token(request)
    token = client_token if client_token else user_token
    return parse_token(token).subject if token else "Not an authenticated user"


def _determine_user_ui_actions(subject_permissions: List[str]) -> Dict[str, bool]:
    return {
        "can_manage_users": Action.USER_ADMIN in subject_permissions,
        "can_upload": any(
            (permission.startswith(Action.WRITE) for permission in subject_permissions)
        ),
        "can_download": any(
            (permission.startswith(Action.READ) for permission in subject_permissions)
        ),
        "can_create_schema": any(
            (
                permission.startswith(Action.DATA_ADMIN)
                for permission in subject_permissions
            )
        ),
        "can_search_catalog": False
        if CATALOG_DISABLED
        else any(
            (permission.startswith(Action.READ) for permission in subject_permissions)
        ),
    }


def _set_security_headers(response) -> None:
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' "
        f"{IDENTITY_PROVIDER_BASE_URL}; "
        "script-src 'self' 'unsafe-inline' "
        "cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js; "
        "style-src 'self' "
        "cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css; "
        "img-src 'self' data: "
        "fastapi.tiangolo.com/img/favicon.png;"
    )
    response.headers["Content-Security-Policy-Report-Only"] = "default-src 'self'"
    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000 ; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Referrer-Policy"] = "strict-origin"
