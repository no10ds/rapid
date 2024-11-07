import pytest
from pydantic import ValidationError

from rapid.items.schema import Schema, Column
from rapid.items.schema_metadata import (
    SchemaMetadata,
    SensitivityLevel,
    Owner,
    UpdateBehaviour,
)


DUMMY_COLUMNS = [
    Column(
        name="column_a",
        partition_index=None,
        data_type="object",
        allow_null=True,
        format=None,
    ),
    Column(
        name="column_b",
        partition_index=None,
        data_type="object",
        allow_null=True,
        format=None,
    ),
]

DUMMY_COLUMNS_TWO = [
    Column(
        name="column_c",
        partition_index=None,
        data_type="Float64",
        allow_null=True,
        format=None,
    )
]


DUMMY_METADATA = SchemaMetadata(
    layer="raw",
    domain="test",
    dataset="rapid_sdk",
    sensitivity=SensitivityLevel.PUBLIC,
    owners=[Owner(name="Test", email="test@email.com")],
    description="test",
    update_behaviour="OVERWRITE",
    is_latest_version=True,
)


@pytest.fixture
def schema():
    return Schema(metadata=DUMMY_METADATA, columns=DUMMY_COLUMNS)


class TestOwnder:
    def test_create_owner_from_dict(self):
        _owner = {"name": "test", "email": "test@email.com"}
        owner = Owner(**_owner)
        assert owner.name == "test"
        assert owner.email == "test@email.com"


class TestSchemaMetadata:
    def test_create_schema_metadata_from_dict(self):
        _schema_metadata = {
            "layer": "raw",
            "domain": "test",
            "dataset": "rapid_sdk",
            "sensitivity": SensitivityLevel.PUBLIC,
            "owners": [{"name": "Test", "email": "test@email.com"}],
            "description": "test",
            "update_behaviour": "OVERWRITE",
            "is_latest_version": True,
        }

        schema_metadata = SchemaMetadata(**_schema_metadata)
        assert schema_metadata.domain == "test"
        assert schema_metadata.dataset == "rapid_sdk"
        assert schema_metadata.sensitivity == "PUBLIC"
        assert schema_metadata.owners == [Owner(name="Test", email="test@email.com")]
        assert schema_metadata.description == "test"
        assert schema_metadata.update_behaviour == "OVERWRITE"
        assert schema_metadata.is_latest_version == True


class TestColumn:
    def test_create_columns_from_dict(self):
        _column = {
            "name": "column_a",
            "partition_index": None,
            "data_type": "object",
            "allow_null": True,
            "format": None,
        }

        column = Column(**_column)
        assert column.name == "column_a"
        assert column.partition_index is None
        assert column.data_type == "object"
        assert column.allow_null is True
        assert column.format is None

    def test_create_columns_fails_name_none(self):
        _column = {
            "partition_index": None,
            "data_type": "object",
            "allow_null": True,
            "format": None,
        }

        with pytest.raises(ValidationError) as exc_info:
            Column(**_column)

        expected_error = {
            "input": {
                "partition_index": None,
                "data_type": "object",
                "allow_null": True,
                "format": None,
            },
            "loc": ("name",),
            "msg": "Field required",
            "type": "missing",
        }

        assert len(exc_info.value.errors()) == 1

        actual_error = exc_info.value.errors()[0]
        for key, value in expected_error.items():
            assert actual_error[key] == value

    def test_create_columns_fails_data_type_none(self):
        _column = {
            "name": "column_a",
            "partition_index": None,
            "allow_null": True,
            "format": None,
        }

        with pytest.raises(ValidationError) as exc_info:
            Column(**_column)

        expected_error = {
            "input": {
                "name": "column_a",
                "partition_index": None,
                "allow_null": True,
                "format": None,
            },
            "loc": ("data_type",),
            "msg": "Field required",
            "type": "missing",
        }

        assert len(exc_info.value.errors()) == 1

        actual_error = exc_info.value.errors()[0]
        for key, value in expected_error.items():
            assert actual_error[key] == value

    def test_returns_dictionary_of_model(self):
        _column = {
            "name": "column_a",
            "partition_index": None,
            "data_type": "object",
            "allow_null": True,
            "format": None,
        }

        column = Column(
            name="column_a",
            allow_null=True,
            data_type="object",
            format=None,
            partition_index=None,
        )
        assert column.dict() == _column


class TestSchema:
    def test_format_columns_when_dict(self):
        _input = [
            {
                "name": "column_a",
                "partition_index": None,
                "data_type": "object",
                "allow_null": True,
                "format": None,
            },
            {
                "name": "column_b",
                "partition_index": None,
                "data_type": "object",
                "allow_null": True,
                "format": None,
            },
        ]

        expected = DUMMY_COLUMNS
        schema = Schema(metadata=DUMMY_METADATA, columns=_input)

        assert schema.columns == expected

    def test_format_columns_when_columns(self):
        schema = Schema(metadata=DUMMY_METADATA, columns=DUMMY_COLUMNS)
        assert schema.columns == DUMMY_COLUMNS

    def test_format_columns_when_neither_valid(self):
        _input = [
            1234,
            1234,
        ]

        with pytest.raises(ValidationError):
            Schema(metadata=None, columns=_input)

    def test_reset_columns(self):
        schema = Schema(metadata=DUMMY_METADATA, columns=DUMMY_COLUMNS)
        assert schema.columns == DUMMY_COLUMNS
        schema.columns = DUMMY_COLUMNS_TWO
        assert schema.columns == DUMMY_COLUMNS_TWO

    def test_are_columns_the_same_passes(self):
        schema = Schema(metadata=DUMMY_METADATA, columns=DUMMY_COLUMNS)
        same = schema.are_columns_the_same(DUMMY_COLUMNS)
        assert same is True

    def test_are_columns_the_same_for_dict_passes(self):
        columns = [
            {
                "name": "column_a",
                "partition_index": None,
                "data_type": "object",
                "allow_null": True,
                "format": None,
            },
            {
                "name": "column_b",
                "partition_index": None,
                "data_type": "object",
                "allow_null": True,
                "format": None,
            },
        ]
        schema = Schema(metadata=DUMMY_METADATA, columns=DUMMY_COLUMNS)
        same = schema.are_columns_the_same(columns)
        assert same is True

    def test_are_columns_the_same_fails(self):
        schema = Schema(metadata=DUMMY_METADATA, columns=DUMMY_COLUMNS)
        same = schema.are_columns_the_same(DUMMY_COLUMNS_TWO)
        assert same is False

    def test_are_columns_the_same_for_dict_fails(self):
        columns = [
            {
                "name": "column_c",
                "partition_index": None,
                "data_type": "Float64",
                "allow_null": True,
                "format": None,
            }
        ]
        schema = Schema(metadata=DUMMY_METADATA, columns=DUMMY_COLUMNS)
        same = schema.are_columns_the_same(columns)
        assert same is False

    def test_schema_returns_correct_dictionary(self):
        schema = Schema(metadata=DUMMY_METADATA, columns=DUMMY_COLUMNS)
        expected_dict = {
            "metadata": {
                "layer": "raw",
                "domain": "test",
                "dataset": "rapid_sdk",
                "sensitivity": SensitivityLevel.PUBLIC,
                "description": "",
                "update_behaviour": UpdateBehaviour.APPEND,
                "owners": [{"name": "Test", "email": "test@email.com"}],
                "version": None,
                "key_value_tags": {},
                "key_only_tags": [],
                "description": "test",
                "update_behaviour": "OVERWRITE",
                "is_latest_version": True,
            },
            "columns": [
                {
                    "name": "column_a",
                    "data_type": "object",
                    "partition_index": None,
                    "allow_null": True,
                    "format": None,
                },
                {
                    "name": "column_b",
                    "data_type": "object",
                    "partition_index": None,
                    "allow_null": True,
                    "format": None,
                },
            ],
        }
        assert schema.dict() == expected_dict
