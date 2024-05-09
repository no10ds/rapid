from pathlib import Path
from unittest.mock import patch, ANY

import pandas as pd
import pytest

from api.adapter.s3_adapter import S3Adapter
from api.application.services.authorisation.dataset_access_evaluator import (
    DatasetAccessEvaluator,
)
from api.application.services.data_service import DataService
from api.application.services.delete_service import DeleteService
from api.application.services.search_service import SearchService
from api.common.custom_exceptions import (
    UserError,
    DatasetValidationError,
    SchemaNotFoundError,
)
from api.common.config.auth import Action
from api.common.config.constants import BASE_API_PATH
from api.domain.dataset_filters import DatasetFilters
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata
from api.domain.search_metadata import SearchMetadata, MatchField
from api.domain.sql_query import SQLQuery
from test.api.common.controller_test_utils import BaseClientTest


class TestDataUpload(BaseClientTest):
    @patch.object(DataService, "upload_dataset")
    @patch("api.controller.datasets.store_file_to_disk")
    @patch("api.controller.datasets.get_subject_id")
    @patch("api.controller.datasets.generate_uuid")
    def test_calls_data_upload_service_successfully(
        self,
        mock_generate_uuid,
        mock_get_subject_id,
        mock_store_file_to_disk,
        mock_upload_dataset,
    ):
        file_content = b"some,content"
        incoming_file_path = Path("filename.csv")
        incoming_file_name = "filename.csv"
        raw_file_identifier = "123-456-789"
        subject_id = "subject_id"
        job_id = "abc-123"

        mock_generate_uuid.return_value = job_id
        mock_get_subject_id.return_value = subject_id
        mock_store_file_to_disk.return_value = incoming_file_path
        mock_upload_dataset.return_value = f"{raw_file_identifier}.csv", 2, "abc-123"

        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/domain/dataset?version=2",
            files={"file": (incoming_file_name, file_content, "text/csv")},
            headers={"Authorization": "Bearer test-token"},
        )

        mock_store_file_to_disk.assert_called_once_with("csv", job_id, ANY)
        mock_upload_dataset.assert_called_once_with(
            subject_id,
            job_id,
            DatasetMetadata("layer", "domain", "dataset", 2),
            incoming_file_path,
        )

        assert response.status_code == 202
        assert response.json() == {
            "details": {
                "original_filename": "filename.csv",
                "raw_filename": "123-456-789.csv",
                "dataset_version": 2,
                "status": "Data processing",
                "job_id": "abc-123",
            }
        }

    @patch("api.controller.datasets.construct_dataset_metadata")
    @patch.object(DataService, "upload_dataset")
    @patch("api.controller.datasets.store_file_to_disk")
    @patch("api.controller.datasets.get_subject_id")
    @patch("api.controller.datasets.generate_uuid")
    def test_calls_data_upload_service_with_latest_version_when_none_provided(
        self,
        mock_generate_uuid,
        mock_get_subject_id,
        mock_store_file_to_disk,
        mock_upload_dataset,
        mock_construct_datset_metadata,
    ):
        file_content = b"some,content"
        incoming_file_path = Path("filename.csv")
        incoming_file_name = "filename.csv"
        raw_file_identifier = "123-456-789"
        subject_id = "subject_id"
        job_id = "abc-123"
        mock_construct_datset_metadata.return_value = DatasetMetadata(
            "layer", "domain", "dataset", 14
        )
        mock_get_subject_id.return_value = subject_id
        mock_store_file_to_disk.return_value = incoming_file_path
        mock_upload_dataset.return_value = f"{raw_file_identifier}.csv", 14, "abc-123"
        mock_generate_uuid.return_value = job_id

        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/domain/dataset",
            files={"file": (incoming_file_name, file_content, "text/csv")},
            headers={"Authorization": "Bearer test-token"},
        )

        mock_store_file_to_disk.assert_called_once_with("csv", job_id, ANY)
        mock_upload_dataset.assert_called_once_with(
            subject_id,
            job_id,
            DatasetMetadata("layer", "domain", "dataset", 14),
            incoming_file_path,
        )

        assert response.status_code == 202
        assert response.json() == {
            "details": {
                "original_filename": "filename.csv",
                "raw_filename": "123-456-789.csv",
                "dataset_version": 14,
                "status": "Data processing",
                "job_id": "abc-123",
            }
        }

    @patch("api.controller.datasets.construct_dataset_metadata")
    @patch.object(DataService, "upload_dataset")
    @patch("api.controller.datasets.store_file_to_disk")
    @patch("api.controller.datasets.get_subject_id")
    @patch("api.controller.datasets.generate_uuid")
    def test_calls_data_upload_service_successfully_parquet(
        self,
        mock_generate_uuid,
        mock_get_subject_id,
        mock_store_file_to_disk,
        mock_upload_dataset,
        mock_construct_datset_metadata,
    ):
        file_content = b"some,content"
        incoming_file_path = Path("filename.parquet")
        incoming_file_name = "filename.parquet"
        raw_file_identifier = "123-456-789"
        subject_id = "subject_id"
        job_id = "abc-123"
        mock_construct_datset_metadata.return_value = DatasetMetadata(
            "layer", "domain", "dataset", 14
        )

        mock_generate_uuid.return_value = job_id
        mock_get_subject_id.return_value = subject_id
        mock_store_file_to_disk.return_value = incoming_file_path
        mock_upload_dataset.return_value = (
            f"{raw_file_identifier}.parquet",
            5,
            "abc-123",
        )

        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/domain/dataset",
            files={
                "file": (incoming_file_name, file_content, "application/octest-stream")
            },
            headers={"Authorization": "Bearer test-token"},
        )

        mock_store_file_to_disk.assert_called_once_with("parquet", job_id, ANY)
        mock_upload_dataset.assert_called_once_with(
            subject_id,
            job_id,
            DatasetMetadata("layer", "domain", "dataset", 14),
            incoming_file_path,
        )

        assert response.status_code == 202
        assert response.json() == {
            "details": {
                "original_filename": "filename.parquet",
                "raw_filename": "123-456-789.parquet",
                "dataset_version": 5,
                "status": "Data processing",
                "job_id": "abc-123",
            }
        }

    @patch.object(DataService, "upload_dataset")
    @patch("api.controller.datasets.store_file_to_disk")
    @patch("api.controller.datasets.get_subject_id")
    @patch("api.controller.datasets.generate_uuid")
    def test_calls_data_upload_service_with_version_successfully(
        self,
        mock_generate_uuid,
        mock_get_subject_id,
        mock_store_file_to_disk,
        mock_upload_dataset,
    ):
        job_id = "abc-123"
        file_content = b"some,content"
        incoming_file_path = Path("filename.csv")
        incoming_file_name = "filename.csv"
        raw_file_identifier = "123-456-789"
        subject_id = "subject_id"

        mock_generate_uuid.return_value = job_id
        mock_get_subject_id.return_value = subject_id
        mock_store_file_to_disk.return_value = incoming_file_path
        mock_upload_dataset.return_value = f"{raw_file_identifier}.csv", 2, "abc-123"

        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/domain/dataset?version=2",
            files={"file": (incoming_file_name, file_content, "text/csv")},
            headers={"Authorization": "Bearer test-token"},
        )

        mock_store_file_to_disk.assert_called_once_with("csv", job_id, ANY)
        mock_upload_dataset.assert_called_once_with(
            subject_id,
            job_id,
            DatasetMetadata("layer", "domain", "dataset", 2),
            incoming_file_path,
        )

        assert response.status_code == 202
        assert response.json() == {
            "details": {
                "original_filename": "filename.csv",
                "raw_filename": "123-456-789.csv",
                "dataset_version": 2,
                "status": "Data processing",
                "job_id": "abc-123",
            }
        }

    @patch.object(DataService, "upload_dataset")
    @patch("api.controller.datasets.store_file_to_disk")
    @patch("api.controller.datasets.get_subject_id")
    @patch("api.controller.datasets.generate_uuid")
    def test_calls_data_upload_service_with_version_successfully_parquet(
        self,
        mock_generate_uuid,
        mock_get_subject_id,
        mock_store_file_to_disk,
        mock_upload_dataset,
    ):
        job_id = "abc-123"
        file_content = b"some,content"
        incoming_file_path = Path("filename.parquet")
        incoming_file_name = "filename.parquet"
        raw_file_identifier = "123-456-789"
        subject_id = "subject_id"

        mock_generate_uuid.return_value = job_id
        mock_get_subject_id.return_value = subject_id
        mock_store_file_to_disk.return_value = incoming_file_path
        mock_upload_dataset.return_value = (
            f"{raw_file_identifier}.parquet",
            2,
            "abc-123",
        )

        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/domain/dataset?version=2",
            files={
                "file": (incoming_file_name, file_content, "application/octest-stream")
            },
            headers={"Authorization": "Bearer test-token"},
        )

        mock_store_file_to_disk.assert_called_once_with("parquet", job_id, ANY)
        mock_upload_dataset.assert_called_once_with(
            subject_id,
            job_id,
            DatasetMetadata("layer", "domain", "dataset", 2),
            incoming_file_path,
        )

        assert response.status_code == 202
        assert response.json() == {
            "details": {
                "original_filename": "filename.parquet",
                "raw_filename": "123-456-789.parquet",
                "dataset_version": 2,
                "status": "Data processing",
                "job_id": "abc-123",
            }
        }

    def test_calls_data_upload_service_fails_when_domain_uppercase(self):
        file_content = b"some,content"
        incoming_file_name = "filename.csv"

        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/DOMAIN/dataset",
            files={"file": (incoming_file_name, file_content, "text/csv")},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": ["domain -> was required to be lowercase only."]
        }

    def test_calls_data_upload_service_fails_when_filetype_is_invalid(self):
        file_content = b"some content"
        incoming_file_name = "filename.txt"

        response = self.client.post(
            f"{BASE_API_PATH}/datasets/raw/domain/dataset",
            files={"file": (incoming_file_name, file_content, "text/plain")},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {"details": "This file type txt, is not supported."}

    @patch.object(DataService, "upload_dataset")
    @patch("api.controller.datasets.store_file_to_disk")
    @patch("api.controller.datasets.get_subject_id")
    @patch("api.controller.datasets.generate_uuid")
    def test_calls_data_upload_service_fails_when_invalid_dataset_is_uploaded(
        self,
        mock_generate_uuid,
        mock_get_subject_id,
        mock_store_file_to_disk,
        mock_upload_dataset,
    ):
        job_id = "job_id"
        file_content = b"some,content"
        incoming_file_path = Path("filename.csv")
        incoming_file_name = "filename.csv"
        subject_id = "subject_id"

        mock_generate_uuid.return_value = job_id
        mock_get_subject_id.return_value = subject_id
        mock_store_file_to_disk.return_value = incoming_file_path
        mock_upload_dataset.side_effect = DatasetValidationError(
            "Expected 3 columns, received 4"
        )

        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/domain/dataset?version=3",
            files={"file": (incoming_file_name, file_content, "text/csv")},
            headers={"Authorization": "Bearer test-token"},
        )

        mock_upload_dataset.assert_called_once_with(
            subject_id,
            job_id,
            DatasetMetadata("layer", "domain", "dataset", 3),
            incoming_file_path,
        )

        assert response.status_code == 400
        assert response.json() == {"details": "Expected 3 columns, received 4"}

    def test_calls_data_fails_with_missing_path(self):
        file_content = b"some,content"
        file_name = "filename.csv"

        response = self.client.post(
            f"{BASE_API_PATH}/datasets//dataset",
            files={"file": (file_name, file_content, "text/csv")},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 404

    def test_raises_validation_error_when_file_not_provided(self):
        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/domain/dataset",
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 400

    @patch.object(DataService, "upload_dataset")
    @patch("api.controller.datasets.store_file_to_disk")
    @patch("api.controller.datasets.get_subject_id")
    def test_raises_error_when_schema_does_not_exist(
        self, mock_get_subject_id, mock_store_file_to_disk, mock_upload_dataset
    ):
        file_content = b"some,content"
        incoming_file_path = Path("filename.csv")
        incoming_file_name = "filename.csv"
        subject_id = "subject_id"

        mock_get_subject_id.return_value = subject_id
        mock_store_file_to_disk.return_value = (incoming_file_path, incoming_file_name)
        mock_upload_dataset.side_effect = SchemaNotFoundError("Error message")

        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/domain/dataset?version=1",
            files={"file": (incoming_file_name, file_content, "text/csv")},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400


class TestListDatasets(BaseClientTest):
    @patch.object(DatasetAccessEvaluator, "get_authorised_datasets")
    @patch("api.controller.datasets.get_subject_id")
    def test_returns_metadata_for_all_datasets(
        self, mock_get_subject_id, mock_get_authorised_datasets
    ):
        metadata_response = [
            SchemaMetadata(
                layer="layer",
                domain="domain1",
                dataset="dataset1",
                key_value_tags={"tag1": "value1"},
                description="",
                version=1,
                sensitivity="PUBLIC",
            ),
            SchemaMetadata(
                layer="layer",
                domain="domain2",
                dataset="dataset2",
                key_value_tags={"tag2": "value2"},
                version=1,
                description="some test description",
                sensitivity="PUBLIC",
            ),
        ]
        subject_id = "subject_id"
        mock_get_subject_id.return_value = subject_id
        mock_get_authorised_datasets.return_value = metadata_response

        expected_response = [
            {
                "layer": "layer",
                "domain": "domain1",
                "dataset": "dataset1",
                "sensitivity": "PUBLIC",
                "version": 1,
                "description": "",
                "key_value_tags": {"tag1": "value1"},
                "key_only_tags": [],
                "owners": None,
                "update_behaviour": "APPEND",
                "is_latest_version": True,
            },
            {
                "layer": "layer",
                "domain": "domain2",
                "dataset": "dataset2",
                "sensitivity": "PUBLIC",
                "version": 1,
                "description": "some test description",
                "key_value_tags": {"tag2": "value2"},
                "key_only_tags": [],
                "update_behaviour": "APPEND",
                "owners": None,
                "is_latest_version": True,
            },
        ]

        expected_query = DatasetFilters()

        response = self.client.post(
            f"{BASE_API_PATH}/datasets",
            headers={"Authorization": "Bearer test-token"},
            # Not passing a JSON body here to filter by tags
        )

        mock_get_authorised_datasets.assert_called_once_with(
            subject_id, Action.READ, expected_query
        )

        assert response.status_code == 200
        assert response.json() == expected_response

    @patch.object(DatasetAccessEvaluator, "get_authorised_datasets")
    @patch("api.controller.datasets.get_subject_id")
    def test_returns_metadata_for_datasets_with_certain_tags(
        self, mock_get_subject_id, mock_get_authorised_datasets
    ):
        subject_id = "abc-123"
        mock_get_subject_id.return_value = subject_id

        metadata_response = [
            SchemaMetadata(
                layer="layer",
                domain="domain1",
                dataset="dataset1",
                sensitivity="PUBLIC",
                key_value_tags={"tag1": "value1"},
                version=1,
                description="",
            ),
            SchemaMetadata(
                layer="layer",
                domain="domain2",
                dataset="dataset2",
                sensitivity="PUBLIC",
                key_value_tags={"tag2": "value2"},
                version=1,
                description="some test description",
            ),
        ]

        mock_get_authorised_datasets.return_value = metadata_response

        expected_response = [
            {
                "layer": "layer",
                "domain": "domain1",
                "dataset": "dataset1",
                "version": 1,
                "sensitivity": "PUBLIC",
                "key_value_tags": {"tag1": "value1"},
                "key_only_tags": [],
                "description": "",
                "owners": None,
                "is_latest_version": True,
                "update_behaviour": "APPEND",
            },
            {
                "layer": "layer",
                "domain": "domain2",
                "dataset": "dataset2",
                "version": 1,
                "sensitivity": "PUBLIC",
                "key_value_tags": {"tag2": "value2"},
                "key_only_tags": [],
                "description": "some test description",
                "is_latest_version": True,
                "owners": None,
                "update_behaviour": "APPEND",
            },
        ]

        tag_filters = {
            "tag1": "value1",
            "tag2": "",
        }

        expected_query_object = DatasetFilters(sensitivity=None, tags=tag_filters)

        response = self.client.post(
            f"{BASE_API_PATH}/datasets",
            headers={"Authorization": "Bearer test-token"},
            json={"tags": tag_filters},
        )

        mock_get_authorised_datasets.assert_called_once_with(
            subject_id, Action.READ, expected_query_object
        )

        assert response.status_code == 200
        assert response.json() == expected_response

    @patch.object(S3Adapter, "get_last_updated_time")
    @patch.object(DatasetAccessEvaluator, "get_authorised_datasets")
    @patch("api.controller.datasets.get_subject_id")
    def test_returns_enriched_metadata_for_datasets_with_certain_sensitivity(
        self,
        mock_get_subject_id,
        mock_get_authorised_datasets,
        mock_get_last_updated_time,
    ):
        metadata_response = [
            SchemaMetadata(
                layer="layer",
                domain="domain1",
                dataset="dataset1",
                version=1,
                sensitivity="PUBLIC",
                key_value_tags={"sensitivity": "PUBLIC", "tag1": "value1"},
                description="",
            ),
            SchemaMetadata(
                layer="layer",
                domain="domain2",
                dataset="dataset2",
                version=1,
                sensitivity="PUBLIC",
                key_value_tags={"sensitivity": "PUBLIC"},
                description="some test description",
            ),
        ]
        subject_id = "abc-123"
        mock_get_subject_id.return_value = subject_id
        mock_get_last_updated_time.side_effect = ["1234", "23456"]
        mock_get_authorised_datasets.return_value = metadata_response

        expected_query_object = DatasetFilters(sensitivity="PUBLIC")

        expected_response = [
            {
                "layer": "layer",
                "domain": "domain1",
                "dataset": "dataset1",
                "version": 1,
                "is_latest_version": True,
                "sensitivity": "PUBLIC",
                "key_value_tags": {"sensitivity": "PUBLIC", "tag1": "value1"},
                "key_only_tags": [],
                "description": "",
                "owners": None,
                "update_behaviour": "APPEND",
                "last_updated_date": "1234",
            },
            {
                "layer": "layer",
                "domain": "domain2",
                "dataset": "dataset2",
                "is_latest_version": True,
                "key_value_tags": {"sensitivity": "PUBLIC"},
                "key_only_tags": [],
                "sensitivity": "PUBLIC",
                "version": 1,
                "description": "some test description",
                "owners": None,
                "update_behaviour": "APPEND",
                "last_updated_date": "23456",
            },
        ]

        response = self.client.post(
            f"{BASE_API_PATH}/datasets?enriched=true",
            headers={"Authorization": "Bearer test-token"},
            json={"sensitivity": "PUBLIC"},
        )

        mock_get_authorised_datasets.assert_called_once_with(
            subject_id, Action.READ, expected_query_object
        )

        assert response.status_code == 200
        assert response.json() == expected_response


class TestSearchDatasets(BaseClientTest):
    @patch.object(SearchService, "search")
    def test_search(self, mock_search):
        mock_data = [
            SearchMetadata(
                layer="layer",
                domain="domain1",
                dataset="dataset1",
                version=1,
                matching_field=MatchField.Columns,
                matching_data=["col1", "col2"],
            ),
            SearchMetadata(
                layer="layer",
                domain="domain2",
                dataset="dataset2",
                version=1,
                matching_field=MatchField.Description,
                matching_data="This is a test dataset",
            ),
        ]
        mock_search.return_value = mock_data

        response = self.client.get(
            f"{BASE_API_PATH}/datasets/search/foo bar",
            headers={"Authorization": "Bearer test-token"},
        )

        mock_search.assert_called_once_with("foo bar")
        assert response.status_code == 200
        assert response.json() == [item.dict() for item in mock_data]

    @patch.object(SearchService, "search")
    def test_search_when_empty(self, mock_search):
        mock_search.return_value = []

        response = self.client.get(
            f"{BASE_API_PATH}/datasets/search/foo bar",
            headers={"Authorization": "Bearer test-token"},
        )

        mock_search.assert_called_once_with("foo bar")
        assert response.status_code == 200
        assert response.json() == []


class TestDatasetInfo(BaseClientTest):
    @patch.object(DataService, "get_dataset_info")
    def test_returns_metadata_for_all_datasets(self, mock_get_dataset_info):
        expected_response = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="mydomain",
                dataset="mydataset",
                sensitivity="PUBLIC",
                version=2,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=None,
                    data_type="string",
                    allow_null=True,
                    format=None,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="int",
                    allow_null=True,
                    format=None,
                ),
            ],
        )

        mock_get_dataset_info.return_value = expected_response

        response = self.client.get(
            f"{BASE_API_PATH}/datasets/layer/mydomain/mydataset/info?version=2",
            headers={"Authorization": "Bearer test-token"},
            # Not passing a JSON body here to filter by tags
        )

        assert response.status_code == 200
        assert response.json() == expected_response.dict()
        mock_get_dataset_info.assert_called_once_with(
            DatasetMetadata("layer", "mydomain", "mydataset", 2)
        )

    @patch.object(DataService, "get_dataset_info")
    @patch("api.controller.datasets.construct_dataset_metadata")
    def test_returns_metadata_for_all_datasets_for_latest_verion_when_none_provided(
        self, mock_construct_dataset_metadata, mock_get_dataset_info
    ):
        expected_response = Schema(
            metadata=SchemaMetadata(
                layer="layer",
                domain="mydomain",
                dataset="mydataset",
                sensitivity="PUBLIC",
                version=2,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=None,
                    data_type="string",
                    allow_null=True,
                    format=None,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="int",
                    allow_null=True,
                    format=None,
                ),
            ],
        )
        dataset_metadata = DatasetMetadata("layer", "mydomain", "mydataset", 2)

        mock_get_dataset_info.return_value = expected_response
        mock_construct_dataset_metadata.return_value = dataset_metadata

        response = self.client.get(
            f"{BASE_API_PATH}/datasets/layer/mydomain/mydataset/info",
            headers={"Authorization": "Bearer test-token"},
            # Not passing a JSON body here to filter by tags
        )

        assert response.status_code == 200
        assert response.json() == expected_response.dict()
        mock_get_dataset_info.assert_called_once_with(dataset_metadata)

    @patch.object(DataService, "get_dataset_info")
    def test_returns_error_response_when_schema_not_found_error(
        self, mock_get_dataset_info
    ):
        mock_get_dataset_info.side_effect = SchemaNotFoundError(
            "Could not find schema for raw/mydomain/mydataset/1"
        )

        response = self.client.get(
            f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/info?version=1",
            headers={"Authorization": "Bearer test-token"},
            # Not passing a JSON body here to filter by tags
        )

        mock_get_dataset_info.assert_called_once_with(
            DatasetMetadata("raw", "mydomain", "mydataset", 1)
        )

        assert response.status_code == 404
        assert response.json() == {
            "details": "Could not find schema for raw/mydomain/mydataset/1"
        }

    def test_returns_error_response_when_domain_uppercase(self):
        response = self.client.get(
            f"{BASE_API_PATH}/datasets/layer/MYDOMAIN/mydataset/info",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": ["domain -> was required to be lowercase only."]
        }


class TestQuery(BaseClientTest):
    def test_returns_error_response_when_domain_uppercase(self):
        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/MYDOMAIN/mydataset/query",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": ["domain -> was required to be lowercase only."]
        }

    @patch.object(DataService, "query_data")
    def test_call_service_with_only_domain_dataset_when_no_json_provided(
        self, mock_query_method
    ):
        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query?version=1"

        res = self.client.post(
            query_url, headers={"Authorization": "Bearer test-token"}
        )
        assert res.status_code == 200
        mock_query_method.assert_called_once_with(
            DatasetMetadata("raw", "mydomain", "mydataset", 1), SQLQuery()
        )

    @patch.object(DataService, "query_data")
    def test_call_service_with_sql_query_when_json_provided(self, mock_query_method):
        request_json = {"select_columns": ["column1"], "limit": "10"}

        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query?version=1"

        self.client.post(
            query_url, headers={"Authorization": "Bearer test-token"}, json=request_json
        )

        mock_query_method.assert_called_once_with(
            DatasetMetadata("raw", "mydomain", "mydataset", 1),
            SQLQuery(select_columns=["column1"], limit="10"),
        )

    @patch("api.controller.datasets.construct_dataset_metadata")
    @patch.object(DataService, "query_data")
    def test_call_service_with_latest_version_when_none_provided(
        self, mock_query_method, mock_construct_metadata
    ):
        mock_construct_metadata.return_value = DatasetMetadata(
            "raw", "mydomain", "mydataset", 32
        )
        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query"

        self.client.post(query_url, headers={"Authorization": "Bearer test-token"})

        mock_query_method.assert_called_once_with(
            DatasetMetadata("raw", "mydomain", "mydataset", 32), SQLQuery()
        )

    @patch.object(DataService, "query_data")
    def test_calls_service_with_sql_query_when_empty_json_values_provided(
        self, mock_query_method
    ):
        request_json = {
            "select_columns": ["column1"],
            "filter": "",
            "aggregation_conditions": "",
            "limit": "10",
        }

        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query?version=1"

        self.client.post(
            query_url, headers={"Authorization": "Bearer test-token"}, json=request_json
        )

        mock_query_method.assert_called_once_with(
            DatasetMetadata("raw", "mydomain", "mydataset", 1),
            SQLQuery(
                select_columns=["column1"],
                filter="",
                aggregation_conditions="",
                limit="10",
            ),
        )

    @patch.object(DataService, "query_data")
    def test_returns_formatted_json_from_query_result(self, mock_query_method):
        mock_query_method.return_value = pd.DataFrame(
            {
                "column1": [1, 2],
                "column2": ["item1", "item2"],
                "area": ["area_1", "area_2"],
            }
        )

        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query?version=3"

        response = self.client.post(
            query_url,
            headers={
                "Authorization": "Bearer test-token",
                "Accept": "application/json",
            },
        )

        assert response.status_code == 200

        assert response.json() == {
            "0": {"column1": "1", "column2": "item1", "area": "area_1"},
            "1": {"column1": "2", "column2": "item2", "area": "area_2"},
        }

    @patch.object(DataService, "query_data")
    def test_request_query_in_csv_is_successful(self, mock_query_method):
        mock_query_method.return_value = pd.DataFrame(
            {
                "column1": [1, 2],
                "column2": ["item1", "item2"],
                "area": ["area_1", "area_2"],
            }
        )

        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query?version=12"

        response = self.client.post(
            query_url,
            headers={"Authorization": "Bearer test-token", "Accept": "text/csv"},
        )

        assert response.status_code == 200

    @patch.object(DataService, "query_data")
    def test_returns_formatted_json_from_query_if_format_is_not_provided(
        self, mock_query_method
    ):
        mock_query_method.return_value = pd.DataFrame(
            {
                "column1": [1, 2],
                "column2": ["item1", "item2"],
                "area": ["area_1", "area_2"],
            }
        )

        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query?version=6"

        response = self.client.post(
            query_url, headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "0": {"column1": "1", "column2": "item1", "area": "area_1"},
            "1": {"column1": "2", "column2": "item2", "area": "area_2"},
        }

    @patch.object(DataService, "query_data")
    def test_returns_204_if_dataframe_is_empty(self, mock_query_method):
        mock_query_method.return_value = pd.DataFrame(
            {
                "column1": [],
                "column2": [],
                "area": [],
            }
        )

        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query?version=6"

        response = self.client.post(
            query_url, headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 204
        assert (
            response.text
            == "No rows were returned. Either there is no data or the query is too limiting."
        )

    @patch.object(DataService, "query_data")
    def test_returns_error_from_query_request_when_format_is_unsupported(
        self, mock_query_method
    ):
        mock_query_method.return_value = pd.DataFrame(
            {
                "column1": [1, 2],
                "column2": ["item1", "item2"],
                "area": ["area_1", "area_2"],
            }
        )

        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query?version=12"

        response = self.client.post(
            query_url,
            headers={"Authorization": "Bearer test-token", "Accept": "text/plain"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": "Provided value for Accept header parameter [text/plain] is not supported. Supported formats: application/json, text/csv, application/octet-stream"
        }

    @pytest.mark.parametrize(
        "input_key", ["select_column", "invalid_key", "another_invalid_key"]
    )
    def test_returns_error_from_query_request_when_invalid_key(self, input_key: str):
        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query"

        response = self.client.post(
            query_url,
            headers={"Authorization": "Bearer test-token", "Accept": "text/csv"},
            json={input_key: "some_value"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": [f"{input_key} -> Extra inputs are not permitted"]
        }


class TestLargeDatasetQuery(BaseClientTest):
    def test_returns_error_response_when_domain_uppercase(self):
        response = self.client.post(
            f"{BASE_API_PATH}/datasets/layer/MYDOMAIN/mydataset/query/large",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": ["domain -> was required to be lowercase only."]
        }

    @patch.object(DataService, "query_large_data")
    @patch("api.controller.datasets.get_subject_id")
    def test_call_service_with_only_domain_dataset_when_no_json_provided(
        self, mock_get_subject_id, mock_large_query_method
    ):
        query_url = (
            f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query/large?version=1"
        )
        subject_id = "subject_id"

        mock_get_subject_id.return_value = subject_id

        self.client.post(query_url, headers={"Authorization": "Bearer test-token"})

        mock_large_query_method.assert_called_once_with(
            subject_id,
            DatasetMetadata("raw", "mydomain", "mydataset", 1),
            SQLQuery(),
        )

    @patch.object(DataService, "query_large_data")
    @patch("api.controller.datasets.get_subject_id")
    def test_call_service_with_sql_query_when_json_provided(
        self, mock_get_subject_id, mock_large_query_method
    ):
        request_json = {"select_columns": ["column1"], "limit": "10"}

        query_url = (
            f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query/large?version=10"
        )
        subject_id = "subject_id"

        mock_get_subject_id.return_value = subject_id

        self.client.post(
            query_url, headers={"Authorization": "Bearer test-token"}, json=request_json
        )

        mock_large_query_method.assert_called_once_with(
            subject_id,
            DatasetMetadata("raw", "mydomain", "mydataset", 10),
            SQLQuery(select_columns=["column1"], limit="10"),
        )

    @patch("api.controller.datasets.construct_dataset_metadata")
    @patch.object(DataService, "query_large_data")
    @patch("api.controller.datasets.get_subject_id")
    def test_call_service_with_latest_version_when_none_provided(
        self,
        mock_get_subject_id,
        mock_large_query_method,
        mock_construct_dataset_metadata,
    ):
        mock_construct_dataset_metadata.return_value = DatasetMetadata(
            "raw", "mydomain", "mydataset", 3
        )
        query_url = f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query/large"
        subject_id = "subject_id"

        mock_get_subject_id.return_value = subject_id

        self.client.post(query_url, headers={"Authorization": "Bearer test-token"})

        mock_large_query_method.assert_called_once_with(
            subject_id, DatasetMetadata("raw", "mydomain", "mydataset", 3), SQLQuery()
        )

    @patch.object(DataService, "query_large_data")
    @patch("api.controller.datasets.get_subject_id")
    def test_calls_service_with_sql_query_when_empty_json_values_provided(
        self, mock_get_subject_id, mock_large_query_method
    ):
        request_json = {
            "select_columns": ["column1"],
            "filter": "",
            "aggregation_conditions": "",
            "limit": "10",
        }

        query_url = (
            f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query/large?version=13"
        )
        subject_id = "subject_id"

        mock_get_subject_id.return_value = subject_id

        self.client.post(
            query_url, headers={"Authorization": "Bearer test-token"}, json=request_json
        )

        mock_large_query_method.assert_called_once_with(
            subject_id,
            DatasetMetadata(
                "raw",
                "mydomain",
                "mydataset",
                13,
            ),
            SQLQuery(
                select_columns=["column1"],
                filter="",
                aggregation_conditions="",
                limit="10",
            ),
        )

    @patch.object(DataService, "query_large_data")
    @patch("api.controller.datasets.get_subject_id")
    def test_request_query_is_successful(
        self, mock_get_subject_id, mock_large_query_method
    ):
        mock_large_query_method.return_value = "5462433"

        query_url = (
            f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query/large?version=1"
        )
        subject_id = "subject_id"

        mock_get_subject_id.return_value = subject_id

        response = self.client.post(
            query_url,
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 202
        assert response.json() == {"details": {"job_id": "5462433"}}

    @pytest.mark.parametrize(
        "input_key", ["select_column", "invalid_key", "another_invalid_key"]
    )
    @patch("api.controller.datasets.get_subject_id")
    def test_returns_error_from_query_request_when_invalid_key(
        self, mock_get_subject_id, input_key: str
    ):
        query_url = (
            f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/query/large?version=2"
        )
        subject_id = "subject_id"

        mock_get_subject_id.return_value = subject_id

        response = self.client.post(
            query_url,
            headers={"Authorization": "Bearer test-token"},
            json={input_key: "some_value"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": [f"{input_key} -> Extra inputs are not permitted"]
        }


class TestListFilesFromDataset(BaseClientTest):
    @patch.object(DataService, "list_raw_files")
    def test_returns_metadata_for_all_datasets(self, mock_list_raw_files):
        mock_list_raw_files.return_value = [
            "2020-01-01T12:00:00-file1.csv",
            "2020-07-01T16:00:00-file2.csv",
            "2020-11-01T15:00:00-file3.csv",
        ]

        response = self.client.get(
            f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/2/files",
            headers={"Authorization": "Bearer test-token"},
        )

        mock_list_raw_files.assert_called_once_with(
            DatasetMetadata("raw", "mydomain", "mydataset", 2)
        )

        assert response.status_code == 200

    def test_returns_error_response_when_domain_uppercase(self):
        response = self.client.get(
            f"{BASE_API_PATH}/datasets/raw/MYDOMAIN/mydataset/2/files",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": ["domain -> was required to be lowercase only."]
        }


class TestDeleteFiles(BaseClientTest):
    @patch.object(DeleteService, "delete_dataset_file")
    def test_returns_200_when_file_is_deleted(self, mock_delete_dataset_file):
        response = self.client.delete(
            f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/3/2022-01-01T00:00:00-file.csv",
            headers={"Authorization": "Bearer test-token"},
        )

        mock_delete_dataset_file.assert_called_once_with(
            DatasetMetadata("raw", "mydomain", "mydataset", 3),
            "2022-01-01T00:00:00-file.csv",
        )

        assert response.status_code == 200

    @patch.object(DeleteService, "delete_dataset_file")
    def test_returns_400_when_file_name_does_not_exist(self, mock_delete_dataset_file):
        mock_delete_dataset_file.side_effect = UserError("Some random message")

        response = self.client.delete(
            f"{BASE_API_PATH}/datasets/raw/mydomain/mydataset/5/2022-01-01T00:00:00-file.csv",
            headers={"Authorization": "Bearer test-token"},
        )

        mock_delete_dataset_file.assert_called_once_with(
            DatasetMetadata("raw", "mydomain", "mydataset", 5),
            "2022-01-01T00:00:00-file.csv",
        )

        assert response.status_code == 400
        assert response.json() == {"details": "Some random message"}

    def test_returns_error_response_when_domain_uppercase(self):
        response = self.client.delete(
            f"{BASE_API_PATH}/datasets/raw/MYDOMAIN/mydataset/5/2022-01-01T00:00:00-file.csv",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "details": ["domain -> was required to be lowercase only."]
        }


class TestDeleteDataset(BaseClientTest):
    @patch.object(DeleteService, "delete_dataset")
    def test_returns_202_when_dataset_is_deleted(self, mock_delete_dataset):
        response = self.client.delete(
            f"{BASE_API_PATH}/datasets/layer/mydomain/mydataset",
            headers={"Authorization": "Bearer test-token"},
        )

        mock_delete_dataset.assert_called_once_with(
            DatasetMetadata("layer", "mydomain", "mydataset")
        )

        assert response.status_code == 202
        assert response.json() == {"details": "mydataset has been deleted."}
