from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

from api.adapter.aws_resource_adapter import AWSResourceAdapter
from api.adapter.s3_adapter import S3Adapter
from api.common.config.aws import AWS_REGION, RESOURCE_PREFIX
from api.common.custom_exceptions import UserError, AWSServiceError
from api.domain.dataset_filters import DatasetFilters


class TestAWSResourceAdapterClientMethods:
    resource_boto_client = None
    aws_return_value = None

    def setup_method(self):
        self.resource_boto_client = Mock()
        self.mock_s3_client = Mock()
        self.resource_adapter = AWSResourceAdapter(self.resource_boto_client)
        self.s3_adapter = S3Adapter(s3_client=self.mock_s3_client, s3_bucket="dataset")
        self.aws_return_value = [
            {
                "PaginationToken": "xxxx",
                "ResponseMetadata": {"key": "value"},
                "ResourceTagMappingList": [
                    {
                        "ResourceARN": f"arn:aws:glue:{AWS_REGION}:123:crawler/{RESOURCE_PREFIX}_crawler/domain1/dataset1",
                        "Tags": [
                            {"Key": "sensitivity", "Value": "PUBLIC"},
                            {"Key": "no_of_versions", "Value": "1"},
                        ],
                    },
                    {
                        "ResourceARN": f"arn:aws:glue:{AWS_REGION}:123:crawler/{RESOURCE_PREFIX}_crawler/domain2/dataset2",
                        "Tags": [
                            {"Key": "tag1", "Value": ""},
                            {"Key": "sensitivity", "Value": "PUBLIC"},
                            {"Key": "no_of_versions", "Value": "2"},
                        ],
                    },
                    {
                        "ResourceARN": f"arn:aws:glue:{AWS_REGION}:123:crawler/{RESOURCE_PREFIX}_crawler/domain3/dataset",
                        "Tags": [
                            {"Key": "tag2", "Value": ""},
                            {"Key": "sensitivity", "Value": "PRIVATE"},
                            {"Key": "no_of_versions", "Value": "3"},
                        ],
                    },
                ],
            },
            {
                "PaginationToken": "xxxx",
                "ResponseMetadata": {"key": "value"},
                "ResourceTagMappingList": [
                    {
                        "ResourceARN": f"arn:aws:glue:{AWS_REGION}:123:crawler/FAKE_PREFIX_crawler/domain3/dataset3",
                        "Tags": [
                            {"Key": "tag5", "Value": ""},
                            {"Key": "sensitivity", "Value": "PUBLIC"},
                            {"Key": "no_of_versions", "Value": "1"},
                        ],
                    },
                    {
                        "ResourceARN": f"arn:aws:glue:{AWS_REGION}:123:crawler/{RESOURCE_PREFIX}_crawler/domain3/dataset3",
                        "Tags": [
                            {"Key": "tag5", "Value": ""},
                            {"Key": "sensitivity", "Value": "PUBLIC"},
                            {"Key": "no_of_versions", "Value": "1"},
                        ],
                    },
                    {
                        "ResourceARN": f"arn:aws:glue:{AWS_REGION}:123:crawler/FAKE_{RESOURCE_PREFIX}_crawler/domain36/dataset3",
                        "Tags": [
                            {"Key": "tag2", "Value": ""},
                            {"Key": "sensitivity", "Value": "PRIVATE"},
                            {"Key": "no_of_versions", "Value": "10"},
                        ],
                    },
                    {
                        "ResourceARN": f"arn:aws:glue:{AWS_REGION}:123:crawler/{RESOURCE_PREFIX}_crawler/domain36/dataset3",
                        "Tags": [
                            {"Key": "tag2", "Value": ""},
                            {"Key": "sensitivity", "Value": "PRIVATE"},
                            {"Key": "no_of_versions", "Value": "10"},
                        ],
                    },
                ],
            },
        ]

    def test_gets_all_datasets_metadata_for_specific_resource_when_query_is_empty(self):
        query = DatasetFilters()

        expected_metadatas = [
            AWSResourceAdapter.EnrichedDatasetMetaData(
                domain="domain1",
                dataset="dataset1",
                description="",
                tags={"sensitivity": "PUBLIC", "no_of_versions": "1"},
                version=1,
            ),
            AWSResourceAdapter.EnrichedDatasetMetaData(
                domain="domain2",
                dataset="dataset2",
                description="",
                tags={"tag1": "", "sensitivity": "PUBLIC", "no_of_versions": "2"},
                version=2,
            ),
            AWSResourceAdapter.EnrichedDatasetMetaData(
                domain="domain3",
                dataset="dataset",
                description="",
                tags={"tag2": "", "sensitivity": "PRIVATE", "no_of_versions": "3"},
                version=3,
            ),
            AWSResourceAdapter.EnrichedDatasetMetaData(
                domain="domain3",
                dataset="dataset3",
                description="",
                tags={"tag5": "", "sensitivity": "PUBLIC", "no_of_versions": "1"},
                version=1,
            ),
            AWSResourceAdapter.EnrichedDatasetMetaData(
                domain="domain36",
                dataset="dataset3",
                description="",
                tags={"tag2": "", "sensitivity": "PRIVATE", "no_of_versions": "10"},
                version=10,
            ),
        ]

        self.resource_boto_client.get_paginator.return_value.paginate.return_value = (
            self.aws_return_value
        )

        actual_metadatas = self.resource_adapter.get_datasets_metadata(
            self.s3_adapter, query
        )

        self.resource_boto_client.get_paginator.assert_called_once_with("get_resources")
        self.resource_boto_client.get_paginator.return_value.paginate.assert_called_once_with(
            ResourceTypeFilters=["glue:crawler"], TagFilters=[]
        )

        assert actual_metadatas == expected_metadatas

    def test_returns_empty_list_of_datasets_when_none_exist(self):
        query = DatasetFilters()

        self.resource_boto_client.get_paginator.return_value.paginate.return_value = {}

        actual_metadatas = self.resource_adapter.get_datasets_metadata(
            self.s3_adapter, query
        )

        self.resource_boto_client.get_paginator.assert_called_once_with("get_resources")
        self.resource_boto_client.get_paginator.return_value.paginate.assert_called_once_with(
            ResourceTypeFilters=["glue:crawler"], TagFilters=[]
        )

        assert len(actual_metadatas) == 0

    def test_calls_resource_client_with_correct_tag_filters(self):
        query = DatasetFilters(
            key_value_tags={
                "tag1": "value1",
                "tag2": None,
            }
        )

        self.resource_boto_client.get_paginator.return_value.paginate.return_value = {}

        self.resource_adapter.get_datasets_metadata(self.s3_adapter, query)

        self.resource_boto_client.get_paginator.assert_called_once_with("get_resources")
        self.resource_boto_client.get_paginator.return_value.paginate.assert_called_once_with(
            ResourceTypeFilters=["glue:crawler"],
            TagFilters=[
                {"Key": "tag1", "Values": ["value1"]},
                {"Key": "tag2", "Values": []},
            ],
        )

    def test_resource_client_returns_invalid_parameter_exception(self):
        query = DatasetFilters(
            tags={
                "tag1": "value1",
                "tag2": None,
            }
        )

        self.resource_boto_client.get_paginator.return_value.paginate.side_effect = (
            ClientError(
                error_response={"Error": {"Code": "InvalidParameterException"}},
                operation_name="GetResources",
            )
        )

        with pytest.raises(UserError, match="Wrong parameters sent to list datasets"):
            self.resource_adapter.get_datasets_metadata(self.s3_adapter, query)

    @pytest.mark.parametrize(
        "error_code",
        [
            ("ThrottledException",),
            ("InternalServiceException",),
            ("PaginationTokenExpiredException",),
            ("SomethingElse",),
        ],
    )
    def test_resource_client_returns_another_exception(self, error_code: str):
        query = DatasetFilters(
            tags={
                "tag1": "value1",
                "tag2": None,
            }
        )

        self.resource_boto_client.get_paginator.return_value.paginate.side_effect = (
            ClientError(
                error_response={"Error": {"Code": f"{error_code}"}},
                operation_name="GetResources",
            )
        )

        with pytest.raises(
            AWSServiceError,
            match="Internal server error, please contact system administrator",
        ):
            self.resource_adapter.get_datasets_metadata(self.s3_adapter, query)

    @pytest.mark.parametrize(
        "domain, dataset, expected_version",
        [
            ("domain1", "dataset1", 1),
            ("domain2", "dataset2", 2),
            ("domain3", "dataset", 3),
            ("domain3", "dataset3", 1),
            ("domain36", "dataset3", 10),
        ],
    )
    def test_get_version_from_crawler(self, domain, dataset, expected_version):

        self.resource_boto_client.get_paginator.return_value.paginate.return_value = (
            self.aws_return_value
        )

        actual_version = self.resource_adapter.get_version_from_crawler_tags(
            domain, dataset
        )

        assert actual_version == expected_version
