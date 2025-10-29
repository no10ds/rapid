from typing import List

import pandas as pd

from api.application.services.partitioning_service import (
    Partition,
    generate_path,
    drop_columns,
    generate_partitioned_data,
)
from api.domain.schema import Schema
from rapid.items.schema import Column
from api.domain.schema_metadata import Owner, SchemaMetadata


class TestPartitioningUtilities:
    def test_generate_path(self):
        partitions = ["first", "second", "third"]
        group_info = (123, 456, 789)
        result = generate_path(partitions, group_info)
        expected = "first=123/second=456/third=789"
        assert result == expected


class TestDropColumns:
    def test_drops_columns(self):
        columns_to_drop = ["to_drop", "to_drop_too"]

        df = pd.DataFrame(
            {
                "col1": [1, 2, 3],
                "to_drop": [1, 2, 3],
                "to_drop_too": [1, 2, 3],
            }
        )

        expected = pd.DataFrame({"col1": [1, 2, 3]})

        result = drop_columns(df, columns_to_drop)

        assert result.equals(expected)


class TestPartitioning:
    def test_generates_partitioned_data(self):
        # Forcing Int64 for testing purposes as parsing & validation should occur before partitioning # noqa E501
        column_dtype = "Int64"

        schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="test_domain",
                dataset="test_dataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="change_me", email="change_me@email.com")],
            ),
            columns=[
                Column(
                    name="col1",
                    partition_index=0,
                    data_type=column_dtype,
                    allow_null=False,
                ),
                Column(
                    name="col2",
                    partition_index=None,
                    data_type=column_dtype,
                    allow_null=True,
                ),
                Column(
                    name="col3",
                    partition_index=1,
                    data_type=column_dtype,
                    allow_null=False,
                ),
            ],
        )

        df = pd.DataFrame(
            {
                "col1": [1, 1, 2, 2],
                "col2": [4, 5, 6, None],
                "col3": [7, 8, 9, 2],
            },
            dtype=column_dtype,
        )

        expected = [
            Partition(
                keys=[1, 7],
                path="col1=1/col3=7",
                df=pd.DataFrame({"col2": [4]}, dtype=column_dtype),
            ),
            Partition(
                keys=[1, 8],
                path="col1=1/col3=8",
                df=pd.DataFrame({"col2": [5]}, dtype=column_dtype),
            ),
            Partition(
                keys=[2, 2],
                path="col1=2/col3=2",
                df=pd.DataFrame({"col2": [pd.NA]}, dtype=column_dtype),
            ),
            Partition(
                keys=[2, 9],
                path="col1=2/col3=9",
                df=pd.DataFrame({"col2": [6]}, dtype=column_dtype),
            ),
        ]

        actual = generate_partitioned_data(schema, df)
        self.assert_partitions_are_the_same(expected, actual)

    def test_handles_one_partition(self):
        # Forcing Int64 for testing purposes as parsing & validation should occur before partitioning # noqa E501
        column_dtype = "Int64"

        schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="test_domain",
                dataset="test_dataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="change_me", email="change_me@email.com")],
            ),
            columns=[
                Column(
                    name="col1",
                    partition_index=0,
                    data_type=column_dtype,
                    allow_null=False,
                ),
                Column(
                    name="col2",
                    partition_index=None,
                    data_type=column_dtype,
                    allow_null=True,
                ),
            ],
        )

        df = pd.DataFrame({"col1": [1, 1, 2, 2], "col2": [4, 5, 6, 2]})

        df1 = pd.DataFrame({"col2": [4, 5]})
        df2 = pd.DataFrame({"col2": [6, 2]})

        expected = [
            Partition(keys=[1], path="col1=1", df=df1),
            Partition(keys=[2], path="col1=2", df=df2),
        ]

        actual = generate_partitioned_data(schema, df)
        self.assert_partitions_are_the_same(expected, actual)

    def test_handles_no_partitions(self):
        # Forcing Int64 for testing purposes as parsing & validation should occur before partitioning # noqa E501
        column_dtype = "int"

        schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="test_domain",
                dataset="test_dataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="change_me", email="change_me@email.com")],
            ),
            columns=[
                Column(
                    name="col1",
                    partition_index=None,
                    data_type=column_dtype,
                    allow_null=False,
                ),
                Column(
                    name="col2",
                    partition_index=None,
                    data_type=column_dtype,
                    allow_null=True,
                ),
            ],
        )

        df = pd.DataFrame({"col1": [1, 1, 2, 2], "col2": [4, 5, 6, 2]})

        expected = [Partition(df=df)]
        actual = generate_partitioned_data(schema, df)
        self.assert_partitions_are_the_same(expected, actual)

    def assert_partitions_are_the_same(
        self, expected: List[Partition], actual: List[Partition]
    ):
        test_combos = zip(actual, expected)
        for actual_partition, expected_partition in test_combos:
            assert actual_partition.df.to_dict() == expected_partition.df.to_dict()
            assert actual_partition.path == expected_partition.path
            assert actual_partition.keys == expected_partition.keys
