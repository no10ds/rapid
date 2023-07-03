from fastapi import APIRouter
from fastapi import status as http_status

from api.application.services.data_service import DataService
from api.common.config.constants import BASE_API_PATH

data_service = DataService()

table_router = APIRouter(
    prefix=f"{BASE_API_PATH}/table_config",
    tags=["table_config"],
    responses={404: {"description": "Not found"}},
)


@table_router.post("", status_code=http_status.HTTP_200_OK, include_in_schema=False)
async def update_table_config(domain: str, dataset: str):
    data_service.update_table_config(domain, dataset)
