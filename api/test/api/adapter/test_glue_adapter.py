from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError

from api.adapter.glue_adapter import GlueAdapter
from api.common.config.aws import (
    DATA_BUCKET,
    GLUE_TABLE_PRESENCE_CHECK_RETRY_COUNT,
    GLUE_CATALOGUE_DB_NAME,
)
from api.common.custom_exceptions import (
    AWSServiceError,
    TableAlreadyExistsError,
    TableCreationError,
)
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import SchemaMetadata


class TestGlueAdapterTableMethods:
    glue_boto_client = None

    def setup_method(self):
        self.glue_boto_client = Mock()
        self.glue_adapter = GlueAdapter(
            self.glue_boto_client,
            "GLUE_CATALOGUE_DB_NAME",
        )
        self.valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="layer",
                domain="domain",
                dataset="dataset",
                version=1,
                description="description",
                sensitivity="PUBLIC",
            ),
            columns={
                "colname1": Column(
                    partition_index=0,
                    dtype="int",
                    nullable=True,
                ),
                "colname2": Column(
                    partition_index=None,
                    dtype="string",
                    nullable=False,
                ),
            },
        )

    def test_create_table(self):
        self.glue_adapter.create_table(self.valid_schema)
        self.glue_boto_client.create_table.assert_called_once_with(
            DatabaseName="GLUE_CATALOGUE_DB_NAME",
            TableInput={
                "Name": "layer_domain_dataset_1",
                "Owner": "hadoop",
                "StorageDescriptor": {
                    "Columns": [{"Name": "colname2", "Type": "string"}],
                    "Location": f"s3://{DATA_BUCKET}/data/layer/domain/dataset/1",
                    "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                    "Compressed": False,
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                        "Parameters": {"serialization.format": "1"},
                    },
                    "NumberOfBuckets": -1,
                    "StoredAsSubDirectories": False,
                },
                "PartitionKeys": [
                    {"Name": "colname1", "Type": "int"},
                ],
                "TableType": "EXTERNAL_TABLE",
                "Parameters": {
                    "classification": "parquet",
                    "typeOfData": "file",
                    "compressionType": "none",
                    "EXTERNAL": "TRUE",
                },
            },
            PartitionIndexes=[
                {
                    "Keys": ["colname1"],
                    "IndexName": "rapid-creation-partition",
                }
            ],
        )

    def test_create_table_already_exists_error(self):
        self.glue_boto_client.create_table.side_effect = ClientError(
            error_response={"Error": {"Code": "AlreadyExistsException"}},
            operation_name="CreateTable",
        )
        with pytest.raises(TableAlreadyExistsError):
            self.glue_adapter.create_table(self.valid_schema)

    def test_create_table_creation_error(self):
        self.glue_boto_client.create_table.side_effect = ClientError(
            error_response={"Error": {"Code": "OtherError"}},
            operation_name="CreateTable",
        )
        with pytest.raises(TableCreationError):
            self.glue_adapter.create_table(self.valid_schema)

    def test_gets_table_when_created(self):
        table_config = {}
        self.glue_boto_client.get_table.return_value = table_config

        result = self.glue_adapter.get_table_when_created("some-name")

        assert result == table_config

    def test_get_tables_for_dataset(self):
        paginate = self.glue_boto_client.get_paginator.return_value.paginate
        paginate.return_value = [
            {"TableList": [{"Name": "layer_domain_dataset_1"}]},
            {"TableList": [{"Name": "layer_domain_dataset_2"}]},
        ]

        result = self.glue_adapter.get_tables_for_dataset(
            DatasetMetadata("layer", "domain", "dataset")
        )

        assert result == ["layer_domain_dataset_1", "layer_domain_dataset_2"]

    def test_delete_tables(self):
        table_names = ["domain_dataset_1", "domain_dataset_2"]
        self.glue_adapter.delete_tables(table_names)
        self.glue_boto_client.batch_delete_table.assert_called_once_with(
            DatabaseName=GLUE_CATALOGUE_DB_NAME, TablesToDelete=table_names
        )

    def test_delete_tables_fails(self):
        table_names = ["domain_dataset_1", "domain_dataset_2"]
        self.glue_boto_client.batch_delete_table.side_effect = ClientError(
            error_response={"Error": {"Code": "SomethingElse"}},
            operation_name="BatchDeleteTable",
        )

        with pytest.raises(AWSServiceError):
            self.glue_adapter.delete_tables(table_names)

    @patch("api.adapter.glue_adapter.sleep")
    def test_raises_error_when_table_does_not_exist_and_retries_exhausted(
        self, mock_sleep
    ):
        self.glue_boto_client.get_table.side_effect = ClientError(
            error_response={"Error": {"Code": "EntityNotFoundException"}},
            operation_name="GetTable",
        )

        with pytest.raises(
            AWSServiceError, match=r"\[some-name\] was not created after \d+s"
        ):
            self.glue_adapter.get_table_when_created("some-name")

        assert mock_sleep.call_count == GLUE_TABLE_PRESENCE_CHECK_RETRY_COUNT
