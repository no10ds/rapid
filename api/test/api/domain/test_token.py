import pytest

from api.domain.token import Token


@pytest.fixture
def valid_client_token_payload():
    yield {
        "sub": "the-client-subject",
        "scope": "https://example.com/scope1 https://example.com/scope2",
    }


@pytest.fixture
def valid_user_token_payload():
    yield {
        "sub": "the-user-subject",
        "username": "username123",
        "scope": "phone email",
        "cognito:groups": ["group1", "group2"],
    }


class TestSubjectExtraction:
    def test_extract_subject_when_available_and_valid(self, valid_client_token_payload):
        token = Token(valid_client_token_payload)

        assert token.subject == "the-client-subject"

    def test_raises_error_when_no_subject_field(self):
        payload = {}

        with pytest.raises(ValueError):
            Token(payload)

    def test_raises_error_when_subject_field_empty(self):
        payload = {"sub": None}

        with pytest.raises(ValueError):
            Token(payload)
