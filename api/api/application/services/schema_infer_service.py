from typing import Any, Dict
from pathlib import Path

import pandas as pd
import pandera.pandas as pandera
from pandera.errors import SchemaError, SchemaInitError, ParserError

from api.application.services.schema_validation import validate_schema
from api.common.config.layers import Layer
from api.common.custom_exceptions import UserError
from api.common.data_handlers import (
    construct_chunked_dataframe,
    delete_incoming_raw_file,
    get_dataframe_from_chunk_type,
)
from api.common.value_transformers import clean_column_name

from api.domain.data_types import is_date_type, convert_pandera_column_to_athena
from api.domain.schema import Column, Schema
from api.domain.schema import Owner
from api.domain.dataset_metadata import DatasetMetadata

DEFAULT_DATE_FORMAT = "%Y-%m-%d"


class SchemaInferService:
    def infer_schema(
        self,
        layer: Layer,
        domain: str,
        dataset: str,
        sensitivity: str,
        file_path: Path,
    ) -> dict[str, Any]:
        try:
            dataframe = self._construct_single_chunk_dataframe(file_path)

            pandera_schema = pandera.infer_schema(dataframe)
            customized_columns = self._customize_inferred_columns(pandera_schema.columns)

            dataset_metadata = DatasetMetadata(
                layer=layer,
                domain=domain,
                dataset=dataset,
            )

            schema = Schema(
                dataset_metadata=dataset_metadata,
                columns=customized_columns,
                sensitivity=sensitivity,
                owners=[Owner(name="change_me", email="change_me@email.com")],
            )

            try:
                validate_schema(schema)
            finally:
                # We need to delete the incoming file from the local file system
                # regardless of the schema validation was successful or not
                delete_incoming_raw_file(schema, file_path)
            
            return schema.dict()
            
            
            
        except (SchemaError, SchemaInitError, ParserError) as e:
            raise UserError(f"Invalid data format: {str(e)}")

    def _customize_inferred_columns(self, inferred_columns: Dict[str, pandera.Column]) -> Dict[str, Column]:
        customized = {}

        for name, pandera_column in inferred_columns.items():
            clean_name = clean_column_name(name)

            customized[clean_name] = Column(
                dtype=pandera_column.dtype,
                nullable=True,
                unique=False,
                format=DEFAULT_DATE_FORMAT if is_date_type(pandera_column.dtype) else None,
                partition_index=None,
            )

        return customized

    def _construct_single_chunk_dataframe(self, file_path: Path) -> pd.DataFrame:
        try:
            for chunk in construct_chunked_dataframe(file_path):
                # We only validate a schema based on the first chunk
                return get_dataframe_from_chunk_type(chunk)
        except ValueError as error:
            raise UserError(
                f"The dataset you have provided is not formatted correctly: {self._clean_error(error.args[0])}"
            )

    def _clean_error(self, error_message: str) -> str:
        return error_message.replace("\n", "")
