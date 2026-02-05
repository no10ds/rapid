import os

from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html

VERSION = os.getenv("VERSION", None)
COMMIT_SHA = os.getenv("COMMIT_SHA", None)

RAPID_DESCRIPTION = """
See the full [docs here](https://rapid.readthedocs.io/en/latest/)
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


def custom_swagger_ui_html(openapi_url: str, title: str):
    """Generate custom Swagger UI HTML using self-hosted assets"""
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=title,
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico",
    )
