from mock import MagicMock, Mock, patch, call
import pytest
from pandas import DataFrame
from requests_mock import Mocker

from rapid.items.schema import Schema, Column
from rapid.items.schema_metadata import Owner, SchemaMetadata, SensitivityLevel
from rapid.patterns.dataset import (
    upload_and_create_dataset,
    update_schema_to_dataframe,
)
from rapid.exceptions import (
    DataFrameUploadValidationException,
    DatasetNotFoundException,
)
from rapid import Rapid


class TestData:
    def setup_method(self):
        self.metadata = SchemaMetadata(
            layer="raw",
            domain="test",
            dataset="rapid_sdk",
            sensitivity=SensitivityLevel.PUBLIC,
            owners=[Owner(name="test", email="test@email.com")],
        )

        self.mock_schema = Schema(
            metadata=self.metadata,
            columns=[
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
                Column(
                    name="column_c",
                    partition_index=None,
                    data_type="object",
                    allow_null=True,
                    format=None,
                ),
            ],
        )

        self.df = DataFrame(
            {
                "column_a": ["one", "two", "three"],
                "column_b": ["one", "two", "three"],
                "column_c": ["one", "two", "three"],
            }
        )

    def test_upload_and_create_dataset_success(self, rapid: Rapid):
        rapid.upload_dataframe = Mock()
        rapid.create_schema = Mock()
        rapid.update_schema = Mock()

        upload_and_create_dataset(rapid, self.metadata, self.df)
        rapid.upload_dataframe.assert_called_once_with(
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.df,
            wait_to_complete=True,
        )
        rapid.create_schema.assert_not_called()
        rapid.update_schema.assert_not_called()

    def test_upload_and_create_dataset_dataset_not_found(self, rapid: Rapid):
        rapid.upload_dataframe = Mock(
            side_effect=[DatasetNotFoundException("dummy", "data"), None]
        )
        rapid.generate_schema = Mock(return_value=self.mock_schema)
        rapid.create_schema = Mock()
        upload_and_create_dataset(rapid, self.metadata, self.df)

        rapid.generate_schema.assert_called_once_with(
            self.df,
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.metadata.sensitivity,
        )
        rapid.create_schema.assert_called_once_with(self.mock_schema)

        expected_call = call(
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.df,
            wait_to_complete=True,
        )
        rapid.upload_dataframe.assert_has_calls([expected_call, expected_call])

    def test_upload_and_create_dataset_do_not_upgrade_schema_on_fail(
        self, rapid: Rapid
    ):
        rapid.upload_dataframe = Mock(
            side_effect=[DataFrameUploadValidationException("dummy", "data"), None]
        )

        with pytest.raises(DataFrameUploadValidationException):
            upload_and_create_dataset(
                rapid, self.metadata, self.df, upgrade_schema_on_fail=False
            )
        rapid.upload_dataframe.assert_called_once_with(
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.df,
            wait_to_complete=True,
        )

    @patch("rapid.patterns.dataset.update_schema_to_dataframe")
    def test_upload_and_create_dataset_upgrade_schema_on_fail(
        self, mocked_update_schema_to_dataframe: MagicMock, rapid: Rapid
    ):
        rapid.upload_dataframe = Mock(
            side_effect=[DataFrameUploadValidationException("dummy", "data"), None]
        )

        upload_and_create_dataset(
            rapid, self.metadata, self.df, upgrade_schema_on_fail=True
        )
        mocked_update_schema_to_dataframe.assert_called_once_with(
            rapid, self.metadata, self.df
        )

        expected_call = call(
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.df,
            wait_to_complete=True,
        )
        rapid.upload_dataframe.assert_has_calls([expected_call, expected_call])

    def test_update_schema_to_dataframe(self, requests_mock: Mocker, rapid: Rapid):
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

        new_schema = Schema(metadata=self.mock_schema.metadata, columns=new_columns)
        rapid.generate_schema = Mock(return_value=new_schema)
        rapid.update_schema = Mock()

        update_schema_to_dataframe(rapid, self.metadata, self.df)

        rapid.generate_schema.assert_called_once_with(
            self.df,
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.metadata.sensitivity,
        )
        rapid.update_schema.assert_called_once_with(new_schema)
