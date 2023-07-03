from dataclasses import dataclass
from unittest.mock import patch, ANY
from starlette.status import HTTP_302_FOUND

from api.common.config.auth import IDENTITY_PROVIDER_TOKEN_URL, COGNITO_REDIRECT_URI
from api.common.config.constants import BASE_API_PATH
from test.api.common.controller_test_utils import BaseClientTest


@dataclass
class MockResponse:
    content: bytes


class TestAuth(BaseClientTest):
    @patch("api.controller.auth.get_secret")
    @patch("api.controller.auth.RedirectResponse")
    @patch("api.controller.auth.requests")
    def test_calls_cognito_for_access_token_when_callback_is_called_with_temporary_code(
        self, mock_requests, mock_redirect, mock_get_secret
    ):
        mock_client_id = "client-id-123"
        temporary_code = "111-222-333-444"

        mock_token_response = MockResponse(b'{"access_token": "A12B3C4D"}')
        mock_get_secret.return_value = {
            "client_id": mock_client_id,
            "client_secret": "client-secret-999",  # pragma: allowlist secret
        }

        mock_requests.post.return_value = mock_token_response

        self.client.get(f"{BASE_API_PATH}/oauth2/success?code={temporary_code}")

        mock_requests.post.assert_called_once_with(
            IDENTITY_PROVIDER_TOKEN_URL,
            auth=ANY,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "client_id": mock_client_id,
                "redirect_uri": COGNITO_REDIRECT_URI,
                "code": temporary_code,
            },
        )
        mock_redirect.assert_called_once_with(url="/", status_code=HTTP_302_FOUND)
