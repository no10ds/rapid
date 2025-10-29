import json

from mock import Mock
import pytest

from rapid import RapidAuth
from rapid.exceptions import AuthenticationErrorException, CannotFindCredentialException


class MockRequestResponse:
    def __init__(self, status_code: int = 200, content=None):
        self.status_code = status_code
        self.content = content


class TestAuth:
    def test_evaluate_inputs_with_value(self, rapid_auth: RapidAuth):
        value = "value"
        result = rapid_auth.evaluate_inputs(value, "ENVIRONMENT_VARIABLE")
        assert result == value

    def test_evaluate_inputs_without_either_value(self, rapid_auth: RapidAuth):
        with pytest.raises(CannotFindCredentialException):
            rapid_auth.evaluate_inputs(None, "ENVIRONMENT_VARIABLE")

    def test_evaluate_inputs_with_environment_variable(
        self, rapid_auth: RapidAuth, monkeypatch
    ):
        name = "ENVIRONMENT_VARIABLE"
        value = "value"
        monkeypatch.setenv(name, value)
        result = rapid_auth.evaluate_inputs(None, name)
        assert result == value

    def test_validate_credentials_success(self, rapid_auth: RapidAuth):
        rapid_auth.request_token = Mock(return_value=MockRequestResponse(200))
        rapid_auth.validate_credentials()
        rapid_auth.request_token.assert_called_once()

    def test_validate_credentials_failure(self, rapid_auth: RapidAuth):
        rapid_auth.request_token = Mock(return_value=MockRequestResponse(401))
        with pytest.raises(AuthenticationErrorException):
            rapid_auth.validate_credentials()
            rapid_auth.request_token.assert_called_once()

    def test_fetch_token(self, rapid_auth: RapidAuth):
        mocked_response = MockRequestResponse(
            content=json.dumps({"access_token": "token"}).encode("utf-8")
        )
        rapid_auth.request_token = Mock(return_value=mocked_response)
        res = rapid_auth.fetch_token()
        assert res == "token"
