from pathlib import Path
from unittest.mock import Mock, call, patch

import pandas as pd
import pytest
from botocore.exceptions import ClientError

from api.adapter.s3_adapter import S3Adapter
from api.common.config.auth import SensitivityLevel
from api.common.config.aws import SCHEMAS_LOCATION, OUTPUT_QUERY_BUCKET
from api.common.custom_exceptions import (
    UserError,
    AWSServiceError,
)
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata, SchemaMetadatas
from test.test_utils import (
    mock_schema_response,
    mock_list_schemas_response,
)


class TestS3AdapterUpload:
    mock_s3_client = None
    persistence_adapter = None

    def setup_method(self):
        self.mock_s3_client = Mock()
        self.persistence_adapter = S3Adapter(
            s3_client=self.mock_s3_client, s3_bucket="dataset"
        )

    def _assert_store_data_raises(self, exception, message, filename, object_content):
        with pytest.raises(exception, match=message):
            self.persistence_adapter.store_data(
                object_full_path=filename, object_content=object_content
            )

    def test_data_upload(self):
        filename = "test_journey_file.csv"
        file_content = b"colname1,colname2\nsomething,123\notherthing,456\n\n"

        self.persistence_adapter.store_data(
            object_full_path=filename, object_content=file_content
        )

        self.mock_s3_client.put_object.assert_called_with(
            Bucket="dataset",
            Key=filename,
            Body=file_content,
        )

    def test_store_data_throws_exception_when_file_name_is_not_provided(self):
        self._assert_store_data_raises(
            exception=UserError,
            message="File path is invalid",
            filename=None,
            object_content="something",
        )

    def test_store_data_throws_exception_when_file_name_is_empty(self):
        self._assert_store_data_raises(
            exception=UserError,
            message="File path is invalid",
            filename="",
            object_content="something",
        )

    def test_store_data_throws_exception_when_file_contents_empty(self):
        self._assert_store_data_raises(
            exception=UserError,
            message="File content is invalid",
            filename="filename.csv",
            object_content="",
        )

    def test_construct_partitioned_data_path(self):
        result = self.persistence_adapter._construct_partitioned_data_path(
            "partition", "file.csv", "domain", "dataset", "4"
        )
        assert result == "data/domain/dataset/4/partition/file.csv"

    def test_upload_partitioned_data(self):
        domain = "domain"
        dataset = "dataset"
        version = 1
        filename = "data.parquet"

        partition_1 = pd.DataFrame({"colname2": ["user1"]})
        partition_2 = pd.DataFrame({"colname2": ["user2"]})

        partitioned_data = [
            ("year=2020/month=1", partition_1),
            ("year=2020/month=2", partition_2),
        ]

        self.persistence_adapter.upload_partitioned_data(
            domain, dataset, version, filename, partitioned_data
        )

        partition_1_parquet = partition_1.to_parquet(compression="gzip", index=False)
        partition_2_parquet = partition_2.to_parquet(compression="gzip", index=False)

        calls = [
            call(
                Bucket="dataset",
                Key="data/domain/dataset/1/year=2020/month=1/data.parquet",
                Body=partition_1_parquet,
            ),
            call(
                Bucket="dataset",
                Key="data/domain/dataset/1/year=2020/month=2/data.parquet",
                Body=partition_2_parquet,
            ),
        ]

        self.mock_s3_client.put_object.assert_has_calls(calls)

    def test_schema_upload(self):
        valid_schema = Schema(
            metadata=SchemaMetadata(
                domain="test_domain",
                dataset="test_dataset",
                sensitivity="PUBLIC",
                version=1,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=True,
                )
            ],
        )

        result = self.persistence_adapter.save_schema(schema=valid_schema)

        self.mock_s3_client.put_object.assert_called_with(
            Bucket="dataset",
            Key="data/schemas/PUBLIC/test_domain/test_dataset/1/schema.json",
            Body=b'{"metadata": {"domain": "test_domain", "dataset": "test_dataset", "sensitivity": "PUBLIC", "version": 1, "description": "", "key_value_tags": {}, "key_only_tags": [], "owners": [{"name": "owner", "email": "owner@email.com"}], "update_behaviour": "APPEND"}, "columns": [{"name": "colname1", "partition_index": 0, "data_type": "Int64", "allow_null": true, "format": null}]}',
        )

        assert result == "test_domain/test_dataset/1/schema.json"

    def test_schema_upload_capitalised(self):
        valid_schema = Schema(
            metadata=SchemaMetadata(
                domain="TEST_DOMAIN",
                dataset="test_dataset",
                sensitivity="PUBLIC",
                version=1,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=True,
                )
            ],
        )

        result = self.persistence_adapter.save_schema(schema=valid_schema)

        self.mock_s3_client.put_object.assert_called_with(
            Bucket="dataset",
            Key="data/schemas/PUBLIC/test_domain/test_dataset/1/schema.json",
            Body=b'{"metadata": {"domain": "test_domain", "dataset": "test_dataset", "sensitivity": "PUBLIC", "version": 1, "description": "", "key_value_tags": {}, "key_only_tags": [], "owners": [{"name": "owner", "email": "owner@email.com"}], "update_behaviour": "APPEND"}, "columns": [{"name": "colname1", "partition_index": 0, "data_type": "Int64", "allow_null": true, "format": null}]}',
        )

        assert result == "test_domain/test_dataset/1/schema.json"

    def test_raw_data_upload(self):
        valid_schema = Schema(
            metadata=SchemaMetadata(
                domain="some",
                dataset="values",
                sensitivity="PUBLIC",
                version=2,
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=True,
                )
            ],
        )

        self.persistence_adapter.upload_raw_data(
            valid_schema,
            file_path=Path("filename.csv"),
            raw_file_identifier="123-456-789",
        )

        self.mock_s3_client.upload_file.assert_called_with(
            Filename="filename.csv",
            Bucket="dataset",
            Key="raw_data/some/values/2/123-456-789.csv",
        )


class TestS3AdapterDataRetrieval:
    mock_s3_client = None
    persistence_adapter = None

    def setup_method(self):
        self.mock_s3_client = Mock()
        self.persistence_adapter = S3Adapter(
            s3_client=self.mock_s3_client, s3_bucket="dataset"
        )

    def test_retrieve_data(self):
        self.persistence_adapter.retrieve_data(key="an_s3_object")
        self.mock_s3_client.get_object.assert_called_once()

    @patch("api.adapter.s3_adapter.S3Adapter.retrieve_schema_metadata")
    def test_retrieve_existing_schema(self, mock_s3_adapter_retrieve_schema_metadata):
        domain = "test_domain"
        dataset = "test_dataset"
        version = 1

        valid_schema = Schema(
            metadata=SchemaMetadata(
                domain=domain,
                dataset=dataset,
                sensitivity="PUBLIC",
                description="some test description",
                version=1,
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="Int64",
                    allow_null=True,
                )
            ],
        )

        self.mock_s3_client.get_object.return_value = mock_schema_response()
        mock_s3_adapter_retrieve_schema_metadata.return_value = SchemaMetadata(
            domain=domain,
            dataset=dataset,
            sensitivity="PUBLIC",
            description="some test description",
            version=1,
        )

        schema = self.persistence_adapter.find_schema(
            domain=domain, dataset=dataset, version=version
        )
        self.mock_s3_client.get_object.assert_called_once_with(
            Bucket="dataset",
            Key="data/schemas/PUBLIC/test_domain/test_dataset/1/schema.json",
        )

        assert schema == valid_schema

    def test_retrieve_non_existent_schema(self):
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = (
            mock_list_schemas_response()
        )
        schema = self.persistence_adapter.find_schema("bad", "data", 1)

        self.mock_s3_client.get_paginator.assert_called_once_with("list_objects")
        self.mock_s3_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="dataset", Prefix="data/schemas"
        )

        assert schema is None

    def test_find_raw_file_when_file_exists(self):
        self.persistence_adapter.find_raw_file("domain", "dataset", 1, "filename.csv")
        self.mock_s3_client.get_object.assert_called_once_with(
            Bucket="dataset", Key="raw_data/domain/dataset/1/filename.csv"
        )

    def test_throws_error_for_find_raw_file_when_file__does_not_exist(self):
        self.mock_s3_client.get_object.side_effect = ClientError(
            error_response={
                "Error": {"Code": "NoSuchKey"},
            },
            operation_name="message",
        )

        with pytest.raises(UserError, match="The file \\[bad_file\\] does not exist"):
            self.persistence_adapter.find_raw_file("domain", "dataset", 2, "bad_file")

        self.mock_s3_client.get_object.assert_called_once_with(
            Bucket="dataset", Key="raw_data/domain/dataset/2/bad_file"
        )


class TestS3Deletion:
    mock_s3_client = None
    persistence_adapter = None

    def setup_method(self):
        self.mock_s3_client = Mock()
        self.persistence_adapter = S3Adapter(
            s3_client=self.mock_s3_client, s3_bucket="data-bucket"
        )

    def test_deletion_of_schema(self):
        self.persistence_adapter.delete_schema("domain", "dataset", "PUBLIC", 2)

        self.mock_s3_client.delete_object.assert_called_once_with(
            Bucket="data-bucket", Key="data/schemas/PUBLIC/domain/dataset/2/schema.json"
        )

    def test_deletion_of_dataset_files_with_no_partitions(self):
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "Contents": [
                    {"Key": "data/domain/dataset/1/123-456-789_111-222-333.parquet"},
                    {"Key": "data/domain/dataset/1/123-456-789_444-555-666.parquet"},
                    {"Key": "data/domain/dataset/1/123-456-789_777-888-999.parquet"},
                    {"Key": "data/domain/dataset/1/999-999-999_111-888-999.parquet"},
                    {"Key": "data/domain/dataset/2/888-888-888_777-888-999.parquet"},
                ],
                "Name": "data-bucket",
                "Prefix": "data/domain/dataset",
                "EncodingType": "url",
            }
        ]
        self.mock_s3_client.delete_objects.return_value = {
            "Deleted": [
                {
                    "Key": "data/domain/dataset/1/123-456-789_111-222-333.parquet",
                },
                {
                    "Key": "data/domain/dataset/1/123-456-789_444-555-666.parquet",
                },
                {
                    "Key": "data/domain/dataset/1/123-456-789_777-888-999.parquet",
                },
            ],
        }

        self.persistence_adapter.delete_dataset_files(
            "domain", "dataset", 1, "123-456-789.csv"
        )
        self.mock_s3_client.get_paginator.assert_called_once_with("list_objects")
        self.mock_s3_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="data-bucket", Prefix="data/domain/dataset/1"
        )

        self.mock_s3_client.delete_objects.assert_called_once_with(
            Bucket="data-bucket",
            Delete={
                "Objects": [
                    {
                        "Key": "data/domain/dataset/1/123-456-789_111-222-333.parquet",
                    },
                    {
                        "Key": "data/domain/dataset/1/123-456-789_444-555-666.parquet",
                    },
                    {
                        "Key": "data/domain/dataset/1/123-456-789_777-888-999.parquet",
                    },
                ],
            },
        )

    def test_deletion_of_dataset_files_with_partitions(self):
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "Contents": [
                    {
                        "Key": "data/domain/dataset/1/2022/123-456-789_111-222-333.parquet"
                    },
                    {
                        "Key": "data/domain/dataset/1/2021/123-456-789_444-555-666.parquet"
                    },
                    {
                        "Key": "data/domain/dataset/1/2019/123-456-789_777-888-999.parquet"
                    },
                    {
                        "Key": "data/domain/dataset/1/2019/999-999-999_111-888-999.parquet"
                    },
                    {
                        "Key": "data/domain/dataset/2/2022/888-888-888_777-888-999.parquet"
                    },
                ],
                "Name": "data-bucket",
                "Prefix": "data/domain/dataset",
                "EncodingType": "url",
            }
        ]
        self.mock_s3_client.delete_objects.return_value = {
            "Deleted": [
                {"Key": "data/domain/dataset/1/2022/123-456-789_111-222-333.parquet"},
                {"Key": "data/domain/dataset/1/2021/123-456-789_444-555-666.parquet"},
                {"Key": "data/domain/dataset/1/2019/123-456-789_777-888-999.parquet"},
            ]
        }

        self.persistence_adapter.delete_dataset_files(
            "domain", "dataset", 1, "123-456-789.csv"
        )
        self.mock_s3_client.get_paginator.assert_called_once_with("list_objects")
        self.mock_s3_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="data-bucket", Prefix="data/domain/dataset/1"
        )

        self.mock_s3_client.delete_objects.assert_called_once_with(
            Bucket="data-bucket",
            Delete={
                "Objects": [
                    {
                        "Key": "data/domain/dataset/1/2022/123-456-789_111-222-333.parquet"
                    },
                    {
                        "Key": "data/domain/dataset/1/2021/123-456-789_444-555-666.parquet"
                    },
                    {
                        "Key": "data/domain/dataset/1/2019/123-456-789_777-888-999.parquet"
                    },
                ],
            },
        )

    def test_deletion_of_dataset_files_when_error_is_thrown(self):
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = {}

        self.mock_s3_client.delete_objects.return_value = {
            "Errors": [
                {
                    "Key": "An error",
                    "VersionId": "has occurred",
                    "Code": "403 Forbidden",
                    "Message": "There is a problem with your Amazon Web Services account",
                },
                {
                    "Key": "Another error",
                    "VersionId": "has occurred",
                    "Code": "403 Forbidden",
                    "Message": "There is a problem with your Amazon Web Services account",
                },
            ]
        }
        msg = "The item \\[123-456-789.csv\\] could not be deleted. Please contact your administrator."

        with pytest.raises(AWSServiceError, match=msg):
            self.persistence_adapter.delete_dataset_files(
                "domain", "dataset", 3, "123-456-789.csv"
            )

        self.mock_s3_client.get_paginator.assert_called_once_with("list_objects")
        self.mock_s3_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="data-bucket", Prefix="data/domain/dataset/3"
        )

    def test_deletion_of_raw_files(self):
        self.mock_s3_client.list_objects.return_value = {
            "Contents": [
                {"Key": "data/domain/dataset/1/123-456-789_11-222-333.parquet"},
                {"Key": "data/domain/dataset/1/123-456-789_444-555-666.parquet"},
                {"Key": "data/domain/dataset/1/123-456-789_777-888-999.parquet"},
            ],
            "Name": "data-bucket",
            "Prefix": "data/domain/dataset",
            "EncodingType": "url",
        }
        self.mock_s3_client.delete_objects.return_value = {
            "Deleted": [{"Key": "raw_data/domain/dataset/123-456-789.csv"}]
        }

        self.persistence_adapter.delete_raw_dataset_files(
            "domain", "dataset", 1, "123-456-789.csv"
        )
        self.mock_s3_client.delete_objects.assert_called_once_with(
            Bucket="data-bucket",
            Delete={"Objects": [{"Key": "raw_data/domain/dataset/1/123-456-789.csv"}]},
        )

    def test_deletion_of_raw_files_when_error_is_thrown(self):
        self.mock_s3_client.delete_objects.return_value = {
            "Errors": [
                {
                    "Key": "An error",
                    "VersionId": "has occurred",
                    "Code": "403 Forbidden",
                    "Message": "There is a problem with your Amazon Web Services account",
                },
                {
                    "Key": "Another error",
                    "VersionId": "has occurred",
                    "Code": "403 Forbidden",
                    "Message": "There is a problem with your Amazon Web Services account",
                },
            ]
        }
        msg = "The item \\[123-456-789.csv\\] could not be deleted. Please contact your administrator."

        with pytest.raises(AWSServiceError, match=msg):
            self.persistence_adapter.delete_raw_dataset_files(
                "domain", "dataset", 3, "123-456-789.csv"
            )

    def test_delete_previous_dataset_files(self):
        self.persistence_adapter._list_files_from_path = Mock(
            return_value=[
                "data/domain/dataset/1/abc-def.parquet",
                "data/domain/dataset/1/123-456.parquet",
                "data/domain/dataset/1/789-123.parquet",
            ]
        )
        self.persistence_adapter._delete_data = Mock()

        self.persistence_adapter.delete_previous_dataset_files(
            "domain", "dataset", 1, "123-456"
        )
        expected_calls = [
            call("data/domain/dataset/1/abc-def.parquet"),
            call("data/domain/dataset/1/789-123.parquet"),
        ]

        self.persistence_adapter._list_files_from_path.assert_called_once_with(
            "data/domain/dataset/1"
        )
        self.persistence_adapter._delete_data.assert_has_calls(expected_calls)

    def test_delete_previous_dataset_files_when_none_exist(self):
        self.persistence_adapter._list_files_from_path = Mock(
            return_value=[
                "data/domain/dataset/1/123-456.parquet",
            ]
        )
        self.persistence_adapter._delete_data = Mock()

        self.persistence_adapter.delete_previous_dataset_files(
            "domain", "dataset", 1, "123-456"
        )

        self.persistence_adapter._list_files_from_path.assert_called_once_with(
            "data/domain/dataset/1"
        )
        self.persistence_adapter._delete_data.assert_not_called()


class TestDatasetMetadataRetrieval:
    mock_s3_client = None
    persistence_adapter = None

    def setup_method(self):
        self.mock_s3_client = Mock()
        self.persistence_adapter = S3Adapter(
            s3_client=self.mock_s3_client, s3_bucket="data-bucket"
        )

    @pytest.mark.parametrize(
        "domain, dataset, sensitivity, expected",
        [
            ("test_domain", "test_dataset", "PUBLIC", SensitivityLevel.PUBLIC),
            ("sample", "other", "PRIVATE", SensitivityLevel.PRIVATE),
            ("hi", "there", "PROTECTED", SensitivityLevel.PROTECTED),
        ],
    )
    def test_retrieves_dataset_sensitivity(
        self, domain: str, dataset: str, sensitivity: str, expected: SensitivityLevel
    ):
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = (
            mock_list_schemas_response(domain, dataset, sensitivity)
        )

        result = self.persistence_adapter.get_dataset_sensitivity(domain, dataset)

        self.mock_s3_client.get_paginator.assert_called_once_with("list_objects")
        self.mock_s3_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="data-bucket", Prefix=SCHEMAS_LOCATION
        )

        assert result == expected

    def test_returns_none_if_not_schemas_exist(self):
        domain, dataset = "test_domain", "test_dataset"
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = {}

        result = self.persistence_adapter.find_schema(domain, dataset, 1)

        self.mock_s3_client.get_paginator.assert_called_once_with("list_objects")
        self.mock_s3_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="data-bucket", Prefix=SCHEMAS_LOCATION
        )

        assert result is None

    @pytest.mark.parametrize(
        "domain, dataset",
        [
            (None, None),
            ("domain", None),
            (None, "dataset"),
        ],
    )
    def test_returns_none_when_either_domain_or_dataset_or_both_not_specified(
        self, domain: str, dataset: str
    ):
        result = self.persistence_adapter.get_dataset_sensitivity(domain, dataset)

        assert result is SensitivityLevel.PUBLIC


class TestS3FileList:
    mock_s3_client = None
    persistence_adapter = None

    def setup_method(self):
        self.mock_s3_client = Mock()
        self.persistence_adapter = S3Adapter(
            s3_client=self.mock_s3_client, s3_bucket="my-bucket"
        )

    def test_list_raw_files(self):
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "Contents": [
                    {"Key": "raw_data/my_domain/my_dataset/"},
                    {
                        "Key": "raw_data/my_domain/my_dataset/2020-01-01T12:00:00-file1.csv"
                    },
                    {
                        "Key": "raw_data/my_domain/my_dataset/2020-06-01T15:00:00-file2.csv"
                    },
                    {
                        "Key": "raw_data/my_domain/my_dataset/2020-11-15T16:00:00-file3.csv",
                    },
                ],
                "Name": "my-bucket",
                "Prefix": "raw_data/my_domain/my_dataset",
                "EncodingType": "url",
            }
        ]

        raw_files = self.persistence_adapter.list_raw_files(
            "my_domain", "my_dataset", 1
        )
        assert raw_files == [
            "2020-01-01T12:00:00-file1.csv",
            "2020-06-01T15:00:00-file2.csv",
            "2020-11-15T16:00:00-file3.csv",
        ]

        self.mock_s3_client.get_paginator.assert_called_once_with("list_objects")
        self.mock_s3_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="my-bucket", Prefix="raw_data/my_domain/my_dataset/1"
        )

    def test_list_raw_files_when_empty(self):
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "Name": "my-bucket",
                "Prefix": "raw_data/my_domain/my_dataset",
                "EncodingType": "url",
            }
        ]

        raw_files = self.persistence_adapter.list_raw_files(
            "my_domain", "my_dataset", 2
        )
        assert raw_files == []

        self.mock_s3_client.get_paginator.assert_called_once_with("list_objects")
        self.mock_s3_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="my-bucket", Prefix="raw_data/my_domain/my_dataset/2"
        )

    def test_list_raw_files_when_empty_response(self):
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = {}

        raw_files = self.persistence_adapter.list_raw_files(
            "my_domain", "my_dataset", 1
        )
        assert raw_files == []

        self.mock_s3_client.get_paginator.assert_called_once_with("list_objects")
        self.mock_s3_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="my-bucket", Prefix="raw_data/my_domain/my_dataset/1"
        )

    def test_list_dataset_files(self):
        self.mock_s3_client.get_paginator.return_value.paginate.side_effect = [
            [
                {
                    "NextToken": "xxx",
                    "ResponseMetadata": {"key": "value"},
                    "Contents": [
                        {"Key": "raw_data/my_domain/my_dataset/"},
                        {
                            "Key": "raw_data/my_domain/my_dataset/2020-01-01T12:00:00-file1.csv"
                        },
                        {
                            "Key": "raw_data/my_domain/my_dataset/2020-06-01T15:00:00-file2.csv"
                        },
                        {
                            "Key": "raw_data/my_domain/my_dataset/2020-11-15T16:00:00-file3.csv",
                        },
                    ],
                    "Name": "my-bucket",
                    "EncodingType": "url",
                },
            ],
            [
                {
                    "NextToken": "xxx",
                    "ResponseMetadata": {"key": "value"},
                    "Contents": [
                        {"Key": "data/my_domain/my_dataset/"},
                        {
                            "Key": "data/my_domain/my_dataset/2020-01-01T12:00:00-file1.parquet"
                        },
                        {
                            "Key": "data/my_domain/my_dataset/2020-06-01T15:00:00-file2.parquet"
                        },
                    ],
                    "Name": "my-bucket",
                    "EncodingType": "url",
                },
            ],
            [
                {
                    "NextToken": "xxx",
                    "ResponseMetadata": {"key": "value"},
                    "Contents": [
                        {"Key": "data/schemas/PROTECTED/my_domain/my_dataset/"},
                        {
                            "Key": "data/schemas/PROTECTED/my_domain/my_dataset/1/schema.json"
                        },
                    ],
                    "Name": "my-bucket",
                    "EncodingType": "url",
                },
            ],
        ]

        dataset_files = self.persistence_adapter.list_dataset_files(
            "my_domain", "my_dataset", "PROTECTED"
        )
        assert dataset_files == [
            "raw_data/my_domain/my_dataset/",
            "raw_data/my_domain/my_dataset/2020-01-01T12:00:00-file1.csv",
            "raw_data/my_domain/my_dataset/2020-06-01T15:00:00-file2.csv",
            "raw_data/my_domain/my_dataset/2020-11-15T16:00:00-file3.csv",
            "data/my_domain/my_dataset/",
            "data/my_domain/my_dataset/2020-01-01T12:00:00-file1.parquet",
            "data/my_domain/my_dataset/2020-06-01T15:00:00-file2.parquet",
            "data/schemas/PROTECTED/my_domain/my_dataset/",
            "data/schemas/PROTECTED/my_domain/my_dataset/1/schema.json",
        ]

        calls = [
            call(Bucket="my-bucket", Prefix="raw_data/my_domain/my_dataset"),
            call(Bucket="my-bucket", Prefix="data/my_domain/my_dataset"),
            call(
                Bucket="my-bucket", Prefix="data/schemas/PROTECTED/my_domain/my_dataset"
            ),
        ]
        self.mock_s3_client.get_paginator.return_value.paginate.assert_has_calls(calls)

    def test_list_dataset_files_when_empty(self):
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "Name": "my-bucket",
                "Prefix": "raw_data/my_domain/my_dataset",
                "EncodingType": "url",
            }
        ]
        dataset_files = self.persistence_adapter.list_dataset_files(
            "my_domain", "my_dataset", "PROTECTED"
        )
        assert dataset_files == []

        calls = [
            call(Bucket="my-bucket", Prefix="raw_data/my_domain/my_dataset"),
            call(Bucket="my-bucket", Prefix="data/my_domain/my_dataset"),
            call(
                Bucket="my-bucket", Prefix="data/schemas/PROTECTED/my_domain/my_dataset"
            ),
        ]
        self.mock_s3_client.get_paginator.return_value.paginate.assert_has_calls(calls)

    def test_list_dataset_files_when_empty_response(self):
        self.mock_s3_client.get_paginator.return_value.paginate.return_value = {}

        dataset_files = self.persistence_adapter.list_dataset_files(
            "my_domain", "my_dataset", "PROTECTED"
        )
        assert dataset_files == []

        calls = [
            call(Bucket="my-bucket", Prefix="raw_data/my_domain/my_dataset"),
            call(Bucket="my-bucket", Prefix="data/my_domain/my_dataset"),
            call(
                Bucket="my-bucket", Prefix="data/schemas/PROTECTED/my_domain/my_dataset"
            ),
        ]
        self.mock_s3_client.get_paginator.return_value.paginate.assert_has_calls(calls)


class TestGenerateS3PreSignedUrl:
    mock_s3_client = None
    persistence_adapter = None

    def setup_method(self):
        self.mock_s3_client = Mock()
        self.persistence_adapter = S3Adapter(
            s3_client=self.mock_s3_client, s3_bucket="my-bucket"
        )

    def test_generate_presigned_download_url(self):
        self.mock_s3_client.generate_presigned_url.return_value = (
            "https://aws.the-s3-url.com"
        )

        url = self.persistence_adapter.generate_query_result_download_url(
            "the-execution-id"
        )

        assert url == "https://aws.the-s3-url.com"
        self.mock_s3_client.generate_presigned_url.assert_called_once_with(
            ClientMethod="get_object",
            Params={"Bucket": OUTPUT_QUERY_BUCKET, "Key": "the-execution-id.csv"},
            HttpMethod="GET",
            ExpiresIn=86400,
        )

    def test_raises_error_when_generation_fails(self):
        self.mock_s3_client.generate_presigned_url.side_effect = ClientError(
            error_response={
                "Error": {"Code": "NoSuchKey"},
            },
            operation_name="GeneratePresignedURL",
        )

        with pytest.raises(AWSServiceError, match="Unable to generate download URL"):
            self.persistence_adapter.generate_query_result_download_url(
                "the-file-key.csv"
            )


class TestS3AdapterFunctions:
    mock_s3_client = None
    persistence_adapter = None

    def setup_method(self):
        self.mock_s3_client = Mock()
        self.persistence_adapter = S3Adapter(
            s3_client=self.mock_s3_client, s3_bucket="my-bucker"
        )

    @patch("api.adapter.s3_adapter.S3Adapter._list_all_schemas")
    def test_retrieve_schema_metadata(self, mock_s3_adapter_list_all_schemas):
        mock_s3_adapter_list_all_schemas.return_value = SchemaMetadatas(
            metadatas=[
                SchemaMetadata(
                    domain="test_domain",
                    dataset="test_dataset",
                    sensitivity="PUBLIC",
                    description="some test description",
                    version=1,
                )
            ]
        )
        metadata = self.persistence_adapter.retrieve_schema_metadata(
            "test_domain", "test_dataset", 1
        )

        assert metadata.domain == "test_domain"
