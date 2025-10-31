from typing import List, Type

from api.adapter.dynamodb_adapter import DynamoDBAdapter
from api.adapter.glue_adapter import GlueAdapter
from api.application.services.protected_domain_service import ProtectedDomainService
from api.application.services.schema_validation import validate_schema_for_upload
from api.common.config.constants import (
    FIRST_SCHEMA_VERSION_NUMBER,
    SCHEMA_VERSION_INCREMENT,
)
from api.common.custom_exceptions import (
    ConflictError,
    SchemaNotFoundError,
    UserError,
)
from api.common.logger import AppLogger
from api.domain.schema import Schema, COLUMNS
from rapid.items.schema import Column
from api.domain.schema_metadata import SchemaMetadata
from api.domain.dataset_metadata import DatasetMetadata

from api.domain.dataset_filters import DatasetFilters
from api.common.config.auth import Sensitivity


class SchemaService:
    def __init__(
        self,
        dynamodb_adapter=DynamoDBAdapter(),
        glue_adapter=GlueAdapter(),
        protected_domain_service=ProtectedDomainService(),
    ):
        self.dynamodb_adapter = dynamodb_adapter
        self.glue_adapter = glue_adapter
        self.protected_domain_service = protected_domain_service

    def get_schema(
        self, dataset: Type[DatasetMetadata], latest: bool = False
    ) -> Schema:
        if latest or not dataset.get_version():
            schema_dict = self.dynamodb_adapter.get_latest_schema(dataset)
        else:
            schema_dict = self.dynamodb_adapter.get_schema(dataset)

        if not schema_dict:
            raise SchemaNotFoundError(
                f"Could not find the schema for dataset {dataset.string_representation()}"
            )

        return self._parse_schema(schema_dict)

    def _parse_schema(self, schema: dict, only_metadata: bool = False):
        metadata = SchemaMetadata.model_validate(schema)
        if only_metadata:
            return metadata
        return Schema(
            metadata=metadata,
            columns=[Column.model_validate(col) for col in schema[COLUMNS]],
        )

    def get_schema_metadatas(
        self, query: DatasetFilters = DatasetFilters()
    ) -> List[SchemaMetadata]:
        schemas = self.dynamodb_adapter.get_latest_schemas(query)
        if schemas:
            return [
                self._parse_schema(schema, only_metadata=True) for schema in schemas
            ]
        return []

    def get_latest_schema_version(self, dataset: Type[DatasetMetadata]) -> int:
        schema = self.dynamodb_adapter.get_latest_schema(dataset)
        if not schema:
            return FIRST_SCHEMA_VERSION_NUMBER

        return self._parse_schema(schema).get_version()

    def delete_schema(self, dataset: Type[DatasetMetadata]) -> int:
        return self.dynamodb_adapter.delete_schema(dataset)

    def delete_schemas(self, dataset: Type[DatasetMetadata]) -> int:
        max_version = self.get_latest_schema_version(dataset)
        for i in range(max_version):
            metadata = DatasetMetadata(
                layer=dataset.layer,
                domain=dataset.domain,
                dataset=dataset.dataset,
                version=i + 1,
            )
            self.dynamodb_adapter.delete_schema(metadata)

    def upload_schema(self, schema: Schema) -> str:
        schema.metadata.version = FIRST_SCHEMA_VERSION_NUMBER
        dataset = schema.metadata
        try:
            if self.get_schema(dataset) is not None:
                AppLogger.warning(
                    f"Schema already exists for {dataset.string_representation()}"
                )
                raise ConflictError("Schema already exists")
        except SchemaNotFoundError:
            pass
        self.check_for_protected_domain(schema)
        validate_schema_for_upload(schema)
        self.glue_adapter.create_table(schema)
        self.dynamodb_adapter.store_schema(schema)
        return schema.metadata.glue_table_name()

    def update_schema(self, schema: Schema) -> str:
        original_schema = self.get_schema(schema.metadata, latest=True)

        schema.metadata.version = (
            original_schema.get_version() + SCHEMA_VERSION_INCREMENT
        )

        self.check_for_sensitivity_consistency(original_schema, schema)
        self.check_for_protected_domain(schema)
        validate_schema_for_upload(schema)

        # Upload schema
        self.glue_adapter.create_table(schema)

        self.dynamodb_adapter.store_schema(schema)
        self.dynamodb_adapter.deprecate_schema(original_schema.metadata)
        return schema.metadata.dataset_identifier()

    def check_for_protected_domain(self, schema: Schema) -> str:
        if Sensitivity.PROTECTED == schema.get_sensitivity():
            if (
                schema.get_domain()
                not in self.protected_domain_service.list_protected_domains()
            ):
                raise UserError(
                    f"The protected domain '{schema.get_domain()}' does not exist."
                )
        return schema.get_domain()

    def check_for_sensitivity_consistency(
        self, original_schema: Schema, schema: Schema
    ):
        original_sensitivity = original_schema.metadata.get_sensitivity()
        new_sensitivity = schema.metadata.get_sensitivity()
        if original_sensitivity != new_sensitivity:
            raise UserError(
                f"The sensitivity of this updated schema [{new_sensitivity}] does not match"
                + f" the original [{original_schema.get_sensitivity()}]. You cannot change"
                + " the sensitivity when updating a schema",
            )
