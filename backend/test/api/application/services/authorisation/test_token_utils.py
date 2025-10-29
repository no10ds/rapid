from unittest.mock import patch, Mock

import pytest

from api.application.services.authorisation.token_utils import (
    parse_token,
    get_validated_token_payload,
)


class TestParseToken:
    @patch("api.application.services.authorisation.token_utils.Token")
    @patch(
        "api.application.services.authorisation.token_utils.get_validated_token_payload"
    )
    def test_parses_user_token_with_groups(self, mock_token_payload, mock_token):
        token = "user-token"
        payload = {
            "sub": "the-user-id",
            "cognito:groups": ["group1", "group2"],
            "scope": "scope1 scope2 scope3",
        }
        mock_token_payload.return_value = payload

        parse_token(token)

        mock_token_payload.assert_called_once_with("user-token")
        mock_token.assert_called_once_with(payload)

    @patch("api.application.services.authorisation.token_utils.Token")
    @patch(
        "api.application.services.authorisation.token_utils.get_validated_token_payload"
    )
    def test_parses_client_token_with_scopes(self, mock_token_payload, mock_token):
        token = "client-token"
        payload = {
            "sub": "the-client-id",
        }
        mock_token_payload.return_value = payload

        parse_token(token)

        mock_token_payload.assert_called_once_with("client-token")
        mock_token.assert_called_once_with(payload)

    @patch("api.application.services.authorisation.token_utils.Token")
    @patch(
        "api.application.services.authorisation.token_utils.get_validated_token_payload"
    )
    def test_parses_user_token_with_no_permissions(
        self, mock_token_payload, mock_token
    ):
        token = "user-token"
        payload = {
            "sub": "the-user-id",
            "scope": "scope1 scope2 scope3",
        }
        mock_token_payload.return_value = payload

        parse_token(token)

        mock_token_payload.assert_called_once_with("user-token")
        mock_token.assert_called_once_with(payload)

    @patch("api.application.services.authorisation.token_utils.Token")
    @patch(
        "api.application.services.authorisation.token_utils.get_validated_token_payload"
    )
    def test_passes_errors_through(self, _mock_token_payload, mock_token):
        mock_token.side_effect = ValueError("Error detail")
        with pytest.raises(ValueError, match="Error detail"):
            parse_token("user-token")

    @patch("jwt.decode")
    @patch("api.application.services.authorisation.token_utils.jwks_client")
    def test_extract_token_permissions_for_users(self, mock_jwks_client, mock_decode):
        token = "test-token"
        mock_signing_key = Mock()
        mock_signing_key.key = "secret"
        mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

        mock_decode.return_value = {
            "cognito:groups": ["READ/domain/dataset", "WRITE/domain/dataset"],
            "scope": "phone openid email",
        }

        validated_token_payload = get_validated_token_payload(token)
        mock_jwks_client.get_signing_key_from_jwt.assert_called_once_with(token)
        mock_decode.assert_called_once_with(token, "secret", algorithms=["RS256"])
        assert validated_token_payload == {
            "cognito:groups": ["READ/domain/dataset", "WRITE/domain/dataset"],
            "scope": "phone openid email",
        }
