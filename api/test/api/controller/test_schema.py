from pathlib import Path
from typing import Tuple, Dict
from unittest.mock import patch, ANY

from api.application.services.data_service import DataService
from api.application.services.delete_service import DeleteService
from api.application.services.schema_infer_service import SchemaInferService
from api.common.custom_exceptions import (
    SchemaValidationError,
    ConflictError,
    CrawlerCreationError,
    UserError,
    SchemaNotFoundError,
    CrawlerIsNotReadyError,
    CrawlerUpdateError,
)
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata
from api.common.config.constants import BASE_API_PATH
from test.api.common.controller_test_utils import BaseClientTest


class TestSchemaUpload(BaseClientTest):
    @patch.object(DataService, "upload_schema")
    def test_calls_services_successfully(
        self,
        mock_upload_schema,
    ):
        request_body, expected_schema = self._generate_schema()

        mock_upload_schema.return_value = "some-thing.json"

        response = self.client.post(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        mock_upload_schema.assert_called_once_with(expected_schema)

        assert response.status_code == 201
        assert response.json() == {"details": "some-thing.json"}

    def test_return_400_pydantic_error(self):
        request_body = {
            "metadata": {"tags": {"tag1": "value1", "tag2": "value2"}},
            "columns": [
                {
                    "name": "colname1",
                    "partition_index": None,
                    "data_type": "number",
                    "allow_null": True,
                },
            ],
        }

        response = self.client.post(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": [
                "metadata: domain -> field required",
                "metadata: dataset -> field required",
                "metadata: sensitivity -> field required",
            ]
        }

    @patch.object(DataService, "upload_schema")
    def test_returns_409_when_schema_already_exists(self, mock_upload_schema):
        request_body, expected_schema = self._generate_schema()
        mock_upload_schema.side_effect = ConflictError("Error message")
        response = self.client.post(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 409
        assert response.json() == {"details": "Error message"}

    @patch.object(DataService, "upload_schema")
    def test_returns_400_when_invalid_schema(self, mock_upload_schema):
        request_body, expected_schema = self._generate_schema()
        mock_upload_schema.side_effect = SchemaValidationError("Error message")
        response = self.client.post(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {"details": "Error message"}

    @patch.object(DeleteService, "delete_schema")
    @patch.object(DataService, "upload_schema")
    def test_schema_deletion_returns_500_if_crawler_creation_fails(
        self, mock_upload_schema, mock_delete_schema
    ):
        request_body, _ = self._generate_schema()

        mock_upload_schema.return_value = "some-thing.json"
        mock_upload_schema.side_effect = CrawlerCreationError("Crawler creation error")

        response = self.client.post(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 500
        assert response.json() == {"details": "Crawler creation error"}

        mock_delete_schema.assert_called_once_with("some", "thing", "PUBLIC", None)

    @patch.object(DataService, "upload_schema")
    def test_returns_500_if_protected_domain_does_not_exist(
        self,
        mock_upload_schema,
    ):
        request_body, _ = self._generate_schema()

        mock_upload_schema.side_effect = UserError("Protected domain error")

        response = self.client.post(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {"details": "Protected domain error"}

    def _generate_schema(self) -> Tuple[Dict, Schema]:
        request_body = {
            "metadata": {
                "domain": "some",
                "dataset": "thing",
                "sensitivity": "PUBLIC",
                "version": None,
                "owners": [{"name": "owner", "email": "owner@email.com"}],
                "key_value_tags": {"tag1": "value1", "tag2": "value2"},
                "key_only_tags": ["tag3", "tag4"],
            },
            "columns": [
                {
                    "name": "colname1",
                    "partition_index": None,
                    "data_type": "number",
                    "allow_null": True,
                },
                {
                    "name": "colname2",
                    "partition_index": 0,
                    "data_type": "str",
                    "allow_null": False,
                },
            ],
        }
        expected_schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="thing",
                sensitivity="PUBLIC",
                key_value_tags={"tag1": "value1", "tag2": "value2"},
                key_only_tags=["tag3", "tag4"],
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=None,
                    data_type="number",
                    allow_null=True,
                ),
                Column(
                    name="colname2",
                    partition_index=0,
                    data_type="str",
                    allow_null=False,
                ),
            ],
        )
        return request_body, expected_schema


class TestSchemaUpdate(BaseClientTest):
    @patch.object(DataService, "update_schema")
    def test_calls_services_successfully(
        self,
        mock_update_schema,
    ):
        request_body, expected_schema = self._generate_schema()

        mock_update_schema.return_value = "some-thing.json"

        response = self.client.put(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        mock_update_schema.assert_called_once_with(expected_schema)

        assert response.status_code == 200
        assert response.json() == {"details": "some-thing.json"}

    def test_return_400_when_request_body_invalid(self):
        request_body = {
            "metadata": {"tags": {"tag1": "value1", "tag2": "value2"}},
            "columns": [
                {
                    "name": "colname1",
                    "partition_index": None,
                    "data_type": "number",
                    "allow_null": True,
                },
            ],
        }

        response = self.client.put(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": [
                "metadata: domain -> field required",
                "metadata: dataset -> field required",
                "metadata: sensitivity -> field required",
            ]
        }

    @patch.object(DataService, "update_schema")
    def test_returns_404_when_schema_does_not_exist(self, mock_update_schema):
        request_body, expected_schema = self._generate_schema()
        mock_update_schema.side_effect = SchemaNotFoundError("Error message")
        response = self.client.put(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 404
        assert response.json() == {"details": "Error message"}

    @patch.object(DataService, "update_schema")
    def test_returns_400_when_invalid_schema(self, mock_update_schema):
        request_body, expected_schema = self._generate_schema()
        mock_update_schema.side_effect = SchemaValidationError("Error message")
        response = self.client.put(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {"details": "Error message"}

    @patch.object(DataService, "update_schema")
    def test_schema_deletion_returns_429_if_crawler_is_running(
        self, mock_update_schema
    ):
        request_body, _ = self._generate_schema()

        mock_update_schema.return_value = "some-thing.json"
        mock_update_schema.side_effect = CrawlerIsNotReadyError(
            "Crawler is currently processing"
        )

        response = self.client.put(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 429
        assert response.json() == {"details": "Crawler is currently processing"}

    @patch.object(DataService, "update_schema")
    def test_schema_deletion_returns_500_if_crawler_update_fails(
        self, mock_update_schema
    ):
        request_body, _ = self._generate_schema()

        mock_update_schema.return_value = "some-thing.json"
        mock_update_schema.side_effect = CrawlerUpdateError(
            "Crawler could not be updated"
        )

        response = self.client.put(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 500
        assert response.json() == {"details": "Crawler could not be updated"}

    @patch.object(DataService, "update_schema")
    def test_returns_500_if_protected_domain_does_not_exist(
        self,
        mock_update_schema,
    ):
        request_body, _ = self._generate_schema()

        mock_update_schema.side_effect = UserError("Protected domain error")

        response = self.client.put(
            f"{BASE_API_PATH}/schema",
            json=request_body,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {"details": "Protected domain error"}

    def _generate_schema(self) -> Tuple[Dict, Schema]:
        request_body = {
            "metadata": {
                "domain": "some",
                "dataset": "thing",
                "sensitivity": "PUBLIC",
                "version": None,
                "owners": [{"name": "owner", "email": "owner@email.com"}],
                "key_value_tags": {"tag1": "value1", "tag2": "value2"},
                "key_only_tags": ["tag3", "tag4"],
            },
            "columns": [
                {
                    "name": "colname1",
                    "partition_index": None,
                    "data_type": "number",
                    "allow_null": True,
                },
                {
                    "name": "colname2",
                    "partition_index": 0,
                    "data_type": "str",
                    "allow_null": False,
                },
            ],
        }
        expected_schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="thing",
                sensitivity="PUBLIC",
                key_value_tags={"tag1": "value1", "tag2": "value2"},
                key_only_tags=["tag3", "tag4"],
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=None,
                    data_type="number",
                    allow_null=True,
                ),
                Column(
                    name="colname2",
                    partition_index=0,
                    data_type="str",
                    allow_null=False,
                ),
            ],
        )
        return request_body, expected_schema


class TestSchemaGeneration(BaseClientTest):
    @patch.object(SchemaInferService, "infer_schema")
    @patch("api.controller.schema.store_file_to_disk")
    @patch("api.controller.schema.generate_uuid")
    def test_returns_schema_from_a_csv_file(
        self, mock_generate_uuid, mock_store_file_to_disk, mock_infer_schema
    ):
        expected_response = Schema(
            metadata=SchemaMetadata(
                domain="mydomain",
                dataset="mydataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=None,
                    data_type="object",
                    allow_null=True,
                    format=None,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="Int64",
                    allow_null=True,
                    format=None,
                ),
            ],
        )
        file_content = b"colname1,colname2\nsomething,123\notherthing,456\n\n"
        file_name = "filename.csv"
        job_id = "abc-123"
        incoming_file_path = Path(file_name)
        mock_generate_uuid.return_value = job_id
        mock_store_file_to_disk.return_value = incoming_file_path
        mock_infer_schema.return_value = expected_response

        response = self.client.post(
            f"{BASE_API_PATH}/schema/PUBLIC/mydomain/mydataset/generate",
            files={"file": (file_name, file_content, "text/csv")},
            headers={"Authorization": "Bearer test-token"},
        )
        mock_infer_schema.assert_called_once_with(
            "mydomain", "mydataset", "PUBLIC", incoming_file_path
        )
        mock_store_file_to_disk.assert_called_once_with(
            "csv", job_id, ANY, to_chunk=True
        )

        assert response.status_code == 200
        assert response.json() == expected_response

    @patch.object(SchemaInferService, "infer_schema")
    @patch("api.controller.schema.store_file_to_disk")
    @patch("api.controller.schema.generate_uuid")
    def test_returns_schema_from_a_parquet_file(
        self, mock_generate_uuid, mock_store_file_to_disk, mock_infer_schema
    ):
        expected_response = Schema(
            metadata=SchemaMetadata(
                domain="mydomain",
                dataset="mydataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=None,
                    data_type="object",
                    allow_null=True,
                    format=None,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="Int64",
                    allow_null=True,
                    format=None,
                ),
            ],
        )
        file_content = b"colname1,colname2\nsomething,123\notherthing,456\n\n"
        file_name = "filename.parquet"
        job_id = "abc-123"
        incoming_file_path = Path(file_name)
        mock_generate_uuid.return_value = job_id
        mock_store_file_to_disk.return_value = incoming_file_path
        mock_infer_schema.return_value = expected_response

        response = self.client.post(
            f"{BASE_API_PATH}/schema/PUBLIC/mydomain/mydataset/generate",
            files={"file": (file_name, file_content, "application/octest-stream")},
            headers={"Authorization": "Bearer test-token"},
        )
        mock_infer_schema.assert_called_once_with(
            "mydomain", "mydataset", "PUBLIC", incoming_file_path
        )
        mock_store_file_to_disk.assert_called_once_with(
            "parquet", job_id, ANY, to_chunk=True
        )

        assert response.status_code == 200
        assert response.json() == expected_response

    def test_bad_request_when_filetype_is_invalid(self):
        file_content = b"some content"
        file_name = "filename.txt"

        response = self.client.post(
            f"{BASE_API_PATH}/schema/PUBLIC/mydomain/mydataset/generate",
            files={"file": (file_name, file_content, "text/plain")},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {"details": "This file type txt, is not supported."}

    @patch.object(SchemaInferService, "infer_schema")
    @patch("api.controller.schema.store_file_to_disk")
    @patch("api.controller.schema.generate_uuid")
    def test_bad_request_when_schema_is_invalid(
        self, mock_generate_uuid, mock_store_file_to_disk, mock_infer_schema
    ):
        file_content = b"colname1,colname2\nsomething,123\notherthing,456\n\n"
        file_name = "filename.csv"
        job_id = "abc-123"
        incoming_file_path = Path(file_name)
        mock_generate_uuid.return_value = job_id
        mock_store_file_to_disk.return_value = incoming_file_path
        error_message = "The schema is wrong"
        mock_infer_schema.side_effect = SchemaValidationError(error_message)

        response = self.client.post(
            f"{BASE_API_PATH}/schema/PUBLIC/mydomain/mydataset/generate",
            files={"file": (file_name, file_content, "text/csv")},
            headers={"Authorization": "Bearer test-token"},
        )
        mock_infer_schema.assert_called_once_with(
            "mydomain", "mydataset", "PUBLIC", incoming_file_path
        )
        mock_store_file_to_disk.assert_called_once_with(
            "csv", job_id, ANY, to_chunk=True
        )

        assert response.status_code == 400
        assert response.json() == {"details": error_message}

    def test_returns_error_response_when_domain_uppercase(self):
        response = self.client.post(
            f"{BASE_API_PATH}/datasets/MYDOMAIN/mydataset/query",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": ["domain -> was required to be lowercase only."]
        }
