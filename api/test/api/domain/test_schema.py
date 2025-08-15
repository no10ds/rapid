from unittest.mock import Mock

import pyarrow as pa
import pytest

from api.adapter.s3_adapter import S3Adapter
from api.domain.schema import Schema, Column, Owner
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.data_types import BooleanType, NumericType, StringType


class TestSchema:
    def setup_method(self):
        self.schema = Schema(
            dataset_metadata=DatasetMetadata(
                layer="raw",
                domain="test_domain",
                dataset="test_dataset",
                version=1,
            ),
            sensitivity="PUBLIC",
            owners=[Owner(name="owner", email="owner@email.com")],
            columns={
                "colname1": Column(
                    name="colname1",
                    partition_index=1,
                    data_type="int",
                    allow_null=True,
                ),
                "colname2": Column(
                    name="colname2",
                    partition_index=0,
                    data_type="string",
                    allow_null=False,
                ),
                "colname3": Column(
                    name="colname3",
                    partition_index=None,
                    data_type="boolean",
                    allow_null=False,
                ),
            },
        )

    def test_gets_column_names(self):
        expected_column_names = ["colname1", "colname2", "colname3"]

        actual_column_names = self.schema.get_column_names()

        assert actual_column_names == expected_column_names

    def test_gets_partitions(self):
        expected_columns = ["colname2", "colname1"]

        actual_columns = self.schema.get_partitions()

        assert actual_columns == expected_columns

    def test_gets_partition_numbers(self):
        expected_partitions_numbers = [0, 1]

        actual_partitions_numbers = self.schema.get_partition_indexes()

        assert actual_partitions_numbers == expected_partitions_numbers

    def test_get_data_types(self):
        expected_data_types = {"int", "string", "boolean"}

        actual_data_types = self.schema.get_data_types()

        assert actual_data_types == expected_data_types

    def test_get_partition_columns(self):
        res = self.schema.get_partition_columns()
        expected = [
            {"colname2", Column(
                name="colname2",
                partition_index=0,
                data_type="string",
                allow_null=False,
                format=None,
            )},
            {"colname1", Column(
                name="colname1",
                partition_index=1,
                data_type="int",
                allow_null=True,
                format=None,
            )},
        ]
        assert res == expected

    def test_get_partition_columns_for_glue(self):
        res = self.schema.get_partition_columns_for_glue()
        expected = [
            {
                "Name": "colname2",
                "Type": "string",
            },
            {"Name": "colname1", "Type": "int"},
        ]

        assert res == expected

    def test_get_non_partition_columns_for_glue(self):
        res = self.schema.get_non_partition_columns_for_glue()
        expected = [
            {
                "Name": "colname3",
                "Type": "boolean",
            },
        ]
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            (BooleanType, ["colname3"]),
            (NumericType, ["colname1"]),
            (StringType, ["colname2"]),
        ],
    )
    def test_get_column_names_by_type(self, type, expected):
        res = self.schema.get_column_names_by_type(type)
        assert res == expected

    def test_generates_storage_schema(self):
        res = self.schema.generate_storage_schema()

        expected = pa.schema(
            [
                pa.field("colname1", pa.int32()),
                pa.field("colname2", pa.string()),
                pa.field("colname3", pa.bool_()),
            ]
        )
        assert res == expected
