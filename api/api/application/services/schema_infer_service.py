from typing import List, Any
from pathlib import Path

import pandas as pd

from api.application.services.schema_validation import validate_schema
from api.common.custom_exceptions import UserError
from api.common.data_handlers import (
    construct_chunked_dataframe,
    delete_incoming_raw_file,
    get_dataframe_from_chunk_type,
)
from api.common.value_transformers import clean_column_name
from api.domain.data_types import DataTypes
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata


class SchemaInferService:
    def infer_schema(
        self,
        domain: str,
        dataset: str,
        sensitivity: str,
        file_path: Path,
    ) -> dict[str, Any]:
        dataframe = self._construct_single_chunk_dataframe(file_path)
        schema = Schema(
            metadata=SchemaMetadata(
                domain=domain,
                dataset=dataset,
                sensitivity=sensitivity,
                owners=[Owner(name="change_me", email="change_me@email.com")],
            ),
            columns=self._infer_columns(dataframe),
        )
        try:
            validate_schema(schema)
        finally:
            # We need to delete the incoming file from the local file system
            # regardless of the schema validation was successful or not
            delete_incoming_raw_file(schema, file_path)
        return schema.dict(exclude={"metadata": {"version"}})

    def transform_to_nullable_data_type(self, data_type_name: str) -> str:
        if data_type_name.capitalize() in DataTypes.numeric_data_types():
            data_type_name = data_type_name.capitalize()
        if data_type_name in "boolean":
            data_type_name = "boolean"
        return data_type_name

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
        columns = []
        for data_column in dataframe.columns:
            columns.append(
                self._infer_column(data_column, dataframe[data_column].dtype)
            )
        return columns

    def _infer_column(self, name: str, data_type) -> Column:
        data_type_name = data_type.name
        data_type_name = self.transform_to_nullable_data_type(data_type_name)
        return Column(
            name=clean_column_name(name),
            partition_index=None,
            data_type=data_type_name,
            allow_null=True,
            format=None,
        )
