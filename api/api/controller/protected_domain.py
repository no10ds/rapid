from fastapi import APIRouter, Response
from fastapi import Security
from fastapi import status as http_status

from api.application.services.authorisation.authorisation_service import secure_endpoint
from api.application.services.protected_domain_service import ProtectedDomainService
from api.application.services.subject_service import SubjectService
from api.common.config.auth import Action
from api.common.config.constants import BASE_API_PATH


protected_domain_service = ProtectedDomainService()
subject_service = SubjectService()

protected_domain_router = APIRouter(
    prefix=f"{BASE_API_PATH}/protected_domains",
    tags=["Protected Domains"],
    responses={404: {"description": "Not found"}},
)


@protected_domain_router.post(
    "/{domain}",
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Security(secure_endpoint, scopes=[Action.DATA_ADMIN])],
)
def create_protected_domain(domain: str):
    """
    ## Create protected domain

    Protected domains can be created to restrict access permissions to specific domains

    Use this endpoint to create a new protected domain. After this you can create clients with the permission for this domain and create `PROTECTED` datasets within this domain.


    ### Inputs

    | Parameters       | Usage               | Example values   | Definition                       |
    |------------------|---------------------|------------------|----------------------------------|
    | `domain`         | URL Parameter       | `land`           | The name of the protected domain |

    ### Domain

    The domain name must adhere to the following conditions:

    - Only alphanumeric and underscore `_` characters allowed
    - Start with an alphabetic character

    ### Accepted permissions

    In order to use this endpoint you need the `DATA_ADMIN` permission

    ### Click  `Try it out` to use the endpoint
    """
    protected_domain_service.create_protected_domain_permission(domain)
    return {"details": f"Successfully created protected domain for {domain}"}


@protected_domain_router.get(
    "",
    dependencies=[Security(secure_endpoint, scopes=[Action.DATA_ADMIN])],
)
def list_protected_domains():
    """
    ## List protected domains

    Use this endpoint to list the protected domains that currently exist.

    ### Outputs

    List of protected permissions in json format in the response body:

    ```json
    [
    "land",
    "department"
    ]
    ```
    ### Accepted permissions

    In order to use this endpoint you need the `DATA_ADMIN` permission

    ### Click  `Try it out` to use the endpoint
    """
    return protected_domain_service.list_protected_domains()


@protected_domain_router.delete(
    "/{domain}",
    dependencies=[Security(secure_endpoint, scopes=[Action.DATA_ADMIN])],
)
def delete_protected_domain(domain: str, response: Response):
    """
    ## Delete protected domain

    Use this endpoint to delete a specific protected domain linked to a domain. If there is no protected domain with this name it
    will throw an error, likewise if the protected domain currently contains any datasets it will throw an error as the protected
    domain is not empty.

    When a valid empty protected domain is deleted, a success message will be displayed.

    ### Inputs

    | Parameters       | Usage               | Example values   | Definition                       |
    |------------------|---------------------|------------------|----------------------------------|
    | `domain`         | URL Parameter       | `land`           | The name of the protected domain |

    ### Accepted permissions

    In order to use this endpoint you need the `DATA_ADMIN` permission

    ### Click  `Try it out` to use the endpoint
    """
    subjects_list = [
        subject["subject_id"] for subject in subject_service.list_subjects()
    ]
    protected_domain_service.delete_protected_domain_permission(domain, subjects_list)
    response.status_code = http_status.HTTP_202_ACCEPTED
    return {"details": f"{domain} has been deleted."}
