from dotenv import load_dotenv
from mock import MagicMock, Mock
import pytest

from rapid import Rapid, RapidAuth


load_dotenv()


RAPID_URL = "https://TEST_DOMAIN/api"
RAPID_CLIENT_ID = "1234567890"
RAPID_CLIENT_SECRET = "qwertyuiopasdfghjkl;'"  # nosec
RAPID_TOKEN = "TOKEN"  # nosec


@pytest.fixture
def rapid_auth(requests_mock) -> RapidAuth:
    requests_mock.post(f"{RAPID_URL}/oauth2/token", json={"access_token": RAPID_TOKEN})
    return RapidAuth(
        url=RAPID_URL, client_id=RAPID_CLIENT_ID, client_secret=RAPID_CLIENT_SECRET
    )


@pytest.fixture
def rapid() -> Rapid:
    auth = MagicMock()
    auth.url = RAPID_URL
    auth.fetch_token = Mock(return_value=RAPID_TOKEN)
    return Rapid(auth)
