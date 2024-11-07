from fastapi import APIRouter
from fastapi import Security
from fastapi import status as http_status

from api.application.services.authorisation.authorisation_service import secure_endpoint
from api.application.services.subject_service import SubjectService
from api.common.config.auth import Action
from api.common.config.constants import BASE_API_PATH
from api.domain.client import ClientRequest

subject_service = SubjectService()

client_router = APIRouter(
    prefix=f"{BASE_API_PATH}/client",
    tags=["Client"],
    responses={404: {"description": "Not found"}},
)


@client_router.post(
    "",
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Security(secure_endpoint, scopes=[Action.USER_ADMIN])],
)
async def create_client(client_request: ClientRequest):
    """
    ### Inputs

    | Parameters       | Usage               | Example values   | Definition                                                                |
    |------------------|---------------------|------------------|---------------------------------------------------------------------------|
    | `client details` | JSON Request Body   | See below        | The name of the client application to onboard and the granted permissions |

    ```json
    {
    "client_name": "department_for_education",
    "permissions": [
        "READ_ALL",
        "WRITE_PUBLIC"
    ]
    }
    ```

    ### Client Name

    The client name must adhere to the following conditions:

    - Alphanumeric
    - Start with an alphabetic character
    - Can contain any symbol of `. - _ @`
    - Must be between 3 and 128 characters

    #### Permissions you can grant to the client

    Depending on what permission you would like to grant the onboarding client, the relevant permission(s) must be assigned.
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
    return subject_service.create_client(client_request)


@client_router.delete(
    "/{client_id}",
    status_code=http_status.HTTP_200_OK,
    dependencies=[Security(secure_endpoint, scopes=[Action.USER_ADMIN])],
)
async def delete_client(client_id: str):
    """
    Use this endpoint to delete an existing client.

    ### Accepted permissions

    In order to use this endpoint you need the `USER_ADMIN` permission

    ### Click  `Try it out` to use the endpoint

    """
    subject_service.delete_client(client_id)
    return {"details": f"The client '{client_id}' has been deleted"}
