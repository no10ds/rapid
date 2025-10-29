from typing import Any

import jwt
from jwt import PyJWKClient

from api.common.config.auth import (
    COGNITO_JWKS_URL,
)
from api.domain.token import Token

jwks_client = PyJWKClient(COGNITO_JWKS_URL)


def get_validated_token_payload(token: str) -> dict[str, Any]:
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(token, signing_key.key, algorithms=["RS256"])


def parse_token(token: str) -> Token:
    payload = get_validated_token_payload(token)
    return Token(payload)
