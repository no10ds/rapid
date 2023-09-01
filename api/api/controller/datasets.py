import os
from typing import Optional

from fastapi import APIRouter, Request
from fastapi import UploadFile, File, Response, Security
from fastapi import status as http_status
from fastapi import Path as FastApiPath
from pandas import DataFrame
from starlette.responses import PlainTextResponse

from api.adapter.athena_adapter import AthenaAdapter
from api.application.services.authorisation.authorisation_service import (
    secure_dataset_endpoint,
    secure_endpoint,
    get_subject_id,
)
from api.application.services.authorisation.dataset_access_evaluator import (
    DatasetAccessEvaluator,
)
from api.application.services.data_service import DataService

from api.application.services.delete_service import DeleteService
from api.application.services.format_service import FormatService
from api.application.services.schema_service import SchemaService
from api.common.data_handlers import store_file_to_disk
from api.common.utilities import strtobool
from api.common.config.auth import Action
from api.common.config.constants import (
    BASE_API_PATH,
    LOWERCASE_ROUTE_DESCRIPTION,
    LOWERCASE_REGEX,
    VALID_FILE_MIME_TYPES,
    VALID_FILE_EXTENSIONS,
)
from api.common.config.layers import Layer
from api.common.custom_exceptions import (
    SchemaNotFoundError,
    UserError,
    InvalidFileUploadError,
)
from api.common.logger import AppLogger
from api.common.utilities import construct_dataset_metadata
from api.domain.dataset_filters import DatasetFilters
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.schema_metadata import SchemaMetadata
from api.domain.mime_type import MimeType
from api.domain.sql_query import SQLQuery
from api.domain.Jobs.Job import generate_uuid


CATALOG_DISABLED = strtobool(os.environ.get("CATALOG_DISABLED", "False"))

athena_adapter = AthenaAdapter()
data_service = DataService()
delete_service = DeleteService()
schema_service = SchemaService()
data_access_evaluator = DatasetAccessEvaluator()


datasets_router = APIRouter(
    prefix=f"{BASE_API_PATH}/datasets",
    tags=["Datasets"],
    responses={404: {"description": "Not found"}},
)


@datasets_router.post(
    "",
    dependencies=[Security(secure_endpoint, scopes=[Action.READ])],
    status_code=http_status.HTTP_200_OK,
)
async def list_all_datasets(
    request: Request,
    tag_filters: DatasetFilters = DatasetFilters(),
    enriched: Optional[bool] = False,
):
    """
    ## List datasets

    Use this endpoint to retrieve a list of available datasets. You can also filter by the dataset sensitivity level or by
    tags specified on the dataset.

    If you do not specify any filter values, you will retrieve all available datasets.

    You can optionally enrich the information returned, this will include values like `Last Updated Time`, `Description` and `Tags`.

    ### Inputs

    | Parameters    | Required| Usage                                   | Example values                                                                                         | Definition            |
    |---------------|---------|-----------------------------------------|------------------------------------------------------------------------------------------------------- |-----------------------|
    | enriched      | False   | Boolean Query parameter                 | True                                                                                                   | enriches the metadata |
    | query         | False   | JSON Request Body                       | Consult the [docs](https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/usage.md#examples-2)| the filtering query   |

    ### Accepted permissions

    You will always be able to list all available datasets, regardless of their sensitivity level, provided you have
    a `READ` permission, e.g.: `READ_ALL`, `READ_PUBLIC`, `READ_PRIVATE`, `READ_PROTECTED_{DOMAIN}`

    ### Click  `Try it out` to use the endpoint
    """
    subject_id = get_subject_id(request)
    datasets = data_access_evaluator.get_authorised_datasets(
        subject_id, Action.READ, tag_filters
    )

    class EnrichedMetadata(SchemaMetadata):
        last_updated_date: str

    if enriched:
        return [
            EnrichedMetadata(
                **metadata.dict(),
                last_updated_date=data_service.get_last_updated_time(metadata),
            )
            for metadata in datasets
        ]
    else:
        return datasets


if not CATALOG_DISABLED:

    @datasets_router.get(
        "/search/{term}",
        dependencies=[Security(secure_endpoint, scopes=[Action.READ])],
        status_code=http_status.HTTP_200_OK,
        include_in_schema=False,
    )
    async def search_dataset_metadata(term: str):
        return None


@datasets_router.get(
    "/{layer}/{domain}/{dataset}/info",
    dependencies=[Security(secure_dataset_endpoint, scopes=[Action.READ])],
)
async def get_dataset_info(
    layer: Layer,
    dataset: str,
    domain: str = FastApiPath(
        default="", regex=LOWERCASE_REGEX, description=LOWERCASE_ROUTE_DESCRIPTION
    ),
    version: Optional[int] = None,
):
    """
    ## Dataset info

    Use this endpoint to retrieve basic information for specific datasets, if there is no data stored for the dataset and
    error will be thrown.

    When a valid dataset is retrieved the available data will be the schema definition with some extra values such as:

    - number of rows
    - number of columns
    - statistics data for date columns

    ### Inputs

    | Parameters | Required | Usage             | Example values   | Definition            |
    |------------|----------|-------------------|------------------|-----------------------|
    | `layer`    | True     | URL parameter     | `raw`            | layer of the dataset  |
    | `domain`   | True     | URL parameter     | `land`           | domain of the dataset |
    | `dataset`  | True     | URL parameter     | `train_journeys` | dataset title         |
    | `version`  | False    | Query parameter   | `3`              | dataset version       |


    #### Layer

    The set of values that can be specified for layer are sepcific to the instance of rAPId. You can list them at the endpoint `/layers`.

    #### Domain and dataset

    The domain and dataset names must adhere to the following conditions:

    - Only alphanumeric and underscore `_` characters allowed
    - Start with an alphabetic character

    The domain must also be lowercase only.

    ### Accepted permissions

    You will always be able to get info on all available datasets, regardless of their sensitivity level, provided you have
    a `READ` permission, e.g.: `READ_ALL`, `READ_PUBLIC`, `READ_PRIVATE`, `READ_PROTECTED_{DOMAIN}`

    ### Click  `Try it out` to use the endpoint

    """
    return data_service.get_dataset_info(
        construct_dataset_metadata(layer, domain, dataset, version)
    )


@datasets_router.get(
    "/{layer}/{domain}/{dataset}/{version}/files",
    dependencies=[Security(secure_dataset_endpoint, scopes=[Action.READ])],
)
async def list_raw_files(
    layer: Layer,
    dataset: str,
    version: int,
    domain: str = FastApiPath(
        default="", regex=LOWERCASE_REGEX, description=LOWERCASE_ROUTE_DESCRIPTION
    ),
):
    """
    ## List Raw Files

    Use this endpoint to retrieve all raw files linked to a specific layer/domain/dataset/version, if there is no data stored for the
    layer/domain/dataset/version an error will be thrown.

    When a valid domain/dataset/version is retrieved the available raw file uploads will be displayed in list format.

    ### Inputs

    | Parameters    | Required  | Usage                                   | Example values               | Definition            |
    |---------------|-----------|-----------------------------------------|------------------------------|-----------------------|
    | `layer`       | True      | URL parameter                           | `raw`                        | layer of the dataset  |
    | `domain`      | True      | URL parameter                           | `land`                       | domain of the dataset |
    | `dataset`     | True      | URL parameter                           | `train_journeys`             | dataset title         |
    | `version`     | True      | URL parameter                           | `3`                          | dataset version       |

    #### Layer

    The set of values that can be specified for layer are sepcific to the instance of rAPId. You can list them at the endpoint `/layers`.

    #### Domain and dataset

    The domain and dataset names must adhere to the following conditions:

    - Only alphanumeric and underscore `_` characters allowed
    - Start with an alphabetic character

    The domain must also be lowercase only.

    ### Outputs

    List of raw files in json format in the response body:

    ```json
    [
    "2022-01-21T17:12:31-file1.csv",
    "2022-01-24T11:43:28-file2.csv"
    ]
    ```

    ### Accepted permissions

    You will always be able to get info on all available datasets, regardless of their sensitivity level, provided you have
    a `READ` permission, e.g.: `READ_ALL`, `READ_PUBLIC`, `READ_PRIVATE`, `READ_PROTECTED_{DOMAIN}`

    ### Click  `Try it out` to use the endpoint

    """
    raw_files = data_service.list_raw_files(
        DatasetMetadata(layer, domain, dataset, version)
    )
    return raw_files


@datasets_router.delete(
    "/{layer}/{domain}/{dataset}",
    dependencies=[Security(secure_endpoint, scopes=[Action.DATA_ADMIN])],
)
async def delete_dataset(layer: Layer, domain: str, dataset: str, response: Response):
    """
    ## Delete Dataset

    Use this endpoint to delete all the contents linked to a layer/domain/dataset. It deletes the table, raw data, uploaded data
    and all schemas.

    When all valid items in the domain/dataset have been deleted, a success message will be displayed.

    ### Inputs

    | Parameters | Required | Usage         | Example values                  | Definition                    |
    |------------|----------|---------------|---------------------------------|-------------------------------|
    | `layer`    | True     | URL parameter | `raw`                           | layer of the dataset          |
    | `domain`   | True     | URL parameter | `land`                          | domain of the dataset         |
    | `dataset`  | True     | URL parameter | `train_journeys`                | dataset title                 |

    ### Accepted permissions
    In order to use this endpoint you need the DATA_ADMIN permission.

    ### Click `Try it out` to use the endpoint

    """
    delete_service.delete_dataset(DatasetMetadata(layer, domain, dataset))
    response.status_code = http_status.HTTP_202_ACCEPTED
    return {"details": f"{dataset} has been deleted."}


@datasets_router.delete(
    "/{layer}/{domain}/{dataset}/{version}/{filename}",
    dependencies=[Security(secure_dataset_endpoint, scopes=[Action.WRITE])],
)
async def delete_data_file(
    layer: Layer,
    dataset: str,
    version: int,
    filename: str,
    domain: str = FastApiPath(
        default="", regex=LOWERCASE_REGEX, description=LOWERCASE_ROUTE_DESCRIPTION
    ),
):
    """
    ## Delete Data File

    Use this endpoint to delete a specific file linked to a layer/domain/dataset/version. If there is no data stored for the
    layer/domain/dataset/version or the file name is invalid an error will be thrown.

    When a valid file in the layer/domain/dataset/version is deleted, a success message will be displayed.

    ### General structure

    `GET /datasets/{layer}/{domain}/{dataset}/{version}/{filename}`

    ### Inputs

    | Parameters | Required | Usage         | Example values                  | Definition                    |
    |------------|----------|---------------|---------------------------------|-------------------------------|
    | `layer`    | True     | URL parameter | `raw`                           | layer of the dataset          |
    | `domain`   | True     | URL parameter | `land`                          | domain of the dataset         |
    | `dataset`  | True     | URL parameter | `train_journeys`                | dataset title                 |
    | `version`  | True     | URL parameter | `3`                             | dataset version               |
    | `filename` | True     | URL parameter | `2022-01-21T17:12:31-file1.csv` | previously uploaded file name |

    #### Layer

    The set of values that can be specified for layer are sepcific to the instance of rAPId. You can list them at the endpoint `/layers`.

    #### Domain and dataset

    The domain and dataset names must adhere to the following conditions:

    - Only alphanumeric and underscore `_` characters allowed
    - Start with an alphabetic character

    The domain must also be lowercase only.

    ### Accepted permissions
    In order to use this endpoint you need a relevant WRITE permission that matches the dataset sensitivity level,
    e.g.: `WRITE_ALL`, `WRITE_PUBLIC`, `WRITE_PUBLIC`, `WRITE_PROTECTED_{DOMAIN}`

    ### Click  `Try it out` to use the endpoint

    """
    delete_service.delete_dataset_file(
        DatasetMetadata(layer, domain, dataset, version), filename
    )
    return {"details": f"{filename} has been deleted."}


@datasets_router.post(
    "/{layer}/{domain}/{dataset}",
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Security(secure_dataset_endpoint, scopes=[Action.WRITE])],
)
def upload_data(
    layer: Layer,
    dataset: str,
    request: Request,
    response: Response,
    domain: str = FastApiPath(
        default="", regex=LOWERCASE_REGEX, description=LOWERCASE_ROUTE_DESCRIPTION
    ),
    version: Optional[int] = None,
    file: UploadFile = File(...),
):
    """
    ## Upload dataset

    Given a schema has been uploaded you can upload data which matches that schema. Uploading a CSV or Parquet file via this endpoint
    ensures that the data matches the schema and that it is consistent and sanitised. Should any errors be detected during
    upload, these are sent back in the response to facilitate you fixing the issues.

    ### Inputs

    | Parameters | Required | Usage                                   | Example values              | Definition              |
    |------------|----------|-----------------------------------------|-----------------------------|-------------------------|
    | `layer`    | True     | URL parameter                           | `raw`                       | layer of the dataset    |
    | `domain`   | True     | URL parameter                           | `air`                       | domain of the dataset   |
    | `dataset`  | True     | URL parameter                           | `passengers_by_airport`     | dataset title           |
    | `version`  | False    | Query parameter                         | `3`                         | dataset version         |
    | `file`     | True     | File in form data with key value `file` | `passengers_by_airport.csv` | the dataset file itself |

    #### Layer

    The set of values that can be specified for layer are sepcific to the instance of rAPId. You can list them at the endpoint `/layers`.

    #### Domain and dataset

    The domain and dataset names must adhere to the following conditions:

    - Only alphanumeric and underscore `_` characters allowed
    - Start with an alphabetic character

    The domain must also be lowercase only.

    ### Output

    If successful returns file name with a timestamp included, e.g.:

    ```json
    {
    "uploaded": "2022-01-01T13:00:00-passengers_by_airport.csv"
    }
    ```

    ### Accepted permissions

    In order to use this endpoint you need a relevant `WRITE` permission that matches the dataset sensitivity level,
    e.g.: `WRITE_ALL`, `WRITE_PUBLIC`, `WRITE_PRIVATE`, `WRITE_PROTECTED_{DOMAIN}`

    ### Click  `Try it out` to use the endpoint

    """
    try:
        extension = file.filename.split(".")[-1].lower()
        if (
            file.content_type not in VALID_FILE_MIME_TYPES
            and extension not in VALID_FILE_EXTENSIONS
        ):
            raise InvalidFileUploadError(
                f"This file type {extension}, is not supported."
            )

        subject_id = get_subject_id(request)
        job_id = generate_uuid()
        incoming_file_path = store_file_to_disk(extension, job_id, file)
        raw_filename, version, job_id = data_service.upload_dataset(
            subject_id,
            job_id,
            construct_dataset_metadata(layer, domain, dataset, version),
            incoming_file_path,
        )
        response.status_code = http_status.HTTP_202_ACCEPTED
        return {
            "details": {
                "original_filename": incoming_file_path.name,
                "raw_filename": raw_filename,
                "dataset_version": version,
                "status": "Data processing",
                "job_id": job_id,
            }
        }
    except SchemaNotFoundError as error:
        AppLogger.warning("Schema not found: %s", error.args[0])
        raise UserError(message=error.args[0])


@datasets_router.post(
    "/{layer}/{domain}/{dataset}/query",
    dependencies=[Security(secure_dataset_endpoint, scopes=[Action.READ])],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        0: {"col1": "123", "col2": "something", "col3": "500"},
                        1: {"col1": "456", "col2": "something else", "col3": "600"},
                    }
                },
                "text/csv": {
                    "example": 'col1;col2;col3\n"123","something","500"\n"456","something else","600"'
                },
                "application/octet-stream": {},
            }
        }
    },
)
async def query_dataset(
    layer: Layer,
    dataset: str,
    request: Request,
    domain: str = FastApiPath(
        default="", regex=LOWERCASE_REGEX, description=LOWERCASE_ROUTE_DESCRIPTION
    ),
    version: Optional[int] = None,
    query: Optional[SQLQuery] = SQLQuery(),
):
    """
    ## Query dataset

    Data can be queried provided data has been uploaded at some point in the past. Large datasets are not supported by this endpoint.

    ### Inputs

    | Parameters    | Required     | Usage                   | Example values                                                                                                              | Definition                    |
    |---------------|--------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------------------|
    | `layer`       | True         | URL parameter           | `raw`                                                                                                                       | layer of the dataset          |
    | `domain`      | True         | URL parameter           | `space`                                                                                                                     | domain of the dataset         |
    | `dataset`     | True         | URL parameter           | `rocket_launches`                                                                                                           | dataset title                 |
    | `version`     | False        | Query parameter         | '3'                                                                                                                         | dataset version               |
    | `query`       | False        | JSON Request Body       | Consult the [docs](https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/usage.md#how-to-construct-a-query-object)| the query object              |

    #### Layer

    The set of values that can be specified for layer are sepcific to the instance of rAPId. You can list them at the endpoint `/layers`.

    #### Domain and dataset

    The domain and dataset names must adhere to the following conditions:

    - Only alphanumeric and underscore `_` characters allowed
    - Start with an alphabetic character

    The domain must also be lowercase only.

    ### Outputs

    #### JSON

    By default, the result of the query are returned in JSON format where each key represents a row, e.g.:

    ```json
    {
        "0": {
            "column1": "value1",
            "column2": "value2"
        },
        ...
    }
    ```

    #### CSV

    To get a CSV response, the `Accept` Header has to be set to `text/csv`, this can be set below. The response will come as a table, e.g.:

    ```csv
    "","column1","column2"
    0,"value1","value2"
    ...
    ```

    ### Parquet

    To get a Parquet response, the `Accept` Header has to be set to `application/octet-stream`, this can be set below. The response will be the raw Parquet
    binary result.

    We recommend using this in a programmatic sense.

    ### Accepted permissions

    In order to use this endpoint you need a `READ` permission with appropriate sensitivity level permission,
    e.g.: `READ_ALL`, `READ_PUBLIC`, `READ_PRIVATE`, `READ_PROTECTED_{DOMAIN}`

    ### Click  `Try it out` to use the endpoint

    """
    df = data_service.query_data(
        construct_dataset_metadata(layer, domain, dataset, version), query
    )
    string_df = df.astype("string")
    output_format = request.headers.get("Accept")
    mime_type = MimeType.to_mimetype(output_format)
    return _format_query_output(string_df, mime_type)


@datasets_router.post(
    "/{layer}/{domain}/{dataset}/query/large",
    dependencies=[Security(secure_dataset_endpoint, scopes=[Action.READ])],
    status_code=http_status.HTTP_202_ACCEPTED,
)
async def query_large_dataset(
    layer: Layer,
    dataset: str,
    request: Request,
    domain: str = FastApiPath(
        default="", regex=LOWERCASE_REGEX, description=LOWERCASE_ROUTE_DESCRIPTION
    ),
    version: Optional[int] = None,
    query: Optional[SQLQuery] = SQLQuery(),
):
    """
    ## Query large dataset

    Data can be queried provided data has been uploaded at some point in the past.

    This endpoint allows querying datasets larger than 100,000 rows.

    ⚠️ The only download format currently available is `CSV`


    ### Inputs

    | Parameters    | Required     | Usage                   | Example values                                                                                                              | Definition                    |
    |---------------|--------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------------------|
    | `layer`       | True         | URL parameter           | `raw`                                                                                                                       | layer of the dataset          |
    | `domain`      | True         | URL parameter           | `space`                                                                                                                     | domain of the dataset         |
    | `dataset`     | True         | URL parameter           | `rocket_launches`                                                                                                           | dataset title                 |
    | `version`     | False        | Query parameter         | '3'                                                                                                                         | dataset version               |
    | `query`       | False        | JSON Request Body       | Consult the [docs](https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/usage.md#how-to-construct-a-query-object)| the query object              |

    #### Layer

    The set of values that can be specified for layer are sepcific to the instance of rAPId. You can list them at the endpoint `/layers`.

    #### Domain and dataset

    ### Outputs

    Asynchronous Job ID that can be used to track the progress of the query.

    Once the query has completed successfully, you can query the `/jobs/<job-id>` endpoint to retrieve the download URL for the query results

    ### Accepted permissions

    In order to use this endpoint you need a `READ` permission with appropriate sensitivity level permission,
    e.g.: `READ_ALL`, `READ_PUBLIC`, `READ_PRIVATE`, `READ_PROTECTED_{DOMAIN}`

    ### Click  `Try it out` to use the endpoint

    """
    subject_id = get_subject_id(request)
    job_id = data_service.query_large_data(
        subject_id, construct_dataset_metadata(layer, domain, dataset, version), query
    )
    return {"details": {"job_id": job_id}}


def _format_query_output(df: DataFrame, mime_type: MimeType) -> Response:
    formatted_output = FormatService.from_df_to_mimetype(df, mime_type)
    if mime_type in [MimeType.TEXT_CSV, MimeType.BINARY]:
        return PlainTextResponse(status_code=200, content=formatted_output)
    else:
        return formatted_output
