from fastapi import APIRouter
from fastapi import Security
from fastapi import status as http_status

from api.application.services.authorisation.authorisation_service import secure_endpoint
from api.application.services.subject_service import SubjectService
from api.common.config.auth import Action
from api.common.config.constants import BASE_API_PATH
from api.domain.subject_permissions import SubjectPermissions

subject_service = SubjectService()

subjects_router = APIRouter(
    prefix=f"{BASE_API_PATH}/subjects",
    tags=["Subjects"],
    responses={404: {"description": "Not found"}},
)


@subjects_router.get(
    "",
    status_code=http_status.HTTP_200_OK,
    dependencies=[Security(secure_endpoint, scopes=[Action.USER_ADMIN.value])],
)
async def list_subjects():
    """
    This endpoint lists all user and client apps, returning their username or client app name and their corresponding ID

    ### Click  `Try it out` to use the endpoint

    """
    return subject_service.list_subjects()


@subjects_router.put(
    path="/permissions",
    status_code=http_status.HTTP_200_OK,
    dependencies=[Security(secure_endpoint, scopes=[Action.USER_ADMIN.value])],
)
async def update_subject_permissions(subject_permissions: SubjectPermissions):
    """
    ### Inputs

    | Parameters            | Usage               | Example values   | Definition                                      |
    |-----------------------|---------------------|------------------|-------------------------------------------------|
    | `subject permissions` | JSON Request Body   | See below        | The client ID of whom to change the permissions |

    ```json
    {
            "subject_id": "123abc",
            "permissions": ["READ_ALL", "WRITE_ALL"],
    }
    ```

    #### Permissions you can grant to the client

    Depending on what permission you would like to grant the client, the relevant permission(s) must be provided.
    Note: You must provide the exhaustive set of permissions (both existing and modifications)

    Available choices are:

    - `READ_ALL` - allow client to read any dataset
    - `READ_PUBLIC` - allow client to read any public dataset
    - `READ_PRIVATE` - allow client to read any dataset with sensitivity private or public
    - `READ_PROTECTED_{DOMAIN}` - allow client to read datasets within a specific protected domain
    - `WRITE_ALL` - allow client to write any dataset
    - `WRITE_PUBLIC` - allow client to write any public dataset
    - `WRITE_PRIVATE` - allow client to write any dataset with sensitivity private or public
    - `WRITE_PROTECTED_{DOMAIN}` - allow client to write datasets within a specific protected domain
    - `DATA_ADMIN` - allow client to add a schema for a dataset of any sensitivity
    - `USER_ADMIN` - allow client to add a new client

    The protected domains can be listed [here](#Protected%20Domains/list_protected_domains_protected_domains_get) or created [here](#Protected%20Domains/create_protected_domain_protected_domains__domain__post).

    ### Click  `Try it out` to use the endpoint

    """
    return subject_service.set_subject_permissions(subject_permissions)
