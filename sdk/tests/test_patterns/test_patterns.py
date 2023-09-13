from mock import Mock, patch
import pytest
from pandas import DataFrame
from requests_mock import Mocker

from rapid.items.schema import Owner, SchemaMetadata, SensitivityLevel, Column
from rapid.patterns.data import upload_and_create_dataframe, update_schema_dataframe
from rapid.exceptions import (
    ColumnNotDifferentException,
    DataFrameUploadValidationException,
)
from rapid import Rapid
from tests.conftest import RAPID_URL

metadata = SchemaMetadata(
    layer="raw",
    domain="test",
    dataset="rapid_sdk",
    sensitivity=SensitivityLevel.PUBLIC,
    owners=[Owner(name="test", email="test@email.com")],
)

mock_response = {
    "metadata": {
        "layer": "raw",
        "domain": "test",
        "dataset": "rapid_sdk",
        "sensitivity": "PUBLIC",
        "key_value_tags": {},
        "key_only_tags": [],
        "owners": [{"name": "change_me", "email": "change_me@email.com"}],
        "update_behaviour": "APPEND",
    },
    "columns": [
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
        {
            "name": "column_c",
            "partition_index": None,
            "data_type": "object",
            "allow_null": True,
            "format": None,
        },
    ],
}

mock_failed_response = {"details": "dummy"}

df = DataFrame(
    {
        "column_a": ["one", "two", "three"],
        "column_b": ["one", "two", "three"],
        "column_c": ["one", "two", "three"],
    }
)


class TestUtils:
    def test_upload_and_create_dataframe(self, requests_mock: Mocker, rapid: Rapid):
        requests_mock.post(
            f"{RAPID_URL}/schema/{metadata.layer}/{metadata.sensitivity}/{metadata.domain}"
            + f"/{metadata.dataset}/generate",
            json=mock_response,
        )
        requests_mock.post(
            f"{RAPID_URL}/schema",
        )
        rapid.upload_dataframe = Mock()
        upload_and_create_dataframe(rapid, metadata, df)

        rapid.upload_dataframe.assert_called_once_with(
            metadata.layer, metadata.domain, metadata.dataset, df
        )

    def test_upload_and_create_dataframe_fails(
        self, requests_mock: Mocker, rapid: Rapid
    ):
        requests_mock.post(
            f"{RAPID_URL}/schema/{metadata.layer}/{metadata.sensitivity}/{metadata.domain}"
            + f"/{metadata.dataset}/generate",
            json=mock_response,
        )
        requests_mock.post(f"{RAPID_URL}/schema")
        rapid.upload_dataframe = Mock(side_effect=DataFrameUploadValidationException)

        with pytest.raises(DataFrameUploadValidationException):
            upload_and_create_dataframe(rapid, metadata, df)

    @patch("rapid.patterns.data.update_schema_dataframe")
    def test_upload_and_create_dataframe_upgrade_schema_on_fail(
        self, mocked_update_schema_dataframe, requests_mock: Mocker, rapid: Rapid
    ):
        requests_mock.post(
            f"{RAPID_URL}/schema/{metadata.layer}/{metadata.sensitivity}/{metadata.domain}"
            + f"/{metadata.dataset}/generate",
            json=mock_response,
        )
        requests_mock.post(f"{RAPID_URL}/schema")
        rapid.upload_dataframe = Mock(side_effect=DataFrameUploadValidationException)

        upload_and_create_dataframe(rapid, metadata, df, upgrade_schema_on_fail=True)
        mocked_update_schema_dataframe.assert_called_once()

    def test_update_schema_dataframe(self, requests_mock: Mocker, rapid: Rapid):
        new_columns = [
            Column(
                name="column_a",
                partition_index=None,
                data_type="float64",  # NOTE: Change in data type for column
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
            Column(
                name="column_c",
                partition_index=None,
                data_type="object",
                allow_null=True,
                format=None,
            ),
        ]
        requests_mock.get(
            f"{RAPID_URL}/datasets/{metadata.layer}/{metadata.domain}/{metadata.dataset}/info",
            json=mock_response,
        )
        requests_mock.put(f"{RAPID_URL}/schema", json={"dummy": "data"})
        update_schema_dataframe(rapid, metadata, new_columns)

    def test_update_schema_dataframe_fail(self, requests_mock: Mocker, rapid: Rapid):
        requests_mock.get(
            f"{RAPID_URL}/datasets/{metadata.layer}/{metadata.domain}/{metadata.dataset}/info",
            json=mock_response,
        )
        requests_mock.put(f"{RAPID_URL}/schema", json={"dummy": "data"})
        with pytest.raises(ColumnNotDifferentException):
            update_schema_dataframe(rapid, metadata, mock_response["columns"])
