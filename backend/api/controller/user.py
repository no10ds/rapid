from fastapi import APIRouter
from fastapi import Security
from fastapi import status as http_status

from api.application.services.authorisation.authorisation_service import secure_endpoint
from api.application.services.subject_service import SubjectService
from api.common.config.auth import Action
from api.common.config.constants import BASE_API_PATH
from api.domain.user import UserRequest, UserDeleteRequest

subject_service = SubjectService()

user_router = APIRouter(
    prefix=f"{BASE_API_PATH}/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)


@user_router.post(
    "",
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Security(secure_endpoint, scopes=[Action.USER_ADMIN])],
)
async def create_user(user_request: UserRequest):
    """
    ### Inputs

    | Parameters       | Usage               | Example values   | Definition                                                                |
    |------------------|---------------------|------------------|---------------------------------------------------------------------------|
    | `User details`   | JSON Request Body   | See below        | The name of the user application to onboard and the granted permissions   |

    ```json
    {
    "username": "john_doe",
    "email": "jhon.doe@email.com",
    "permissions": [
        "READ_ALL",
        "WRITE_PUBLIC"
    ]
    }
    ```

    ### Username

    The username must adhere to the following conditions:

    - Alphanumeric
    - Start with an alphabetic character
    - Can contain any symbol of `. - _ @`
    - Must be between 3 and 128 characters

    #### Permissions you can grant to the user

    Depending on what permission you would like to grant the onboarding user, the relevant permission(s) must be assigned.
    Available choices are:

    - `READ_ALL` - allow user to read any dataset
    - `READ_PUBLIC` - allow user to read any public dataset
    - `READ_PRIVATE` - allow user to read any dataset with sensitivity private or public
    - `READ_PROTECTED_{DOMAIN}` - allow user to read datasets within a specific protected domain
    - `WRITE_ALL` - allow user to write any dataset
    - `WRITE_PUBLIC` - allow user to write any public dataset
    - `WRITE_PRIVATE` - allow user to write any dataset with sensitivity private or public
    - `WRITE_PROTECTED_{DOMAIN}` - allow user to write datasets within a specific protected domain
    - `DATA_ADMIN` - allow user to add a schema for a dataset of any sensitivity
    - `USER_ADMIN` - allow user to add a new user

    The protected domains can be listed [here](#Protected%20Domains/list_protected_domains_protected_domains_get) or created [here](#Protected%20Domains/create_protected_domain_protected_domains__domain__post).

    ### Click  `Try it out` to use the endpoint

    """
    return subject_service.create_user(user_request)


@user_router.delete(
    "",
    status_code=http_status.HTTP_200_OK,
    dependencies=[Security(secure_endpoint, scopes=[Action.USER_ADMIN])],
)
async def delete_user(delete_request: UserDeleteRequest):
    """
    Use this endpoint to delete an existing user.

    ### Inputs

    | Parameters       | Usage               | Example values   | Definition                            |
    |------------------|---------------------|------------------|---------------------------------------|
    | `user details`   | JSON Request Body   | See below        | The name and id of the user to delete |

    ```json
    {
      "username": "John Doe",
      "user_id": "some-uuid-generated-string-asdasd0-2133"
    }
    ```

    ### Accepted permissions

    In order to use this endpoint you need the `USER_ADMIN` permission

    ### Click  `Try it out` to use the endpoint

    """
    subject_service.delete_user(delete_request)
    return {"details": f"The user '{delete_request.username}' has been deleted"}
