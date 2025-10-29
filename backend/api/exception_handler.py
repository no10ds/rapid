import os
from typing import List

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from api.application.services.authorisation.authorisation_service import (
    CredentialsUnavailableError,
    is_browser_request,
)
from api.common.custom_exceptions import (
    BaseAppException,
    NotAuthorisedToViewPageError,
)
from api.common.logger import AppLogger

templates = Jinja2Templates(directory=(os.path.abspath("templates")))


def add_exception_handlers(app: FastAPI) -> None:
    # Custom handlers
    @app.exception_handler(CredentialsUnavailableError)
    async def user_credentials_missing_handler(request, exc):
        return RedirectResponse(url="/login")

    @app.exception_handler(NotAuthorisedToViewPageError)
    async def not_authorised_to_view_page_handler(request, exc):
        message = "You are not authorised to perform this action."
        status_code = 403

        AppLogger.warning("Unauthorised page access: %s", exc)
        if is_browser_request(request):
            return RedirectResponse(url="/")
        else:
            return JSONResponse(content={"details": message}, status_code=status_code)

    @app.exception_handler(BaseAppException)
    async def base_app_handler(request, exc):
        AppLogger.error("Base app exception caught: %s", exc)
        if is_browser_request(request):
            return templates.TemplateResponse(
                name="error.html",
                context={"request": request, "error_message": exc.message},
            )
        else:
            return JSONResponse(
                content={"details": exc.message}, status_code=exc.status_code
            )

    @app.exception_handler(Exception)
    async def general_handler(request, exc):
        message = "Something went wrong. Please contact your system administrator."
        status_code = 500

        AppLogger.error("Something went wrong: %s", exc)
        if is_browser_request(request):
            return templates.TemplateResponse(
                name="error.html",
                context={"request": request, "error_message": message},
            )
        else:
            return JSONResponse(content={"details": message}, status_code=status_code)

    # Override handlers
    @app.exception_handler(RequestValidationError)
    async def pydantic_error_handler(request, exc: RequestValidationError):
        return JSONResponse(
            content={"details": _generate_pydantic_error_message(exc.errors())},
            status_code=400,
        )

    def _generate_pydantic_error_message(message: dict) -> List[str]:
        PYDANTIC_JSON_DECODE_ERROR = "json_invalid"
        PATH_STR_REGEX_ERROR = "string_pattern_mismatch"
        REGEX_ERROR_MAP = {r"^[a-z0-9_\-]+$": "was required to be lowercase only."}

        error_messages = []
        for error in message:
            if error.get("type") == PYDANTIC_JSON_DECODE_ERROR:
                error_output = error.get("msg")
            elif error.get("type") == PATH_STR_REGEX_ERROR:
                error_pattern = error.get("ctx").get("pattern")
                error_output = _format_error_message_with_location(
                    error, REGEX_ERROR_MAP[error_pattern]
                )
            else:
                error_output = _format_error_message_with_location(error)
            error_messages.append(error_output)
        return error_messages

    def _format_error_message_with_location(error, msg=None):
        location_path = ": ".join([str(item) for item in error.get("loc")[1:]])
        message = error.get("msg") if msg is None else msg
        return f"{location_path} -> {message}"
