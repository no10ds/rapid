from abc import ABC

from fastapi.testclient import TestClient

from api.application.services.authorisation.authorisation_service import (
    secure_endpoint,
    secure_dataset_endpoint,
)
from api.entry import app
from test.test_utils import mock_secure_dataset_endpoint, mock_secure_endpoint


class BaseClientTest(ABC):
    client = None

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app, raise_server_exceptions=False)
        app.dependency_overrides[
            secure_dataset_endpoint
        ] = mock_secure_dataset_endpoint()
        app.dependency_overrides[secure_endpoint] = mock_secure_endpoint()

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides[secure_dataset_endpoint] = {}
        app.dependency_overrides[secure_endpoint] = {}
