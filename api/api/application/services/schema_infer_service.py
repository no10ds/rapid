from io import StringIO
from typing import List, Union, Any

import pandas as pd

from api.application.services.schema_validation import validate_schema
from api.common.config.constants import CONTENT_ENCODING
from api.common.config.layers import Layer
from api.common.custom_exceptions import UserError
from api.common.value_transformers import clean_column_name

from api.domain.data_types import extract_athena_types
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata


class SchemaInferService:
    def infer_schema(
        self,
        layer: Layer,
        domain: str,
        dataset: str,
        sensitivity: str,
        file_content: Union[bytes, str],
    ) -> dict[str, Any]:
        dataframe = self._construct_dataframe(file_content)
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
        validate_schema(schema)
        return schema.dict(exclude={"metadata": {"version"}})

    def _construct_dataframe(self, file_content: Union[bytes, str]) -> pd.DataFrame:
        parsed_contents = StringIO(str(file_content, CONTENT_ENCODING))
        try:
            return pd.read_csv(parsed_contents, encoding=CONTENT_ENCODING, sep=",")
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
                format=None,
            )
            for name, _type in extract_athena_types(dataframe).items()
        ]
