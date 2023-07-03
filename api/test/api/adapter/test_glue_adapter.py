from unittest.mock import Mock, patch, ANY

import pytest
from botocore.exceptions import ClientError

from api.adapter.glue_adapter import GlueAdapter
from api.common.config.aws import (
    GLUE_TABLE_PRESENCE_CHECK_RETRY_COUNT,
    GLUE_CATALOGUE_DB_NAME,
    DATA_BUCKET,
    AWS_REGION,
    AWS_ACCOUNT,
)
from api.common.config.aws import RESOURCE_PREFIX
from api.common.custom_exceptions import (
    CrawlerStartFailsError,
    CrawlerIsNotReadyError,
    CrawlerAlreadyExistsError,
    CrawlerCreationError,
    AWSServiceError,
    CrawlerUpdateError,
)
from api.domain.schema import Column, Schema
from api.domain.schema_metadata import SchemaMetadata


class TestGlueAdapterCrawlerMethods:
    glue_boto_client = None

    def setup_method(self):
        self.glue_boto_client = Mock()
        self.glue_adapter = GlueAdapter(
            self.glue_boto_client,
            "GLUE_CATALOGUE_DB_NAME",
            "GLUE_CRAWLER_ROLE",
            "GLUE_CONNECTION_DB_NAME",
        )

    def test_create_crawler(self):
        self.glue_adapter.create_crawler(
            "domain",
            "dataset",
            {"tag1": "value1", "tag2": "value2", "tag3": "value3"},
        )
        self.glue_boto_client.create_crawler.assert_called_once_with(
            Name=f"{RESOURCE_PREFIX}_crawler/domain/dataset",
            Role="GLUE_CRAWLER_ROLE",
            DatabaseName="GLUE_CATALOGUE_DB_NAME",
            TablePrefix="domain_dataset_",
            Targets={
                "S3Targets": [
                    {
                        "Path": f"s3://{DATA_BUCKET}/data/domain/dataset/",
                        "ConnectionName": "GLUE_CONNECTION_DB_NAME",
                    },
                ]
            },
            SchemaChangePolicy={"DeleteBehavior": "DELETE_FROM_DATABASE"},
            Configuration='{"Version": 1.0, "Grouping": {"TableLevelConfiguration": 5, "TableGroupingPolicy": "CombineCompatibleSchemas"}}',
            Tags={
                "tag1": "value1",
                "tag2": "value2",
                "tag3": "value3",
            },
        )

    def test_set_crawler_version_tag(self):
        domain = "testdomain323"
        dataset = "testdataset4243"
        glue_crawler_arn = f"arn:aws:glue:{AWS_REGION}:{AWS_ACCOUNT}:crawler/rapid_crawler/{domain}/{dataset}"
        self.glue_adapter.set_crawler_version_tag(
            domain,
            dataset,
            42,
        )
        self.glue_boto_client.tag_resource.assert_called_once_with(
            ResourceArn=glue_crawler_arn, TagsToAdd={"no_of_versions": "42"}
        )

    def test_set_crawler_version_tag_failure(self):
        domain = "testdomain323"
        dataset = "testdataset4243"
        new_version = 42
        glue_crawler_arn = f"arn:aws:glue:{AWS_REGION}:{AWS_ACCOUNT}:crawler/rapid_crawler/{domain}/{dataset}"
        self.glue_boto_client.tag_resource.side_effect = ClientError(
            error_response={"Error": {"Code": "SomeProblem"}},
            operation_name="tag_resource",
        )
        with pytest.raises(
            CrawlerUpdateError,
            match=f"Failed to update crawler version tag for domain = {domain} dataset = {dataset} version = {new_version}",
        ):
            self.glue_adapter.set_crawler_version_tag(
                domain,
                dataset,
                new_version,
            )

        self.glue_boto_client.tag_resource.assert_called_once_with(
            ResourceArn=glue_crawler_arn, TagsToAdd={"no_of_versions": "42"}
        )

    def test_create_crawler_fails_already_exists(self):
        self.glue_boto_client.create_crawler.side_effect = ClientError(
            error_response={"Error": {"Code": "AlreadyExistsException"}},
            operation_name="CreateCrawler",
        )

        with pytest.raises(CrawlerAlreadyExistsError):
            self.glue_adapter.create_crawler("domain", "dataset", {})

    def test_create_crawler_fails(self):
        self.glue_boto_client.create_crawler.side_effect = ClientError(
            error_response={"Error": {"Code": "SomethingElse"}},
            operation_name="CreateCrawler",
        )

        with pytest.raises(CrawlerCreationError):
            self.glue_adapter.create_crawler("domain", "dataset", {})

    def test_start_crawler(self):
        self.glue_adapter.start_crawler("domain", "dataset")
        self.glue_boto_client.start_crawler.assert_called_once_with(
            Name=RESOURCE_PREFIX + "_crawler/domain/dataset"
        )

    def test_start_crawler_fails(self):
        self.glue_boto_client.start_crawler.side_effect = ClientError(
            error_response={"Error": {"Code": "SomethingElse"}},
            operation_name="StartCrawler",
        )

        with pytest.raises(CrawlerStartFailsError):
            self.glue_adapter.start_crawler("domain", "dataset")

    def test_delete_crawler(self):
        self.glue_adapter.delete_crawler("domain", "dataset")
        self.glue_boto_client.delete_crawler.assert_called_once_with(
            Name=RESOURCE_PREFIX + "_crawler/domain/dataset"
        )

    def test_delete_crawler_fails(self):
        self.glue_boto_client.delete_crawler.side_effect = ClientError(
            error_response={"Error": {"Code": "SomethingElse"}},
            operation_name="DeleteCrawler",
        )

        with pytest.raises(AWSServiceError):
            self.glue_adapter.delete_crawler("domain", "dataset")

    @patch("api.adapter.glue_adapter.RESOURCE_PREFIX", "the-resource-prefix")
    def test_fails_to_check_if_crawler_is_running(self):
        self.glue_boto_client.get_crawler.side_effect = ClientError(
            error_response={"Error": {"Code": "SomeProblem"}},
            operation_name="GetCrawler",
        )

        with pytest.raises(
            AWSServiceError,
            match="Failed to get crawler state resource_prefix=the-resource-prefix, domain = domain1 dataset = dataset2",
        ):
            self.glue_adapter.check_crawler_is_ready("domain1", "dataset2")

    def test_check_crawler_is_ready(self):
        self.glue_boto_client.get_crawler.return_value = {
            "Crawler": {
                "State": "READY",
            }
        }
        self.glue_adapter.check_crawler_is_ready("domain", "dataset")
        self.glue_boto_client.get_crawler.assert_called_once_with(
            Name=f"{RESOURCE_PREFIX}_crawler/domain/dataset"
        )

    def test_check_crawler_is_not_ready(self):
        for state in ["RUNNING", "STOPPING"]:
            self.glue_boto_client.get_crawler.return_value = {
                "Crawler": {
                    "State": state,
                }
            }
            with pytest.raises(CrawlerIsNotReadyError):
                self.glue_adapter.check_crawler_is_ready("domain", "dataset")

            self.glue_boto_client.get_crawler.assert_called_with(
                Name=f"{RESOURCE_PREFIX}_crawler/domain/dataset"
            )


class TestGlueAdapterTableMethods:
    glue_boto_client = None

    def setup_method(self):
        self.glue_boto_client = Mock()
        self.glue_adapter = GlueAdapter(
            self.glue_boto_client,
            "GLUE_CATALOGUE_DB_NAME",
            "GLUE_CRAWLER_ROLE",
            "GLUE_CONNECTION_DB_NAME",
        )

    @patch("api.adapter.glue_adapter.threading.Thread")
    def test_starts_thread_to_update_table_config_when_table_does_not_exist(
        self, mock_thread
    ):
        self.glue_boto_client.get_table.side_effect = ClientError(
            error_response={"Error": {"Code": "EntityNotFoundException"}},
            operation_name="GetTable",
        )

        schema = Mock()
        schema.get_domain.return_value = "a-domain"
        schema.get_dataset.return_value = "b-dataset"

        self.glue_adapter.update_catalog_table_config(schema)

        mock_thread.assert_called_once_with(target=ANY, args=(schema,))

    def test_updates_table_config_with_partition_column_data_types(
        self,
    ):
        original_table_config = {
            "Table": {
                "Name": 111,
                "Owner": 222,
                "LastAccessTime": 333,
                "Retention": 444,
                "PartitionKeys": [
                    {"Name": "year", "Type": "string"},
                    {"Name": "rate", "Type": "string"},
                    {"Name": "city", "Type": "string"},
                ],
                "TableType": 666,
                "Parameters": 777,
                "StorageDescriptor": 888,
            }
        }

        partition_columns = [
            Column(name="year", data_type="Int64", partition_index=1, allow_null=False),
            Column(
                name="rate", data_type="Float64", partition_index=2, allow_null=False
            ),
            Column(
                name="city", data_type="object", partition_index=3, allow_null=False
            ),
        ]

        altered_table_config = {
            "Name": 111,
            "Owner": 222,
            "LastAccessTime": 333,
            "Retention": 444,
            "PartitionKeys": [
                {"Name": "year", "Type": "bigint"},
                {"Name": "rate", "Type": "double"},
                {"Name": "city", "Type": "string"},
            ],
            "TableType": 666,
            "Parameters": 777,
            "StorageDescriptor": 888,
        }

        result = self.glue_adapter.update_glue_table_partition_column_types(
            original_table_config, partition_columns
        )

        assert result == altered_table_config

    def test_updates_table_with_altered_config(self):
        self.glue_boto_client.get_table.return_value = {
            "Table": {
                "Name": 111,
                "Owner": 222,
                "LastAccessTime": 333,
                "Retention": 444,
                "PartitionKeys": [
                    {"Name": "year", "Type": "string"},
                    {"Name": "rate", "Type": "string"},
                ],
                "TableType": 666,
                "Parameters": 777,
                "StorageDescriptor": 888,
            }
        }

        schema = Schema(
            metadata=SchemaMetadata(
                domain="some", dataset="other", sensitivity="PUBLIC", owners=[]
            ),
            columns=[
                Column(
                    name="year", data_type="Int64", partition_index=1, allow_null=False
                ),
                Column(
                    name="rate",
                    data_type="Float64",
                    partition_index=2,
                    allow_null=False,
                ),
                Column(
                    name="city",
                    data_type="object",
                    partition_index=None,
                    allow_null=False,
                ),
            ],
        )

        altered_table_config = {
            "Name": 111,
            "Owner": 222,
            "LastAccessTime": 333,
            "Retention": 444,
            "PartitionKeys": [
                {"Name": "year", "Type": "bigint"},
                {"Name": "rate", "Type": "double"},
            ],
            "TableType": 666,
            "Parameters": 777,
            "StorageDescriptor": 888,
        }

        self.glue_adapter.update_partition_column_data_types(schema)

        self.glue_boto_client.update_table.assert_called_once_with(
            DatabaseName="GLUE_CATALOGUE_DB_NAME", TableInput=altered_table_config
        )

    def test_gets_table_when_created(self):
        table_config = {}
        self.glue_boto_client.get_table.return_value = table_config

        result = self.glue_adapter.get_table_when_created("some-name")

        assert result == table_config

    def test_gets_table_last_updated_date(self):
        table_config = {
            "Table": {
                "Name": "test_e2e",
                "DatabaseName": "rapid_catalogue_db",
                "Owner": "owner",
                "CreateTime": "2022-03-01 11:03:49+00:00",
                "UpdateTime": "2022-03-03 11:03:49+00:00",
                "LastAccessTime": "2022-03-02 11:03:49+00:00",
                "Retention": 0,
            }
        }
        self.glue_boto_client.get_table.return_value = table_config

        result = self.glue_adapter.get_table_last_updated_date("table_name")

        assert result == "2022-03-03 11:03:49+00:00"

    def test_get_no_of_rows_in_table(self):
        table_properties = {
            "Table": {
                "Name": "qa_carsales_25_1",
                "DatabaseName": "rapid_catalogue_db",
                "Owner": "owner",
                "StorageDescriptor": {
                    "Parameters": {
                        "averageRecordSize": "17",
                        "classification": "parquet",
                        "compressionType": "none",
                        "objectCount": "5",
                        "recordCount": "990300",
                        "sizeKey": "4762462",
                        "typeOfData": "file",
                    },
                },
            }
        }
        self.glue_boto_client.get_table.return_value = table_properties

        result = self.glue_adapter.get_no_of_rows("qa_carsales_25_1")

        assert result == 990300

    def test_get_tables_for_dataset(self):
        paginate = self.glue_boto_client.get_paginator.return_value.paginate
        paginate.return_value = [
            {"TableList": [{"Name": "domain_dataset_1"}]},
            {"TableList": [{"Name": "domain_dataset_2"}]},
        ]

        result = self.glue_adapter.get_tables_for_dataset("domain", "dataset")

        assert result == ["domain_dataset_1", "domain_dataset_2"]

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
