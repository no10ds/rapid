from fastapi import APIRouter, Security
from fastapi import status as http_status

from api.application.services.authorisation.authorisation_service import secure_endpoint
from api.application.services.permissions_service import PermissionsService
from api.common.config.auth import Action
from api.common.config.constants import BASE_API_PATH

permissions_service = PermissionsService()

permissions_router = APIRouter(
    prefix=f"{BASE_API_PATH}/permissions",
    tags=["Permissions"],
    responses={404: {"description": "Not found"}},
)


@permissions_router.get(
    "",
    status_code=http_status.HTTP_200_OK,
    dependencies=[Security(secure_endpoint, scopes=[Action.USER_ADMIN])],
)
async def get_permissions():
    """
    Use this endpoint to list all available permissions that can be granted to users and clients.

    ### Accepted permissions

    In order to use this endpoint you need the `USER_ADMIN` permission

    ### Click  `Try it out` to use the endpoint
    """
    return permissions_service.get_permissions()


@permissions_router.get(
    "/{subject_id}",
    status_code=http_status.HTTP_200_OK,
    dependencies=[Security(secure_endpoint, scopes=[Action.USER_ADMIN])],
)
async def get_subject_permissions(subject_id: str):
    """
    Use this endpoint to list all permissions that are assigned to a subject.

    ### Accepted permissions

    In order to use this endpoint you need the `USER_ADMIN` permission

    ### Click  `Try it out` to use the endpoint
    """
    return [
        permission.model_dump()
        for permission in permissions_service.get_subject_permissions(subject_id)
    ]
