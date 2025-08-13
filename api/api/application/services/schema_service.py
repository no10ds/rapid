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
from api.domain import schema_utils
from api.domain.dataset_metadata import DatasetMetadata

from api.domain.dataset_filters import DatasetFilters
from api.common.config.auth import Sensitivity

import pandera

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
    ) -> pandera.DataFrameSchema:
        if latest or not dataset.get_version():
            schema_dict = self.dynamodb_adapter.get_latest_schema(dataset)
        else:
            schema_dict = self.dynamodb_adapter.get_schema(dataset)

        if not schema_dict:
            raise SchemaNotFoundError(
                f"Could not find the schema for dataset {dataset.string_representation()}"
            )

        return self._parse_schema(schema_dict)

    # TODO Pandera: parse schema with pandera?
    def _parse_schema(self, schema: dict, only_metadata: bool = False):
        metadata = SchemaMetadata.parse_obj(schema)
        if only_metadata:
            return metadata
        return Schema(
            metadata=metadata,
            columns=[],
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

        return schema_utils.get_version(self._parse_schema(schema))

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

    def upload_schema(self, schema: pandera.DataFrameSchema) -> str:
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

    def update_schema(self, schema: pandera.DataFrameSchema) -> str:
        original_schema = self.get_schema(schema.metadata, latest=True)

        schema.metadata.version = (
            schema_utils.get_version(original_schema) + SCHEMA_VERSION_INCREMENT
        )

        self.check_for_sensitivity_consistency(original_schema, schema)
        self.check_for_protected_domain(schema)
        validate_schema_for_upload(schema)

        # Upload schema
        self.glue_adapter.create_table(schema)

        self.dynamodb_adapter.store_schema(schema)
        self.dynamodb_adapter.deprecate_schema(original_schema.metadata)
        return schema.metadata.dataset_identifier()

    def check_for_protected_domain(self, schema: pandera.DataFrameSchema) -> str:
        if Sensitivity.PROTECTED == schema_utils.get_sensitivity(schema):
            if (
                schema_utils.get_domain(schema)
                not in self.protected_domain_service.list_protected_domains()
            ):
                raise UserError(
                    f"The protected domain '{schema_utils.get_domain(schema)}' does not exist."
                )
        return schema_utils.get_domain(schema)

    def check_for_sensitivity_consistency(
        self, original_schema: pandera.DataFrameSchema, schema: pandera.DataFrameSchema
    ):
        original_sensitivity = original_schema.metadata.get_sensitivity()
        new_sensitivity = schema.metadata.get_sensitivity()
        if original_sensitivity != new_sensitivity:
            raise UserError(
                f"The sensitivity of this updated schema [{new_sensitivity}] does not match"
                + f" the original [{schema_utils.get_sensitivity(original_schema)}]. You cannot change"
                + " the sensitivity when updating a schema",
            )
