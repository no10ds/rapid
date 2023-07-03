import os

from fastapi.openapi.utils import get_openapi

VERSION = os.getenv("VERSION", None)
COMMIT_SHA = os.getenv("COMMIT_SHA", None)

RAPID_DESCRIPTION = """
See the full [changelog here](https://github.com/no10ds/rapid-api/blob/main/changelog.md)

## Getting Started [guide](https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/getting_started.md)

### rAPId usage [guide](https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/usage.md)

### Create schema [documentation](https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/schema_creation.md)

### Data Access [documentation](https://github.com/no10ds/rapid-api/blob/master/docs/guides/usage/data_access.md)

"""

RAPID_TAGS = [
    {
        "name": "Datasets",
        "description": "Manage dataset upload and querying.",
    },
    {
        "name": "Schema",
        "description": "Manage schema generation and upload.",
    },
    {
        "name": "Client",
        "description": "Manage clients.",
    },
    {
        "name": "User",
        "description": "Manage users.",
    },
    {
        "name": "Permissions",
        "description": "Manage permissions.",
    },
    {
        "name": "Protected Domains",
        "description": "Manage protected domains",
    },
    {
        "name": "Status",
        "description": "Shows current status of application, version and commit sha.",
    },
    {
        "name": "Info",
        "description": "Shows the project information including description and contact links.",
    },
]


def custom_openapi_docs_generator(app):
    def custom_openapi_docs():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="rAPId",
            version=VERSION if VERSION is not None else "DEV",
            description=RAPID_DESCRIPTION,
            routes=app.routes,
            tags=RAPID_TAGS,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi_docs
