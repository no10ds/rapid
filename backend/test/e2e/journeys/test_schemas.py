import json
from http import HTTPStatus
import os
import requests
from requests import Response

from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
)
from jinja2 import Template
from strenum import StrEnum


class SchemaVersion(StrEnum):
    V1 = "v1"
    V2 = "v2"


class TestSchemaJourney(BaseAuthenticatedJourneyTest):
    dataset = None

    def client_name(self) -> str:
        return "E2E_TEST_CLIENT_DATA_ADMIN"

    @classmethod
    def setup_class(cls):
        cls.dataset = cls.generate_schema_name("schema")

    @classmethod
    def teardown_class(cls):
        cls.delete_dataset(cls.dataset)

    def read_schema_version(self, version: SchemaVersion) -> dict:
        with open(
            os.path.join(self.schema_directory, f"test_e2e-schema_{version}.json.tpl")
        ) as file:
            template = Template(file.read())
            contents = template.render(name=self.dataset)
            return json.loads(contents)

    def upload_schema(self, schema: dict) -> Response:
        return requests.post(
            self.schema_endpoint,
            headers=self.generate_auth_headers(),
            json=schema,
        )

    def update_schema(self, schema: dict) -> Response:
        return requests.put(
            self.schema_endpoint,
            headers=self.generate_auth_headers(),
            json=schema,
        )

    def test_uploads_new_schema_version(self):
        # Upload initial schema
        schema_v1 = self.read_schema_version(SchemaVersion.V1)
        response1 = self.upload_schema(schema_v1)

        assert response1.status_code == HTTPStatus.CREATED

        # TODO: Later - Verify that initial schema is correct
        # res = requests.get(
        #     self.info_dataset_url(self.layer, self.e2e_test_domain, self.dataset),
        #     headers=self.generate_auth_headers(),
        # )
        # data = res.json()
        # assert data == schema_v1

        schema_v2 = self.read_schema_version(SchemaVersion.V2)
        response2 = self.update_schema(schema_v2)
        assert response2.status_code == HTTPStatus.OK

        # TODO: Some kind of assert that the new schema is the second one
