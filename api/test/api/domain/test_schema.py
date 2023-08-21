from unittest.mock import Mock
import pytest

from api.adapter.s3_adapter import S3Adapter
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata
from api.domain.data_types import BooleanType, NumericType, StringType


class TestSchema:
    def setup_method(self):
        self.schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="test_domain",
                dataset="test_dataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=1,
                    data_type="int",
                    allow_null=True,
                ),
                Column(
                    name="colname2",
                    partition_index=0,
                    data_type="string",
                    allow_null=False,
                ),
                Column(
                    name="colname3",
                    partition_index=None,
                    data_type="boolean",
                    allow_null=False,
                ),
            ],
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
            Column(
                name="colname2",
                partition_index=0,
                data_type="string",
                allow_null=False,
                format=None,
            ),
            Column(
                name="colname1",
                partition_index=1,
                data_type="int",
                allow_null=True,
                format=None,
            ),
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


class TestSchemaMetadata:
    def setup_method(self):
        self.mock_s3_client = Mock()
        self.s3_adapter = S3Adapter(s3_client=self.mock_s3_client, s3_bucket="dataset")

    def test_schema_version(self):
        schema_metadata = SchemaMetadata(
            layer="raw",
            domain="domain",
            dataset="dataset",
            sensitivity="PUBLIC",
            version=3,
            owners=[Owner(name="owner", email="owner@email.com")],
        )
        assert schema_metadata.get_version() == 3

    def test_schema_for_default_version(self):
        schema_metadata = SchemaMetadata(
            layer="raw",
            domain="domain",
            dataset="dataset",
            sensitivity="PUBLIC",
            owners=[Owner(name="owner", email="owner@email.com")],
        )
        assert schema_metadata.get_version() is None

    def test_initialises_with_default_tags_when_no_tags_provided(self):
        result = SchemaMetadata(
            layer="raw",
            domain="domain",
            dataset="dataset",
            sensitivity="PUBLIC",
            version=1,
            owners=[Owner(name="owner", email="owner@email.com")],
        )

        assert result.get_tags() == {
            "no_of_versions": "1",
            "sensitivity": "PUBLIC",
            "layer": "raw",
            "domain": "domain",
        }

    def test_gets_tags(self):
        provided_key_value_tags = {
            "tag1_key": "tag1_value",
            "tag2_key": "tag2_value",
            "tag3_key": "tag3_value",
        }
        provided_key_only_tags = ["tag4_key", "tag5_key"]

        result = SchemaMetadata(
            layer="raw",
            domain="domain",
            dataset="dataset",
            sensitivity="PUBLIC",
            version=2,
            owners=[Owner(name="owner", email="owner@email.com")],
            key_value_tags=provided_key_value_tags,
            key_only_tags=provided_key_only_tags,
        )

        assert result.get_tags() == {
            "no_of_versions": "2",
            **provided_key_value_tags,
            **dict.fromkeys(provided_key_only_tags, ""),
            "sensitivity": "PUBLIC",
            "domain": "domain",
            "layer": "raw",
        }
