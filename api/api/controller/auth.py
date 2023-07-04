import json
import time
from typing import Dict

import requests
from fastapi import APIRouter, Request
from requests.auth import HTTPBasicAuth
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

from api.application.services.authorisation.authorisation_service import (
    RAPID_ACCESS_TOKEN,
    user_logged_in,
)

from api.common.aws_utilities import get_secret
from api.common.config.auth import (
    IDENTITY_PROVIDER_TOKEN_URL,
    COGNITO_USER_LOGIN_APP_CREDENTIALS_SECRETS_NAME,
    COGNITO_REDIRECT_URI,
    COOKIE_MAX_AGE_IN_SECONDS,
    construct_user_auth_url,
    construct_logout_url,
)
from api.common.config.constants import CONTENT_ENCODING, BASE_API_PATH

auth_router = APIRouter(
    prefix=f"{BASE_API_PATH}/oauth2",
    include_in_schema=False,
    responses={404: {"description": "Not found"}},
)


@auth_router.get("/login")
async def get_login_url(request: Request):
    if user_logged_in(request):
        return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

    cognito_user_login_client_id = get_secret(
        COGNITO_USER_LOGIN_APP_CREDENTIALS_SECRETS_NAME
    )["client_id"]
    user_auth_url = construct_user_auth_url(cognito_user_login_client_id)
    return {"auth_url": user_auth_url}


@auth_router.get("/logout")
async def logout():
    cognito_user_login_client_id = get_secret(
        COGNITO_USER_LOGIN_APP_CREDENTIALS_SECRETS_NAME
    )["client_id"]
    logout_url = construct_logout_url(cognito_user_login_client_id)
    redirect_response = RedirectResponse(url=logout_url, status_code=HTTP_302_FOUND)
    redirect_response.delete_cookie(RAPID_ACCESS_TOKEN)
    # we sleep for just over a second so that the Cloudfront cache has time
    # to clear
    time.sleep(1.2)
    return redirect_response


@auth_router.post("/token")
async def redirect_oauth_token_request(request: Request):
    headers = {
        "authorization": request.headers.get("authorization"),
        "content-type": request.headers.get("content-type"),
    }

    payload = await _load_json_bytes_to_dict(request)

    response = requests.post(
        IDENTITY_PROVIDER_TOKEN_URL, headers=headers, data=payload
    )  # nosec B113

    return response.json()


@auth_router.get("/success")
async def auth_success_callback(code: str):
    (
        cognito_user_login_client_id,
        cognito_user_login_client_secret,
    ) = await _get_client_info()
    auth = HTTPBasicAuth(cognito_user_login_client_id, cognito_user_login_client_secret)

    access_token = await _get_access_token(auth, code, cognito_user_login_client_id)
    auth_response = await _build_auth_redirection(access_token)
    return auth_response


async def _get_client_info():
    user_login_app_secrets = get_secret(COGNITO_USER_LOGIN_APP_CREDENTIALS_SECRETS_NAME)
    cognito_user_login_client_id = user_login_app_secrets["client_id"]
    cognito_user_login_client_secret = user_login_app_secrets["client_secret"]
    return cognito_user_login_client_id, cognito_user_login_client_secret


async def _build_auth_redirection(access_token):
    auth_response = RedirectResponse(url="/", status_code=HTTP_302_FOUND)
    auth_response.set_cookie(
        RAPID_ACCESS_TOKEN,
        access_token,
        max_age=COOKIE_MAX_AGE_IN_SECONDS,
        httponly=True,
        samesite="lax",
        secure=True,
    )
    return auth_response


async def _get_access_token(auth, code, cognito_user_login_client_id):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    payload = {
        "grant_type": "authorization_code",
        "client_id": cognito_user_login_client_id,
        "redirect_uri": COGNITO_REDIRECT_URI,
        "code": code,
    }
    response = requests.post(
        IDENTITY_PROVIDER_TOKEN_URL,
        auth=auth,
        headers=headers,
        data=payload,  # nosec B113
    )
    response_content = json.loads(response.content.decode(CONTENT_ENCODING))
    access_token = response_content["access_token"]
    return access_token


async def _load_json_bytes_to_dict(request) -> Dict:
    body = await request.body()
    body = body.decode(CONTENT_ENCODING)
    return json.loads(body)
