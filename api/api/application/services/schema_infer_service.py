from typing import List, Any, Dict
from pathlib import Path
import json

import pandas as pd
import pandera

from api.application.services.schema_validation import validate_schema
from api.common.config.layers import Layer
from api.common.custom_exceptions import UserError
from api.common.data_handlers import (
    construct_chunked_dataframe,
    delete_incoming_raw_file,
    get_dataframe_from_chunk_type,
)
from api.common.value_transformers import clean_column_name

from api.domain.data_types import is_date_type
from api.domain.schema import Schema
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
        
        pandera_schema = pandera.infer_schema(dataframe)
        # TODO Pandera: infer whole schema with pandera
        customized_columns = self._customize_inferred_columns(pandera_schema.columns)
        
        schema = Schema(
            metadata=SchemaMetadata(
                layer=layer,
                domain=domain,
                dataset=dataset,
                sensitivity=sensitivity,
                owners=[Owner(name="change_me", email="change_me@email.com")],
            ),
            columns=customized_columns,
        )
        try:
            validate_schema(schema)
        finally:
            # We need to delete the incoming file from the local file system
            # regardless of the schema validation was successful or not
            delete_incoming_raw_file(schema, file_path)
        schema_json = schema.json(exclude={"metadata": {"version"}})
        return json.loads(schema_json)

    def _customize_inferred_columns(self, inferred_columns: Dict[str, pandera.Column]) -> List[pandera.Column]:
        customized = []
        
        for name, column in inferred_columns.items():
            custom_column = pandera.Column(
                name=clean_column_name(name),  
                dtype=column.dtype,          
                nullable=True,                
                unique=False,                      
                metadata={
                    "format": DEFAULT_DATE_FORMAT if is_date_type(column.dtype) else None,
                    "partition_index": None,
                },
            )
            customized.append(custom_column)
        
        return customized

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

    # TODO Pandera: remove
    # def _infer_columns(self, dataframe: pd.DataFrame) -> List[pandera.Column]:
    #     return [
    #         pandera.Column(
    #             name=clean_column_name(name),
    #             dtype=dataframe[name].dtype,
    #             nullable=True,
    #             unique=False,
    #             metadata={
    #                 "format": DEFAULT_DATE_FORMAT if is_date_type(dataframe[name].dtype) else None,
    #                 "partition_index": None,
    #             },
    #         )
    #         for name in dataframe.columns
    #     ]
