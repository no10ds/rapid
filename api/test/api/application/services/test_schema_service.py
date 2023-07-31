from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError


from api.application.services.schema_service import (
    SchemaService,
)
from api.common.config.auth import Sensitivity
from api.common.custom_exceptions import (
    SchemaNotFoundError,
    SchemaValidationError,
    ConflictError,
    UserError,
)
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata


class TestUploadSchema:
    def setup_method(self):
        self.dynamodb_adapter = Mock()
        self.glue_adapter = Mock()
        self.protected_domain_service = Mock()
        self.schema_service = SchemaService(
            self.dynamodb_adapter,
            self.glue_adapter,
            self.protected_domain_service,
        )
        self.valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="integer",
                    allow_null=False,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="string",
                    allow_null=True,
                ),
            ],
        )

    def test_upload_schema(self):
        self.schema_service.get_schema = Mock(return_value=None)

        result = self.schema_service.upload_schema(self.valid_schema)

        self.dynamodb_adapter.store_schema.assert_called_once_with(self.valid_schema)
        self.glue_adapter.create_table.assert_called_once_with(self.valid_schema)
        assert result == self.valid_schema.metadata.glue_table_name()

    def test_upload_schema_uppercase_domain(self):
        self.schema_service.get_schema = Mock(return_value=None)

        schema = self.valid_schema.copy()
        schema.metadata.domain = schema.metadata.domain.upper()
        result = self.schema_service.upload_schema(schema)

        self.dynamodb_adapter.store_schema.assert_called_once_with(schema)
        self.glue_adapter.create_table.assert_called_once_with(schema)
        result == schema.metadata.glue_table_name()

    def test_aborts_uploading_if_create_table_fails(self):
        self.schema_service.get_schema = Mock(return_value=None)

        self.glue_adapter.create_table.side_effect = ClientError(
            error_response={"Error": {"Code": "Failed"}}, operation_name="CreateTable"
        )

        with pytest.raises(ClientError):
            self.schema_service.upload_schema(self.valid_schema)

        self.dynamodb_adapter.store_schema.assert_not_called()

    def test_check_for_protected_domain_success(self):
        schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="domain",
                dataset="dataset",
                sensitivity="PROTECTED",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="integer",
                    allow_null=True,
                ),
            ],
        )
        self.protected_domain_service.list_protected_domains = Mock(
            return_value=["domain", "other"]
        )

        result = self.schema_service.check_for_protected_domain(schema)

        self.protected_domain_service.list_protected_domains.assert_called_once()
        assert result == "domain"

    def test_check_for_protected_domain_fails(self):
        schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="domain1",
                dataset="dataset2",
                sensitivity="PROTECTED",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="integer",
                    allow_null=True,
                ),
            ],
        )
        self.protected_domain_service.list_protected_domains = Mock(
            return_value=["other"]
        )

        with pytest.raises(
            UserError, match="The protected domain 'domain1' does not exist."
        ):
            self.schema_service.check_for_protected_domain(schema)

    def test_upload_schema_throws_error_when_schema_already_exists(self):
        self.schema_service.get_schema = Mock(return_value=self.valid_schema)

        with pytest.raises(ConflictError, match="Schema already exists"):
            self.schema_service.upload_schema(self.valid_schema)

    def test_upload_schema_throws_error_when_schema_invalid(self):
        self.schema_service.get_schema = Mock(return_value=None)

        invalid_partition_index = -1
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=invalid_partition_index,
                    data_type="integer",
                    allow_null=True,
                )
            ],
        )

        with pytest.raises(SchemaValidationError):
            self.schema_service.upload_schema(invalid_schema)


class TestUpdateSchema:
    def setup_method(self):
        self.dynamodb_adapter = Mock()
        self.glue_adapter = Mock()
        self.protected_domain_service = Mock()
        self.schema_service = SchemaService(
            self.dynamodb_adapter,
            self.glue_adapter,
            self.protected_domain_service,
        )
        self.valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="testdomain",
                dataset="testdataset",
                sensitivity="PUBLIC",
                version=1,
                owners=[Owner(name="owner", email="owner@email.com")],
                key_value_tags={"key1": "val1", "testkey2": "testval2"},
                key_only_tags=["ktag1", "ktag2"],
                update_behaviour="APPEND",
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="integer",
                    allow_null=False,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="string",
                    allow_null=True,
                ),
            ],
        )
        self.valid_updated_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="testdomain",
                dataset="testdataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
                key_value_tags={"key1": "val1", "testkey2": "testval2"},
                key_only_tags=["ktag1", "ktag2"],
                update_behaviour="APPEND",
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="double",
                    allow_null=False,
                ),
                Column(
                    name="colname_new",
                    partition_index=None,
                    data_type="string",
                    allow_null=True,
                ),
            ],
        )

    def test_update_schema_throws_error_when_schema_invalid(self):
        invalid_partition_index = -1
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                version=1,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=invalid_partition_index,
                    data_type="integer",
                    allow_null=True,
                )
            ],
        )
        self.schema_service.get_schema = Mock(return_value=self.valid_schema)

        with pytest.raises(SchemaValidationError):
            self.schema_service.update_schema(invalid_schema)

    def test_update_schema_for_protected_domain_failure(self):
        original_schema = self.valid_schema.copy(deep=True)
        original_schema.metadata.sensitivity = Sensitivity.PROTECTED
        new_schema = self.valid_updated_schema.copy(deep=True)
        new_schema.metadata.sensitivity = Sensitivity.PROTECTED

        self.schema_service.get_schema = Mock(return_value=original_schema)
        self.protected_domain_service.list_protected_domains = Mock(
            return_value=["other"]
        )

        with pytest.raises(
            UserError,
            match=f"The protected domain '{new_schema.get_domain()}' does not exist.",
        ):
            self.schema_service.update_schema(new_schema)

    # TODO: Fix this test
    # def test_update_schema_when_crawler_raises_error(self):
    #     new_schema = self.valid_updated_schema
    #     expected_schema = self.valid_updated_schema.copy(deep=True)
    #     expected_schema.metadata.version = 2

    #     self.schema_service.get_schema = Mock(return_value=self.valid_schema)
    #     self.glue_adapter.create_table.side_effect = TableCreationError(
    #         "error occurred"
    #     )

    #     with pytest.raises(TableCreationError, match="error occurred"):
    #         self.schema_service.update_schema(new_schema)

    #     self.glue_adapter.create_table.assert_called_once_with(new_schema)
    #     self.schema_service.store_schema.assert_not_called()
    #     self.schema_service.deprecate_schema.assert_not_called()

    def test_update_schema_success(self):
        original_schema = self.valid_schema
        original_schema.metadata.version = 2
        new_schema = self.valid_updated_schema
        expected_schema = self.valid_updated_schema.copy(deep=True)
        expected_schema.metadata.version = 3

        self.schema_service.get_schema = Mock(return_value=original_schema)

        result = self.schema_service.update_schema(new_schema)

        self.glue_adapter.create_table.assert_called_once_with(new_schema)
        self.dynamodb_adapter.store_schema.assert_called_once_with(expected_schema)
        self.dynamodb_adapter.deprecate_schema.assert_called_once_with(original_schema)
        assert result == "raw/testdomain/testdataset/3"

    def test_update_schema_enforces_sensitivity_consistency(self):
        original_schema = self.valid_schema
        new_schema = self.valid_updated_schema.copy(deep=True)
        new_schema.metadata.sensitivity = Sensitivity.PRIVATE

        self.schema_service.get_schema = Mock(return_value=original_schema)
        with pytest.raises(
            UserError,
            match=r"The sensitivity of this updated schema \[PRIVATE\] does not match"
            + r" the original \[PUBLIC\]. You cannot change"
            + " the sensitivity when updating a schema",
        ):
            self.schema_service.update_schema(new_schema)

    def test_update_schema_for_protected_domain_success(self):
        original_schema = self.valid_schema.copy(deep=True)
        original_schema.metadata.sensitivity = Sensitivity.PROTECTED
        new_schema = self.valid_updated_schema.copy(deep=True)
        new_schema.metadata.sensitivity = Sensitivity.PROTECTED
        expected_schema = self.valid_updated_schema.copy(deep=True)
        expected_schema.metadata.version = 2
        expected_schema.metadata.sensitivity = Sensitivity.PROTECTED

        self.schema_service.get_schema = Mock(return_value=original_schema)
        self.protected_domain_service.list_protected_domains = Mock(
            return_value=[original_schema.get_domain(), "other"]
        )

        result = self.schema_service.update_schema(new_schema)

        self.glue_adapter.create_table.assert_called_once_with(expected_schema)
        self.dynamodb_adapter.store_schema.assert_called_once_with(expected_schema)
        self.dynamodb_adapter.deprecate_schema.assert_called_once_with(original_schema)
        assert result == "raw/testdomain/testdataset/2"


class TestGetSchema:
    def setup_method(self):
        self.dynamodb_adapter = Mock()
        self.glue_adapter = Mock()
        self.protected_domain_service = Mock()
        self.schema_service = SchemaService(
            self.dynamodb_adapter,
            self.glue_adapter,
            self.protected_domain_service,
        )
        self.metadata = SchemaMetadata(
            layer="raw",
            domain="some",
            dataset="other",
            version=2,
            sensitivity="PUBLIC",
            owners=[Owner(name="owner", email="owner@email.com")],
        )

        self.columns = [
            Column(
                name="colname1",
                partition_index=0,
                data_type="integer",
                allow_null=False,
            ),
            Column(
                name="colname2",
                partition_index=None,
                data_type="string",
                allow_null=True,
            ),
        ]
        self.schema = Schema(metadata=self.metadata, columns=self.columns)

        self.schema_dict = {
            "Layer": "raw",
            "Domain": "some",
            "Dataset": "other",
            "Version": 2,
            "Description": "",
            "Sensitivity": "PUBLIC",
            "UpdateBehaviour": "APPEND",
            "IsLatestVersion": True,
            "Owners": [{"name": "owner", "email": "owner@email.com"}],
            "Columns": [dict(col) for col in self.columns],
            "KeyValueTags": {},
            "KeyOnlyTags": [],
        }

    def test_get_schema_success(self):
        self.dynamodb_adapter.get_schema = Mock(return_value=self.schema_dict)

        res = self.schema_service.get_schema(self.metadata)

        assert res == self.schema
        self.dynamodb_adapter.get_schema.assert_called_once_with(self.metadata)

    def test_get_schema_success_latest(self):
        self.dynamodb_adapter.get_latest_schema = Mock(return_value=self.schema_dict)

        res = self.schema_service.get_schema(self.metadata, latest=True)

        assert res == self.schema
        self.dynamodb_adapter.get_latest_schema.assert_called_once_with(self.metadata)

    def test_get_schema_raises_exception(self):
        self.dynamodb_adapter.get_schema = Mock(return_value=None)

        with pytest.raises(SchemaNotFoundError):
            self.schema_service.get_schema(self.metadata)
            self.dynamodb_adapter.get_schema.assert_called_once_with(self.metadata)

    def test_get_schema_metadatas(self):
        self.dynamodb_adapter.get_latest_schemas.return_value = [
            self.schema_dict,
            self.schema_dict,
        ]
        res = self.schema_service.get_schema_metadatas("query")
        assert res == [self.schema.metadata, self.schema.metadata]
        self.dynamodb_adapter.get_latest_schemas.assert_called_once_with("query")

    def test_get_schema_metadatas_empty(self):
        self.dynamodb_adapter.get_latest_schemas.return_value = []
        res = self.schema_service.get_schema_metadatas("query")
        assert res == []
        self.dynamodb_adapter.get_latest_schemas.assert_called_once_with("query")

    def test_get_latest_schema_version(self):
        self.dynamodb_adapter.get_latest_schema.return_value = self.schema_dict
        res = self.schema_service.get_latest_schema_version(self.metadata)
        assert res == 2
        self.dynamodb_adapter.get_latest_schema.assert_called_once_with(self.metadata)

    def test_get_latest_schema_version_no_schema(self):
        self.dynamodb_adapter.get_latest_schema.return_value = None
        res = self.schema_service.get_latest_schema_version(self.metadata)
        assert res == 1
        self.dynamodb_adapter.get_latest_schema.assert_called_once_with(self.metadata)
