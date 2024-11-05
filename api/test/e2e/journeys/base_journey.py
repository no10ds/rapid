from abc import ABC, abstractmethod
import os
from api.common.config.aws import PERMISSIONS_TABLE_SUFFIX
from test.e2e.utils import get_secret, AuthenticationFailedError
from http import HTTPStatus
import requests
from requests.auth import HTTPBasicAuth
import json
from uuid import uuid4
from jinja2 import Template

from api.common.config.constants import CONTENT_ENCODING

DOMAIN_NAME = os.environ["E2E_DOMAIN_NAME"]
RESOURCE_PREFIX = os.environ["E2E_RESOURCE_PREFIX"]
DYNAMO_PERMISSIONS_TABLE_NAME = RESOURCE_PREFIX + PERMISSIONS_TABLE_SUFFIX
FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class BaseJourneyTest(ABC):
    base_url = f"https://{DOMAIN_NAME}/api"
    datasets_endpoint = f"{base_url}/datasets"
    schema_endpoint = f"{base_url}/schema"

    e2e_test_domain = "test_e2e"
    layer = "default"
    data_directory = f"data/{layer}/{e2e_test_domain}"
    raw_data_directory = f"raw_data/{layer}/{e2e_test_domain}"
    schema_directory = f"{FILE_PATH}/schemas"

    csv_filename = "test_journey_file.csv"
    parquet_filename = "test_journey_file.parquet"

    def dynamo_db_schema_table(self) -> str:
        return RESOURCE_PREFIX + "_schema_table"

    def upload_dataset_url(self, layer: str, domain: str, dataset: str) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}"

    def query_dataset_url(
        self, layer: str, domain: str, dataset: str, version: int = 0
    ) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}/query?version={version}"

    def info_dataset_url(
        self, layer: str, domain: str, dataset: str, version: int = 0
    ) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}/info?version={version}"

    def list_dataset_raw_files_url(self, layer: str, domain: str, dataset: str) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}/1/files"

    def create_protected_domain_url(self, domain: str) -> str:
        return f"{self.base_url}/protected_domains/{domain}"

    def list_protected_domain_url(self) -> str:
        return f"{self.base_url}/protected_domains"

    def modify_subjects_permissions_url(self) -> str:
        return f"{self.base_url}/subjects/permissions"

    def delete_data_url(
        self, layer: str, domain: str, dataset: str, raw_filename: str
    ) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}/1/{raw_filename}"

    def permissions_url(self) -> str:
        return f"{self.base_url}/permissions"

    def subjects_url(self) -> str:
        return f"{self.base_url}/subjects"

    def status_url(self) -> str:
        return f"{self.base_url}/status"

    def user_url(self) -> str:
        return f"{self.base_url}/user"

    def client_url(self) -> str:
        return f"{self.base_url}/client"

    def jobs_url(self) -> str:
        return f"{self.base_url}/jobs"

    def list_datasets_url(self) -> str:
        return f"{self.base_url}/datasets"

    def layers_url(self) -> str:
        return f"{self.base_url}/layers"

    def query_large_dataset_url(
        self, layer: str, domain: str, dataset: str, version: int = 0
    ) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}/query/large?version={version}"

    def protected_domain_url(self, domain: str = "test_domain") -> str:
        return f"{self.base_url}/protected_domains/{domain}"

    def schema_url(self) -> str:
        return f"{self.base_url}/schema"

    def schema_generate_url(
        self, layer: str, sensitivity: str, domain: str, dataset: str
    ) -> str:
        return f"{self.schema_url()}/{layer}/{sensitivity}/{domain}/{dataset}/generate"


class BaseAuthenticatedJourneyTest(BaseJourneyTest):
    @abstractmethod
    def client_name(self) -> str:
        pass

    def generate_auth_headers(self, client_name: str = None) -> dict:

        if not client_name:
            client_name = self.client_name()

        # TODO: Can this be cached to reduce the amount of calls?
        token_url = f"https://{DOMAIN_NAME}/api/oauth2/token"
        data_admin_credentials = get_secret(
            secret_name=f"{RESOURCE_PREFIX}_{client_name}"  # pragma: allowlist secret
        )
        cognito_client_id = data_admin_credentials["CLIENT_ID"]
        cognito_client_secret = data_admin_credentials[
            "CLIENT_SECRET"
        ]  # pragma: allowlist secret

        auth = HTTPBasicAuth(cognito_client_id, cognito_client_secret)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "grant_type": "client_credentials",
            "client_id": cognito_client_id,
        }
        response = requests.post(token_url, auth=auth, headers=headers, json=payload)
        if response.status_code != HTTPStatus.OK:
            raise AuthenticationFailedError(f"{response.status_code}")

        token = json.loads(response.content.decode(CONTENT_ENCODING))["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @classmethod
    def generate_schema_name(cls, name: str) -> str:
        return f"{name}_{str(uuid4()).replace('-', '_')}"

    @classmethod
    def create_schema(cls, name: str) -> str:
        dataset = cls.generate_schema_name(name)
        with open(
            os.path.join(cls.schema_directory, f"test_e2e-{name}.json.tpl")
        ) as file:
            template = Template(file.read())
            contents = template.render(name=dataset)

            schema = json.loads(contents)
            response = requests.post(
                cls.schema_endpoint,
                headers=cls.generate_auth_headers(cls, "E2E_TEST_CLIENT_DATA_ADMIN"),
                json=schema,
            )
        assert response.status_code == HTTPStatus.CREATED

        return dataset

    @classmethod
    def delete_dataset(cls, name: str) -> str:
        response = requests.delete(
            cls.upload_dataset_url(cls, cls.layer, cls.e2e_test_domain, name),
            headers=cls.generate_auth_headers(cls, "E2E_TEST_CLIENT_DATA_ADMIN"),
        )
        assert response.status_code == HTTPStatus.ACCEPTED

    @classmethod
    def delete_user(cls, name: str) -> str:
        response = requests.delete(
            cls.username(cls),
            headers=cls.generate_auth_headers(cls, "E2E_TEST_CLIENT_USER_ADMIN"),
        )
        assert response.status_code == HTTPStatus.ACCEPTED
