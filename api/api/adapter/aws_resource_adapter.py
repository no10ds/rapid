from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional, TYPE_CHECKING

import boto3
from botocore.exceptions import ClientError

from api.common.config.aws import AWS_REGION, RESOURCE_PREFIX
from api.common.custom_exceptions import UserError, AWSServiceError
from api.common.logger import AppLogger
from api.domain.dataset_filters import DatasetFilters
from api.domain.storage_metadata import StorageMetaData


if TYPE_CHECKING:
    from api.adapter.s3_adapter import S3Adapter
    from api.adapter.glue_adapter import GlueAdapter


class AWSResourceAdapter:
    def __init__(
        self,
        resource_client=boto3.client(
            "resourcegroupstaggingapi", region_name=AWS_REGION
        ),
    ):
        self.__resource_client = resource_client

    @dataclass(frozen=True)
    class EnrichedDatasetMetaData(StorageMetaData):
        tags: Optional[Dict[str, str]] = None
        last_updated: Optional[str] = None

    def get_datasets_metadata(
        self,
        s3_adapter: "S3Adapter",
        glue_adapter: "GlueAdapter",
        query: DatasetFilters = DatasetFilters(),
    ) -> List[EnrichedDatasetMetaData]:
        try:
            AppLogger.info("Getting datasets info")
            aws_resources = self._get_resources(
                ["glue:crawler"], query.format_resource_query()
            )
            resources_prefix = self._filter_for_resource_prefix(aws_resources)
            return [
                self._to_dataset_metadata(resource, s3_adapter, glue_adapter)
                for resource in resources_prefix
            ]
        except KeyError:
            return []
        except ClientError as error:
            self._handle_client_error(error)

    def _filter_for_resource_prefix(self, aws_resources):
        return [
            resource
            for resource in aws_resources
            if f":crawler/{RESOURCE_PREFIX}_crawler" in resource["ResourceARN"]
        ]

    def _handle_client_error(self, error):
        AppLogger.error(f"Failed to request datasets tags error={error.response}")
        if (
            error.response
            and error.response["Error"]
            and error.response["Error"]["Code"]
            and error.response["Error"]["Code"] == "InvalidParameterException"
        ):
            raise UserError("Wrong parameters sent to list datasets")
        else:
            raise AWSServiceError(
                "Internal server error, please contact system administrator"
            )

    def _get_resources(self, resource_types: List[str], tag_filters: List[Dict]):
        AppLogger.info(f"Getting AWS resources with tags {tag_filters}")
        paginator = self.__resource_client.get_paginator("get_resources")
        page_iterator = paginator.paginate(
            ResourceTypeFilters=resource_types,
            TagFilters=tag_filters,
        )
        return (
            item for page in page_iterator for item in page["ResourceTagMappingList"]
        )

    def _to_dataset_metadata(
        self,
        resource_tag_mapping: Dict,
        s3_adapter: "S3Adapter",
        glue_adapter: "GlueAdapter",
    ) -> EnrichedDatasetMetaData:
        domain, dataset = self._infer_domain_and_dataset_from_crawler_arn(
            resource_tag_mapping["ResourceARN"]
        )
        tags = {tag["Key"]: tag["Value"] for tag in resource_tag_mapping["Tags"]}
        version = self.get_version_from_tags(resource_tag_mapping)
        senstivity = tags["sensitivity"]
        description = s3_adapter.get_dataset_description(
            domain, dataset, version, senstivity
        )
        metadata = StorageMetaData(domain, dataset, version, description)
        last_updated = glue_adapter.get_table_last_updated_date(
            metadata.glue_table_name(), supress_error=True
        )
        return self.EnrichedDatasetMetaData(
            **asdict(metadata), tags=tags, last_updated=last_updated
        )

    def get_version_from_tags(self, resource_tag_mapping):
        version_tag = [
            tag["Value"]
            for tag in resource_tag_mapping["Tags"]
            if tag["Key"] == "no_of_versions"
        ]
        return int(version_tag[0]) if version_tag else None

    def get_version_from_crawler_tags(self, domain: str, dataset: str) -> int:
        aws_resources = self._get_resources(["glue:crawler"], [])

        crawler_resource = None

        AppLogger.info(f"Getting version for domain {domain} and dataset {dataset}")
        for resource in aws_resources:
            if resource["ResourceARN"].endswith(
                f":crawler/{RESOURCE_PREFIX}_crawler/{domain}/{dataset}"
            ):
                crawler_resource = resource

        return self.get_version_from_tags(crawler_resource)

    def _infer_domain_and_dataset_from_crawler_arn(self, arn: str) -> Tuple[str, str]:
        table_name = arn.split(f"{RESOURCE_PREFIX}_crawler/")[-1]
        table_name_elements = table_name.split("/")
        return table_name_elements[0], table_name_elements[1]
