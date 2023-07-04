import json
import threading
from time import sleep
from typing import Dict, List

import boto3
from botocore.exceptions import ClientError

from api.common.config.aws import (
    AWS_REGION,
    GLUE_CATALOGUE_DB_NAME,
    GLUE_CRAWLER_ROLE,
    GLUE_CONNECTION_NAME,
    GLUE_TABLE_PRESENCE_CHECK_RETRY_COUNT,
    GLUE_TABLE_PRESENCE_CHECK_INTERVAL,
    RESOURCE_PREFIX,
    AWS_ACCOUNT,
)
from api.common.custom_exceptions import (
    CrawlerStartFailsError,
    CrawlerIsNotReadyError,
    TableDoesNotExistError,
    CrawlerAlreadyExistsError,
    CrawlerCreationError,
    AWSServiceError,
    CrawlerUpdateError,
)
from api.common.logger import AppLogger
from api.domain.data_types import DataTypes
from api.domain.schema import Column, Schema
from api.domain.storage_metadata import StorageMetaData


class GlueAdapter:
    def __init__(
        self,
        glue_client=boto3.client("glue", region_name=AWS_REGION),
        glue_catalogue_db_name=GLUE_CATALOGUE_DB_NAME,
        glue_crawler_role=GLUE_CRAWLER_ROLE,
        glue_connection_name=GLUE_CONNECTION_NAME,
    ):
        self.glue_client = glue_client
        self.glue_catalogue_db_name = glue_catalogue_db_name
        self.glue_crawler_role = glue_crawler_role
        self.glue_connection_name = glue_connection_name

    def create_crawler(self, domain: str, dataset: str, tags: Dict[str, str]):
        data_store = StorageMetaData(domain, dataset)
        try:
            self.glue_client.create_crawler(
                Name=self._generate_crawler_name(domain, dataset),
                Role=self.glue_crawler_role,
                DatabaseName=self.glue_catalogue_db_name,
                TablePrefix=data_store.glue_table_prefix(),
                Targets={
                    "S3Targets": [
                        {
                            "Path": data_store.s3_path(),
                            "ConnectionName": self.glue_connection_name,
                        },
                    ]
                },
                SchemaChangePolicy={"DeleteBehavior": "DELETE_FROM_DATABASE"},
                Configuration=json.dumps(
                    {
                        "Version": 1.0,
                        "Grouping": {
                            "TableLevelConfiguration": 5,
                            "TableGroupingPolicy": "CombineCompatibleSchemas",
                        },
                    }
                ),
                Tags=tags,
            )
        except ClientError as error:
            self._handle_crawler_create_error(error)

    def start_crawler(self, domain: str, dataset: str):
        try:
            self.glue_client.start_crawler(
                Name=self._generate_crawler_name(domain, dataset)
            )
        except ClientError:
            raise CrawlerStartFailsError("Failed to start crawler")

    def delete_crawler(self, domain: str, dataset: str):
        try:
            self.glue_client.delete_crawler(
                Name=self._generate_crawler_name(domain, dataset)
            )
        except ClientError:
            raise AWSServiceError("Failed to delete crawler")

    def set_crawler_version_tag(
        self, domain: str, dataset: str, new_version: int
    ) -> None:
        try:
            glue_crawler_arn = (
                "arn:aws:glue:{region}:{account_id}:crawler/{glue_crawler}".format(
                    region=AWS_REGION,
                    account_id=AWS_ACCOUNT,
                    glue_crawler=self._generate_crawler_name(domain, dataset),
                )
            )
            self.glue_client.tag_resource(
                ResourceArn=glue_crawler_arn,
                TagsToAdd={"no_of_versions": str(new_version)},
            )

        except ClientError:
            raise CrawlerUpdateError(
                f"Failed to update crawler version tag for domain = {domain} dataset = {dataset} version = {new_version}"  # nosec B608
            )

    def check_crawler_is_ready(self, domain: str, dataset: str) -> None:
        if self._get_crawler_state(domain, dataset) != "READY":
            raise CrawlerIsNotReadyError(
                f"Crawler is currently processing for resource_prefix={RESOURCE_PREFIX}, domain={domain} and dataset={dataset}"
            )

    def update_catalog_table_config(self, schema: Schema) -> None:
        threading.Thread(
            target=self.update_partition_column_data_types, args=(schema,)
        ).start()

    def update_partition_column_data_types(self, schema: Schema) -> None:
        table_name = StorageMetaData(
            schema.get_domain(), schema.get_dataset()
        ).glue_table_name()
        table_definition = self.get_table_when_created(table_name)
        updated_definition = self.update_glue_table_partition_column_types(
            table_definition, schema.get_partition_columns()
        )
        self.glue_client.update_table(
            DatabaseName=self.glue_catalogue_db_name, TableInput=updated_definition
        )
        AppLogger.info(
            f"Glue table [{table_name}] updated with correct column types config"
        )

    def get_table_when_created(self, table_name: str) -> Dict:
        for _ in range(GLUE_TABLE_PRESENCE_CHECK_RETRY_COUNT):
            try:
                return self._get_table(table_name)
            except TableDoesNotExistError:
                AppLogger.info(
                    f"Waiting {GLUE_TABLE_PRESENCE_CHECK_INTERVAL}s for table [{table_name}] to be created"
                )
                sleep(GLUE_TABLE_PRESENCE_CHECK_INTERVAL)
                continue
        raise AWSServiceError(
            f"[{table_name}] was not created after {GLUE_TABLE_PRESENCE_CHECK_RETRY_COUNT * GLUE_TABLE_PRESENCE_CHECK_INTERVAL}s"
        )  # noqa: E501

    def get_table_last_updated_date(
        self, table_name, supress_error: bool = False
    ) -> str:
        try:
            table = self._get_table(table_name)
        except TableDoesNotExistError as e:
            if supress_error:
                return None
            else:
                raise TableDoesNotExistError(e)
        return str(table["Table"]["UpdateTime"])

    def get_no_of_rows(self, table_name) -> int:
        table = self._get_table(table_name)
        return int(table["Table"]["StorageDescriptor"]["Parameters"]["recordCount"])

    def get_tables_for_dataset(self, domain: str, dataset: str) -> List[str]:
        search_term = StorageMetaData(
            domain=domain, dataset=dataset
        ).glue_table_prefix()
        tables = [item["Name"] for item in self._search_tables(search_term)]
        return tables

    def delete_tables(self, table_names: List[str]):
        try:
            self.glue_client.batch_delete_table(
                DatabaseName=GLUE_CATALOGUE_DB_NAME, TablesToDelete=table_names
            )
        except ClientError:
            raise AWSServiceError("Failed to delete tables")

    def update_glue_table_partition_column_types(
        self, table_definition: Dict, partition_columns: List[Column]
    ) -> Dict:
        table_partition_keys = table_definition["Table"]["PartitionKeys"]

        partition_column_type_map = {
            schema_partition.name: schema_partition.data_type
            for schema_partition in partition_columns
        }

        glue_types_map = {
            DataTypes.INT16: "bigint",
            DataTypes.INT32: "bigint",
            DataTypes.INT64: "bigint",
            DataTypes.FLOAT: "double",
        }

        for table_partition in table_partition_keys:
            actual_data_type = partition_column_type_map[table_partition["Name"]]
            if actual_data_type in glue_types_map:
                table_partition["Type"] = glue_types_map[actual_data_type]

        return {
            "Name": table_definition["Table"]["Name"],
            "Owner": table_definition["Table"]["Owner"],
            "LastAccessTime": table_definition["Table"]["LastAccessTime"],
            "Retention": table_definition["Table"]["Retention"],
            "PartitionKeys": table_partition_keys,
            "TableType": table_definition["Table"]["TableType"],
            "Parameters": table_definition["Table"]["Parameters"],
            "StorageDescriptor": table_definition["Table"]["StorageDescriptor"],
        }

    def _get_crawler_state(self, domain: str, dataset: str) -> str:
        try:
            response = self.glue_client.get_crawler(
                Name=self._generate_crawler_name(domain, dataset)
            )
            return response["Crawler"]["State"]
        except ClientError:
            raise AWSServiceError(
                f"Failed to get crawler state resource_prefix={RESOURCE_PREFIX}, domain = {domain} dataset = {dataset}"
            )

    def _generate_crawler_name(self, domain: str, dataset: str) -> str:
        return f"{RESOURCE_PREFIX}_crawler/{domain}/{dataset}"

    def _handle_crawler_create_error(self, error: ClientError):
        if error.response["Error"]["Code"] == "AlreadyExistsException":
            raise CrawlerAlreadyExistsError("Crawler already exists with same name")
        else:
            raise CrawlerCreationError("Crawler creation error")

    def _get_table(self, table_name: str) -> Dict:
        try:
            table = self.glue_client.get_table(
                DatabaseName=self.glue_catalogue_db_name, Name=table_name
            )
            return table
        except ClientError as error:
            if error.response["Error"]["Code"] == "EntityNotFoundException":
                raise TableDoesNotExistError(f"The table [{table_name}] does not exist")

    def _search_tables(self, search_term: str) -> Dict:
        try:
            paginator = self.glue_client.get_paginator("get_tables")
            page_iterator = paginator.paginate(
                DatabaseName=GLUE_CATALOGUE_DB_NAME,
            )
            tables = []
            for page in page_iterator:
                tables.extend(page["TableList"])

            return [table for table in tables if table["Name"].startswith(search_term)]
        except ClientError:
            raise AWSServiceError(f"Failed to search tables with term={search_term}")
