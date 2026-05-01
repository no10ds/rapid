from strenum import StrEnum
from typing import List, Dict, Optional, Set

import awswrangler as wr
from pydantic.main import BaseModel
from pydantic import field_serializer, field_validator
import pyarrow as pa
import pandera
import pandera.pandas as pandera_pandas
import pandera.io as pandera_io

from api.domain.schema_metadata import Owner, SchemaMetadata
from rapid.items.schema import Column, UpdateBehaviour

METADATA = "metadata"
COLUMNS = "columns"


class Schema(BaseModel):
    metadata: SchemaMetadata
    columns: List[Column]
    panderaDataFrameSchema: Optional[pandera_pandas.DataFrameSchema] = None

    @field_serializer("panderaDataFrameSchema", mode="plain")
    def pandera_dump(self, value: pandera_pandas.DataFrameSchema) -> str:
        if value is not None:
            return value.to_json()
        else:
            return value

    @field_validator("panderaDataFrameSchema", mode="before")
    def capitalize(cls, value: str) -> pandera_pandas.DataFrameSchema:
        if value is not None:
            return pandera_io.from_json(value)
        else:
            return value

    def get_layer(self) -> str:
        return self.metadata.get_layer()

    def get_domain(self) -> str:
        return self.metadata.get_domain().lower()

    def get_dataset(self) -> str:
        return self.metadata.get_dataset()

    def get_description(self) -> str:
        return self.metadata.get_description()

    def get_sensitivity(self) -> str:
        return self.metadata.get_sensitivity()

    def get_version(self) -> int:
        return self.metadata.get_version()

    def get_tags(self) -> Dict[str, str]:
        return self.metadata.get_tags()

    def get_owners(self) -> Optional[List[Owner]]:
        return self.metadata.get_owners()

    def get_update_behaviour(self) -> str:
        return self.metadata.get_update_behaviour()

    def has_overwrite_behaviour(self) -> bool:
        return self.get_update_behaviour() == UpdateBehaviour.OVERWRITE

    def get_column_names(self) -> List[str]:
        return [column.name for column in self.columns]

    def get_partitions(self) -> List[str]:
        sorted_cols = self.get_partition_columns()
        return [column.name for column in sorted_cols]

    def get_partition_indexes(self) -> List[int]:
        sorted_cols = self.get_partition_columns()
        return [column.partition_index for column in sorted_cols]

    def get_data_types(self) -> Set[str]:
        return {column.data_type for column in self.columns}

    def get_columns_by_type(self, d_type: StrEnum) -> List[Column]:
        return [column for column in self.columns if column.is_of_data_type(d_type)]

    def get_column_names_by_type(self, d_type: StrEnum) -> List[str]:
        return [
            column.name for column in self.columns if column.is_of_data_type(d_type)
        ]

    def get_non_partition_columns_for_glue(self) -> List[dict]:
        return [
            self.convert_column_to_glue_format(col)
            for col in self.columns
            if col.partition_index is None
        ]

    def get_partition_columns_for_glue(self) -> List[dict]:
        return [
            self.convert_column_to_glue_format(col)
            for col in self.get_partition_columns()
        ]

    def convert_column_to_glue_format(self, column: List[Column]):
        return {"Name": column.name, "Type": column.data_type}

    def get_partition_columns(self) -> List[Column]:
        return sorted(
            [column for column in self.columns if column.partition_index is not None],
            key=lambda x: x.partition_index,
        )

    def generate_storage_schema(self) -> pa.schema:
        return pa.schema(
            [
                pa.field(column.name, wr._data_types.athena2pyarrow(column.data_type))
                for column in self.columns
            ]
        )

    def pandera_validate(self, df, **kwargs):
        pandera_columns = {col.name: col.to_pandera_column() for col in self.columns}
        pandera_schema = pandera.DataFrameSchema(
            metadata=self.metadata, columns=pandera_columns
        )
        return pandera_schema.validate(df, **kwargs)

    def pandera_schema_validate(self, df, **kwargs):
        if self.panderaDataFrameSchema is not None:
            return self.panderaDataFrameSchema.validate(df, **kwargs)
        else:
            return df
