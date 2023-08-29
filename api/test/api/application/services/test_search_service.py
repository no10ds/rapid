from unittest.mock import Mock, call

import pytest
from botocore.exceptions import ClientError


from typing import List, Union

from api.adapter.athena_adapter import AthenaAdapter
from api.adapter.dynamodb_adapter import DynamoDBAdapter, ExpressionAttribute

from api.application.services.search_service import SearchService
from api.domain.search_metadata import SearchMetadata, MatchField
from api.domain.dataset_filters import DatasetFilters, SearchFilter


class TestSearchService:
    def setup_method(self):
        self.athena_adapter = Mock()
        self.dynamodb_adapter = Mock()
        self.search_service = SearchService(
            athena_adapter=self.athena_adapter,
            dynamodb_adapter=self.dynamodb_adapter,
        )

    def test_search_not_including_columns(self):
        self.search_service.search_columns = Mock()

        self.search_service.query_database_for_search_filter = Mock(
            side_effect=[
                self._generate_valid_search_metadatas(["dataset", "dataset_1"]),
                self._generate_valid_search_metadatas(["dataset_1", "dataset_3"]),
            ]
        )
        res = self.search_service.search("search_term")

        assert res == self._generate_valid_search_metadatas(
            ["dataset", "dataset_1", "dataset_3"]
        )
        self.search_service.search_columns.assert_not_called()
        self.search_service.query_database_for_search_filter.assert_has_calls(
            [
                call(SearchFilter(name=MatchField.Dataset, value="search_term")),
                call(SearchFilter(name=MatchField.Description, value="search_term")),
            ]
        )

    def test_search_including_columns(self):
        self.search_service.search_columns = Mock(
            return_value=self._generate_valid_search_metadatas(
                ["dataset_3", "dataset_4"]
            )
        )
        self.search_service.query_database_for_search_filter = Mock(
            side_effect=[
                self._generate_valid_search_metadatas(["dataset", "dataset_1"]),
                self._generate_valid_search_metadatas(["dataset_1", "dataset_3"]),
            ]
        )

        res = self.search_service.search("search_term", include_columns=True)

        assert res == self._generate_valid_search_metadatas(
            ["dataset", "dataset_1", "dataset_3", "dataset_4"]
        )
        self.search_service.search_columns.assert_called_once_with("search_term")
        self.search_service.query_database_for_search_filter.assert_has_calls(
            [
                call(SearchFilter(name=MatchField.Dataset, value="search_term")),
                call(SearchFilter(name=MatchField.Description, value="search_term")),
            ]
        )

    def test_search_no_result(self):
        self.search_service.search_columns = Mock(return_value=[])
        self.search_service.query_database_for_search_filter = Mock(
            side_effect=[[], []]
        )

        res = self.search_service.search("search_term", include_columns=True)

        assert res == []
        self.search_service.search_columns.assert_called_once_with("search_term")
        self.search_service.query_database_for_search_filter.assert_has_calls(
            [
                call(SearchFilter(name=MatchField.Dataset, value="search_term")),
                call(SearchFilter(name=MatchField.Description, value="search_term")),
            ]
        )

    def _generate_valid_search_metadatas(self, datasets: List[str]):
        return [
            SearchMetadata(
                layer="raw",
                domain="domain",
                dataset=dataset,
                version=1,
                matching_data="dataset",
                matching_field=MatchField.Dataset,
            )
            for dataset in datasets
        ]

    def test_query_database_for_search_filter_returns_nothing(self):
        self.dynamodb_adapter.get_latest_schemas.return_value = []
        res = self.search_service.query_database_for_search_filter(
            SearchFilter(name="Dataset", value="data")
        )

        assert res == []
        self.dynamodb_adapter.get_latest_schemas.assert_called_once_with(
            DatasetFilters(search_filter=SearchFilter(name="Dataset", value="data"))
        )

    def test_query_database_for_search_filter(self):
        self.dynamodb_adapter.get_latest_schemas.return_value = [
            {
                "Layer": "raw",
                "Domain": "domain",
                "Dataset": "dataset",
                "Version": 1,
            },
            {
                "Layer": "raw",
                "Domain": "domain",
                "Dataset": "other_dataset",
                "Version": 2,
            },
        ]

        expected = [
            SearchMetadata(
                layer="raw",
                domain="domain",
                dataset="dataset",
                version=1,
                matching_data="dataset",
                matching_field=MatchField.Dataset,
            ),
            SearchMetadata(
                layer="raw",
                domain="domain",
                dataset="other_dataset",
                version=2,
                matching_data="other_dataset",
                matching_field=MatchField.Dataset,
            ),
        ]

        res = self.search_service.query_database_for_search_filter(
            SearchFilter(name="Dataset", value="data")
        )

        assert res == expected
        self.dynamodb_adapter.get_latest_schemas.assert_called_once_with(
            DatasetFilters(search_filter=SearchFilter(name="Dataset", value="data"))
        )

    def test_search_columns(self):
        self.dynamodb_adapter.get_latest_schemas.return_value = [
            {
                "Layer": "raw",
                "Domain": "domain",
                "Dataset": "dataset",
                "Version": 1,
                "Columns": [
                    {"name": "postcode_long"},
                    {"name": "postcode_short"},
                    {"name": "other"},
                ],
            },
            {
                "Layer": "raw",
                "Domain": "domain",
                "Dataset": "other_dataset",
                "Version": 2,
                "Columns": [{"name": "column1"}, {"name": "column2"}],
            },
        ]

        expected = SearchMetadata(
            layer="raw",
            domain="domain",
            dataset="dataset",
            version=1,
            matching_data=["postcode_long", "postcode_short"],
            matching_field=MatchField.Columns,
        )

        res = self.search_service.search_columns("postcode")

        assert res == [expected]
        self.dynamodb_adapter.get_latest_schemas.assert_called_once_with(
            attributes=[
                ExpressionAttribute("Layer", "L"),
                ExpressionAttribute("Domain", "Do"),
                ExpressionAttribute("Dataset", "Da"),
                ExpressionAttribute("Version", "V"),
                ExpressionAttribute("Columns", "C"),
            ]
        )

    def test_search_columns_no_result(self):
        self.dynamodb_adapter.get_latest_schemas.return_value = []

        res = self.search_service.search_columns("postcode")

        assert res == []

    def test_remove_duplicates_from_search_results(self):
        to_keep = [
            SearchMetadata(
                layer="raw",
                domain="domain",
                dataset="dataset",
                version=1,
                matching_data="data",
                matching_field=MatchField.Dataset,
            ),
            SearchMetadata(
                layer="raw",
                domain="domain",
                dataset="other_dataset",
                version=1,
                matching_data="data",
                matching_field=MatchField.Dataset,
            ),
        ]
        to_remove = [
            SearchMetadata(
                layer="raw",
                domain="domain",
                dataset="dataset",
                version=2,
                matching_data="data",
                matching_field=MatchField.Description,
            ),
        ]
        search_results = to_keep + to_remove

        res = self.search_service.remove_duplicates_from_search_results(search_results)

        assert res == to_keep

    def test_convert_item_to_search_metadata(self):
        item = {
            "Layer": "raw",
            "Domain": "domain",
            "Dataset": "dataset",
            "Version": 1,
        }

        res = self.search_service.convert_item_to_search_metadata(
            item, MatchField.Dataset, ["data"]
        )

        assert res == SearchMetadata(
            layer="raw",
            domain="domain",
            dataset="dataset",
            version=1,
            matching_data=["data"],
            matching_field=MatchField.Dataset,
        )
