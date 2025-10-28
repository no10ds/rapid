from typing import List, Any
from pathlib import Path

import pandas as pd

from api.application.services.schema_validation import validate_schema
from api.common.config.layers import Layer
from api.common.custom_exceptions import UserError
from api.common.data_handlers import (
    construct_chunked_dataframe,
    delete_incoming_raw_file,
    get_dataframe_from_chunk_type,
)
from api.common.value_transformers import clean_column_name

from api.domain.data_types import extract_athena_types, is_date_type
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata

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
        dataframe = self._construct_single_chunk_dataframe(file_path)
        columns = self._infer_columns(dataframe)
        schema = Schema(
            metadata=SchemaMetadata(
                layer=layer,
                domain=domain,
                dataset=dataset,
                sensitivity=sensitivity,
                owners=[Owner(name="change_me", email="change_me@email.com")],
            ),
            columns=columns,
        )
        try:
            validate_schema(schema)
        finally:
            # We need to delete the incoming file from the local file system
            # regardless of the schema validation was successful or not
            delete_incoming_raw_file(schema, file_path)
        return schema.dict(exclude={"metadata": {"version"}})

    def _construct_single_chunk_dataframe(self, file_path: Path) -> pd.DataFrame:
        try:
            for chunk in construct_chunked_dataframe(file_path):
                # We only validate a schema based on the frist chunk
                return get_dataframe_from_chunk_type(chunk)
        except ValueError as error:
            raise UserError(
                f"The dataset you have provided is not formatted correctly: {self._clean_error(error.args[0])}"
            )

    def _clean_error(self, error_message: str) -> str:
        return error_message.replace("\n", "")

    def _infer_columns(self, dataframe: pd.DataFrame) -> List[Column]:
        return [
            Column(
                name=clean_column_name(name),
                partition_index=None,
                data_type=_type,
                allow_null=True,
                format=DEFAULT_DATE_FORMAT if is_date_type(_type) else None,
                unique=False,
            )
            for name, _type in extract_athena_types(dataframe).items()
        ]
