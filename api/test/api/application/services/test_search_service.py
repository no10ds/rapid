from unittest.mock import Mock, call
from typing import List, Union

import pytest
from botocore.exceptions import ClientError
from pandas import DataFrame
from pandas.testing import assert_frame_equal
import numpy as np

from api.adapter.athena_adapter import AthenaAdapter
from api.adapter.dynamodb_adapter import DynamoDBAdapter, ExpressionAttribute

from api.application.services.search_service import (
    SearchService,
    MATCHING_DATA,
    MATCHING_FIELD,
)
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

    def test_search(self):
        mock_df = DataFrame(
            data=[
                [
                    "raw",
                    "domain",
                    "dataset",
                    1,
                    "No description",
                    [
                        {"name": "postcode"},
                    ],
                ]
            ],
            columns=[self.search_service.input_columns],
        )
        self.search_service.fetch_schema_data = Mock(return_value=mock_df)

        res = self.search_service.search("desc")

        assert res == [
            SearchMetadata(
                layer="raw",
                domain="domain",
                dataset="dataset",
                version=1,
                matching_field=MatchField.Description,
                matching_data="No description",
            )
        ]

    def test_search_no_result(self):
        mock_df = DataFrame(data=[], columns=self.search_service.input_columns)
        self.search_service.fetch_schema_data = Mock(return_value=mock_df)

        res = self.search_service.search("search_term")

        assert res == []

    def test_generate_expression_attributes(self):
        res = self.search_service._generate_expression_attributes()

        assert res == [
            ExpressionAttribute("Layer", "La"),
            ExpressionAttribute("Domain", "Do"),
            ExpressionAttribute("Dataset", "Da"),
            ExpressionAttribute("Version", "Ve"),
            ExpressionAttribute("Description", "De"),
            ExpressionAttribute("Columns", "Co"),
        ]

    def test_generate_expression_attributes_values_are_unique(self):
        attributes = self.search_service._generate_expression_attributes()
        assert len(attributes) == len(
            set([attribute.alias for attribute in attributes])
        )

    def test_find_matches(self):
        input_data = [
            # Column match
            [
                "raw",
                "domain",
                "dataset",
                1,
                [
                    {"name": "postcode"},
                ],
                "No description",
            ],
            # Description match
            [
                "raw",
                "domain",
                "dataset_2",
                3,
                [{"name": "column1"}],
                "Includes the postcode",
            ],
            # Dataset match
            [
                "raw",
                "domain",
                "dataset_postcode",
                4,
                [{"name": "column1"}],
                "No description",
            ],
            # Matches all
            [
                "raw",
                "domain",
                "dataset_postcode_2",
                1,
                [{"name": "postcode"}],
                "Include the postcode",
            ],
        ]
        input_columns = self.search_service.input_columns
        input_df = DataFrame(columns=input_columns, data=input_data)

        expected_data = [
            input_data[0][0:4] + [["postcode"], MatchField.Columns],
            input_data[1][0:4] + ["Includes the postcode", MatchField.Description],
            input_data[2][0:4] + ["dataset_postcode", MatchField.Dataset],
            input_data[3][0:4] + ["dataset_postcode_2", MatchField.Dataset],
        ]
        expected_columns = input_columns[0:4] + [MATCHING_DATA, MATCHING_FIELD]
        expected_df = DataFrame(columns=expected_columns, data=expected_data)

        res = self.search_service.find_matches(input_df, "postcode")

        assert_frame_equal(res, expected_df)

    def test_produce_generic_matches(self):
        input_data = [
            ["raw", "domain", "dataset", 2],
            ["raw", "domain", "other_dataset", 3],
        ]
        input_columns = [
            "Layer",
            "Domain",
            "Dataset",
            "Version",
        ]

        input_df = DataFrame(
            columns=input_columns,
            data=input_data,
        )

        expected_data = [
            input_data[1] + ["other_dataset", MatchField.Dataset],
        ]
        expected_columns = input_columns + [MATCHING_DATA, MATCHING_FIELD]
        expected_df = DataFrame(
            columns=expected_columns,
            data=expected_data,
        )
        res = self.search_service.produce_generic_matches(
            "OTHER", MatchField.Dataset, input_df
        )
        res.reset_index(inplace=True, drop=True)

        assert_frame_equal(res, expected_df, check_dtype=False)

    def test_produce_column_matches(self):
        input_data = [
            [
                "raw",
                "domain",
                "dataset",
                1,
                [
                    {"name": "postcode_long"},
                    {"name": "postcode_short"},
                    {"name": "other"},
                ],
            ],
            [
                "raw",
                "domain",
                "other_dataset",
                2,
                [{"name": "column1"}, {"name": "column2"}],
            ],
        ]
        input_columns = ["Layer", "Domain", "Dataset", "Version", "Columns"]

        input_df = DataFrame(
            columns=input_columns,
            data=input_data,
        )

        expected_data = [
            input_data[0][0:4] + [["postcode_long", "postcode_short"], "Columns"],
        ]
        expected_columns = input_columns[0:4] + [MATCHING_DATA, MATCHING_FIELD]
        expected_df = DataFrame(
            columns=expected_columns,
            data=expected_data,
        )

        res = self.search_service.produce_column_matches("POSTCODE", input_df)
        assert_frame_equal(res, expected_df)

    def test_convert_dataframe_to_search_metadata(self):
        input_data = [
            [
                "raw",
                "domain",
                "dataset",
                1,
                ["postcode"],
                "Columns",
            ],
            [
                "raw",
                "domain",
                "other_dataset",
                2,
                "postcode data",
                "Description",
            ],
        ]
        input_columns = [
            "Layer",
            "Domain",
            "Dataset",
            "Version",
            MATCHING_DATA,
            MATCHING_FIELD,
        ]

        input_df = DataFrame(data=input_data, columns=input_columns)
        res = self.search_service.convert_dataframe_to_search_metadata(input_df)

        assert res == [
            SearchMetadata(
                layer="raw",
                domain="domain",
                dataset="dataset",
                version=1,
                matching_data=["postcode"],
                matching_field=MatchField.Columns,
            ),
            SearchMetadata(
                layer="raw",
                domain="domain",
                dataset="other_dataset",
                version=2,
                matching_data="postcode data",
                matching_field=MatchField.Description,
            ),
        ]

    def test_fetch_data(self):
        mock_data = [
            {
                "Layer": "raw",
                "Domain": "domain",
                "Dataset": "dataset",
                "Version": 1,
                "Description": "A description",
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
                "Description": "A description",
                "Columns": [{"name": "column1"}, {"name": "column2"}],
            },
        ]
        self.dynamodb_adapter.get_latest_schemas.return_value = mock_data
        expected = DataFrame(mock_data)

        res = self.search_service.fetch_schema_data()

        assert_frame_equal(res, expected)
        self.dynamodb_adapter.get_latest_schemas.assert_called_once_with(
            attributes=[
                ExpressionAttribute("Layer", "La"),
                ExpressionAttribute("Domain", "Do"),
                ExpressionAttribute("Dataset", "Da"),
                ExpressionAttribute("Version", "Ve"),
                ExpressionAttribute("Description", "De"),
                ExpressionAttribute("Columns", "Co"),
            ]
        )

    def test_fetch_schema_data_when_empty(self):
        mock_data = []
        self.dynamodb_adapter.get_latest_schemas.return_value = mock_data
        expected = DataFrame(
            data=[],
            columns=["Layer", "Domain", "Dataset", "Version", "Description", "Columns"],
        )

        res = self.search_service.fetch_schema_data()

        assert_frame_equal(res, expected)
        self.dynamodb_adapter.get_latest_schemas.assert_called_once_with(
            attributes=[
                ExpressionAttribute("Layer", "La"),
                ExpressionAttribute("Domain", "Do"),
                ExpressionAttribute("Dataset", "Da"),
                ExpressionAttribute("Version", "Ve"),
                ExpressionAttribute("Description", "De"),
                ExpressionAttribute("Columns", "Co"),
            ]
        )
