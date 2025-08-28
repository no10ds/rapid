from typing import Any, Dict
from pathlib import Path

import pandas as pd
import pandera
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

from api.domain.data_types import convert_pandera_column_to_athena, is_date_type
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
            
            # TODO Pandera: tidy this up
            # Return the schema in the expected format with metadata and columns structure
            schema_dict = schema.dict(exclude={"metadata": {"version"}})
            
            # Extract metadata fields
            metadata = {
                "layer": schema_dict["layer"],
                "domain": schema_dict["domain"],
                "dataset": schema_dict["dataset"],
                "sensitivity": schema_dict["sensitivity"],
                "description": schema_dict["description"],
                "key_value_tags": schema_dict["key_value_tags"],
                "key_only_tags": schema_dict["key_only_tags"],
                "owners": schema_dict["owners"],
                "update_behaviour": schema_dict["update_behaviour"],
                "is_latest_version": schema_dict["is_latest_version"],
            }
            
            # Convert columns dict to array format with proper field names
            columns = []
            for column_name, column_data in schema_dict["columns"].items():
                columns.append({
                    "name": column_name,
                    "partition_index": column_data["partition_index"],
                    "data_type": column_data["dtype"],
                    "allow_null": column_data["nullable"],
                    "format": column_data["format"],
                })
            
            # Return structured format
            return {
                "metadata": metadata,
                "columns": columns
            }
            
        except (SchemaError, SchemaInitError, ParserError) as e:
            raise UserError(f"Invalid data format: {str(e)}")

    def _customize_inferred_columns(self, inferred_columns: Dict[str, pandera.Column]) -> Dict[str, Column]:
        customized = {}

        for name, pandera_column in inferred_columns.items():
            clean_name = clean_column_name(name)
            athena_dtype_string = convert_pandera_column_to_athena(pandera_column.dtype)

            customized[clean_name] = Column(
                dtype=pandera_column.dtype,
                nullable=True,
                unique=False,
                format=DEFAULT_DATE_FORMAT if is_date_type(athena_dtype_string) else None,
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
