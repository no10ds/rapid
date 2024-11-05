import json
from http import HTTPStatus
import os
import requests
from requests import Response
import pandas as pd
from io import StringIO
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr, Or
from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
)
from jinja2 import Template
from strenum import StrEnum
import pytest

from api.common.config.aws import AWS_REGION


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
        cls.delete_dataset("invalid_dataset")

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

    def get_dataset_from_dynamodb(self, layer: str, domain: str, dataset: str) -> dict:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        table = dynamodb.Table(self.dynamo_db_schema_table())
        try:
            response = table.query(
                KeyConditionExpression=Key("PK").eq(f"{layer}/{domain}/{dataset}"),
            )
        except ClientError as e:
            raise e
        return response["Items"]

    def extract_column_names(self, dataset_schema: dict) -> list:
        return [item["name"] for item in dataset_schema[0]["columns"]]

    def test_uploads_new_schema_version(self):
        # Upload initial schema
        schema_v1 = self.read_schema_version(SchemaVersion.V1)
        layer = schema_v1["metadata"]["layer"]
        domain = schema_v1["metadata"]["domain"]
        dataset = schema_v1["metadata"]["dataset"]
        column_names = [column["name"] for column in schema_v1["columns"]]
        response1 = self.upload_schema(schema_v1)

        assert response1.status_code == HTTPStatus.CREATED

        # Verify schema in dynamodb is correct -> No way to query schema via API endpoint
        dataset_schema_v1 = self.get_dataset_from_dynamodb(layer, domain, dataset)

        rapid_schema_column_names_v1 = self.extract_column_names(dataset_schema_v1)
        assert dataset_schema_v1[0]["domain"] == schema_v1["metadata"]["domain"]
        assert dataset_schema_v1[0]["layer"] == schema_v1["metadata"]["layer"]
        assert sorted(column_names) == sorted(rapid_schema_column_names_v1)

        schema_v2 = self.read_schema_version(SchemaVersion.V2)
        response2 = self.update_schema(schema_v2)
        assert response2.status_code == HTTPStatus.OK

        dataset_schema_v2 = self.get_dataset_from_dynamodb(layer, domain, dataset)
        rapid_schema_column_names_v2 = self.extract_column_names(dataset_schema_v2)

        assert dataset_schema_v2[0]["domain"] == schema_v2["metadata"]["domain"]
        assert dataset_schema_v2[0]["layer"] == schema_v2["metadata"]["layer"]
        assert sorted(column_names) == sorted(rapid_schema_column_names_v2)

    def test_invalid_schema_upload(self):
        """
        This test should attempt to upload an invalid schema and assert that the response is rejected
        """
        invalid_metadata = {
            "layer": "default123",
            "sensitivity": "INVALID",
            "owners": [{"email": "change_me@email.com"}],
            "update_behaviour": "INVALID",
        }

        invalid_metadata_status_codes = []
        for k, v in invalid_metadata.items():
            schema_v1 = self.read_schema_version(SchemaVersion.V1)
            schema_v1["metadata"]["dataset"] = "invalid_dataset"
            schema_v1["metadata"][k] = v
            response = self.upload_schema(schema_v1)
            invalid_metadata_status_codes.append(response.status_code)

        assert all(
            status_code == HTTPStatus.BAD_REQUEST
            for status_code in invalid_metadata_status_codes
        )

        invalid_columns = {"data_type": "INVALID", "allow_null": "pretend_boolean"}

        for k, v in invalid_columns.items():
            schema_v1 = self.read_schema_version(SchemaVersion.V1)
            schema_v1["metadata"]["dataset"] = "invalid_dataset"
            schema_v1["columns"][0][k] = v
            response = self.upload_schema(schema_v1)
            assert response.status_code == HTTPStatus.BAD_REQUEST

        # Modify schema to be invalid
        schema_v1 = self.read_schema_version(SchemaVersion.V1)
        schema_v1.pop("columns", None)
        response1 = self.upload_schema(schema_v1)
        assert response1.status_code == HTTPStatus.BAD_REQUEST

    def test_invalid_schema_update(self):
        schema_v2 = self.read_schema_version(SchemaVersion.V2)
        schema_v2.pop("columns", None)
        response2 = self.update_schema(schema_v2)
        assert response2.status_code == HTTPStatus.BAD_REQUEST

    def test_generates_new_schema(self):
        files = {
            "file": (self.csv_filename, open("./test/e2e/" + self.csv_filename, "rb"))
        }
        generate_url = self.schema_generate_url(
            self.layer, "PUBLIC", self.e2e_test_domain, "test"
        )

        response = requests.post(
            generate_url, headers=self.generate_auth_headers(), files=files
        )

        assert response.status_code == HTTPStatus.OK

    def make_file_invalid(self, buffer_obj):
        df = pd.read_csv(buffer_obj)
        df.columns = [""] + list(df.columns[1:])
        output_buffer = StringIO()
        df.to_csv(output_buffer)
        output_buffer.seek(0)
        return output_buffer

    def test_generate_schema_with_invalid_data(self):
        """
        This test should generate a schema with invalid data and assert that the response is rejected - deleting column name here
        """
        files = {
            "file": (
                self.csv_filename,
                self.make_file_invalid(open("./test/e2e/" + self.csv_filename, "rb")),
            )
        }
        generate_url = self.schema_generate_url(
            self.layer, "PUBLIC", self.e2e_test_domain, "test"
        )
        # Modify the file to be invalid
        response = requests.post(
            generate_url, headers=self.generate_auth_headers(), files=files
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
