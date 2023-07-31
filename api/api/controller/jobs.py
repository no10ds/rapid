from fastapi import APIRouter
from fastapi import Security
from fastapi import status as http_status
from starlette.requests import Request

from api.application.services.authorisation.authorisation_service import (
    secure_endpoint,
    get_subject_id,
)
from api.application.services.job_service import JobService
from api.common.config.auth import Action
from api.common.config.constants import BASE_API_PATH

jobs_service = JobService()

jobs_router = APIRouter(
    prefix=f"{BASE_API_PATH}/jobs",
    tags=["Jobs"],
    responses={404: {"description": "Not found"}},
)


@jobs_router.get(
    "",
    dependencies=[
        Security(
            secure_endpoint,
            scopes=[Action.READ, Action.WRITE],
        )
    ],
    status_code=http_status.HTTP_200_OK,
)
async def list_all_jobs(request: Request):
    """
    ## List all jobs

    Use this endpoint to retrieve a list of all currently tracked asynchronous processing jobs.

    ### Accepted permissions

    You will always be able to list all 'UPLOAD' jobs, regardless of their sensitivity level, provided you have
    a `READ` permission, e.g.: `READ_ALL`, `READ_PUBLIC`, `READ_PRIVATE`, `READ_PROTECTED_{DOMAIN}`
    or a `WRITE` permission, e.g.: `WRITE_ALL`, `WRITE_PUBLIC`, `WRITE_PRIVATE`, `WRITE_PROTECTED_{DOMAIN}`

    In order to list 'QUERY' jobs you need a relevant `READ` permission that matches the dataset sensitivity level,
    e.g.: `READ_ALL`, `READ_PUBLIC`, `READ_PRIVATE`, `READ_PROTECTED_{DOMAIN}`

    ### Click  `Try it out` to use the endpoint

    """
    return jobs_service.get_all_jobs(get_subject_id(request))


@jobs_router.get(
    "/{job_id}",
    dependencies=[Security(secure_endpoint, scopes=[Action.WRITE])],
    status_code=http_status.HTTP_200_OK,
)
async def get_job(job_id: str):
    """
    ## Get single job

    Use this endpoint to retrieve the status of a tracked asynchronous processing job.

    ### Accepted permissions

    You will always be able to list all jobs, provided you have
    a `WRITE` permission, e.g.: `WRITE_ALL`, `WRITE_PUBLIC`, `WRITE_PRIVATE`, `WRITE_PROTECTED_{DOMAIN}`

    ### Click  `Try it out` to use the endpoint

    """
    return jobs_service.get_job(job_id)
