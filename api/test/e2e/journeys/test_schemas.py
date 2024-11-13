from http import HTTPStatus
import requests
from requests import Response
import pytest
from test.e2e.journeys.base_journey import BaseAuthenticatedJourneyTest, SchemaVersion


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

    def get_schema_from_info_endpoint(
        self, layer: str, domain: str, dataset: str
    ) -> dict:
        url = self.info_dataset_url(layer, domain, dataset)
        response = requests.get(
            url,
            headers=self.generate_auth_headers(
                client_name="E2E_TEST_CLIENT_READ_ALL_WRITE_ALL"
            ),
        )
        return response.json()

    def test_uploads_new_schema_version(self):
        schema_v1 = self.read_schema_version(SchemaVersion.V1)
        layer = schema_v1["metadata"]["layer"]
        domain = schema_v1["metadata"]["domain"]
        dataset = schema_v1["metadata"]["dataset"]

        response1 = self.upload_schema(schema_v1)
        assert response1.status_code == HTTPStatus.CREATED
        uploaded_schema = self.get_schema_from_info_endpoint(layer, domain, dataset)
        self.compare_schema(schema_v1, uploaded_schema, override_keys=["version"])

        schema_v2 = self.read_schema_version(SchemaVersion.V2)
        response2 = self.update_schema(schema_v2)
        assert response2.status_code == HTTPStatus.OK

        updated_schema = self.get_schema_from_info_endpoint(layer, domain, dataset)
        self.compare_schema(
            schema_v2, updated_schema, override_keys=["version", "tags"]
        )

    @pytest.mark.parametrize(
        "metadata_key, metadata_value",
        [
            ("layer", "default123"),
            ("sensitivity", "INVALID"),
            ("owners", [{"email": "change_me@email.com"}]),
            ("update_behaviour", "INVALID"),
        ],
    )
    def test_invalid_metadata_upload(self, metadata_key, metadata_value):
        schema_v1 = self.read_schema_version(SchemaVersion.V1)
        schema_v1["metadata"]["dataset"] = "invalid_dataset"
        schema_v1["metadata"][metadata_key] = metadata_value

        response = self.upload_schema(schema_v1)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.parametrize(
        "column_key, column_value",
        [
            ("data_type", "INVALID"),
            ("allow_null", "pretend_boolean"),
        ],
    )
    def test_invalid_column_upload(self, column_key, column_value):
        schema_v1 = self.read_schema_version(SchemaVersion.V1)
        schema_v1["metadata"]["dataset"] = "invalid_dataset"
        schema_v1["columns"][0][column_key] = column_value

        response = self.upload_schema(schema_v1)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_missing_columns_in_schema_upload(self):
        schema_v1 = self.read_schema_version(SchemaVersion.V1)
        schema_v1.pop("columns", None)

        response = self.upload_schema(schema_v1)
        assert response.status_code == HTTPStatus.BAD_REQUEST

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
            self.layer, "PUBLIC", self.e2e_test_domain, self.dataset
        )

        response = requests.post(
            generate_url, headers=self.generate_auth_headers(), files=files
        )

        assert response.status_code == HTTPStatus.OK

        local_schema = self.read_schema_version("generated_schema")
        assert local_schema == response.json()

    def test_generate_schema_with_invalid_data(self):
        files = {
            "file": (
                self.csv_filename,
                self.make_file_invalid(open("./test/e2e/" + self.csv_filename, "rb")),
            )
        }
        generate_url = self.schema_generate_url(
            self.layer, "PUBLIC", self.e2e_test_domain, "test"
        )
        response = requests.post(
            generate_url, headers=self.generate_auth_headers(), files=files
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
