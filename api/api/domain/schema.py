from strenum import StrEnum
from typing import List, Dict, Optional, Set

import awswrangler as wr
from pydantic.main import BaseModel
import pyarrow as pa
import pandera

from api.domain.schema_metadata import Owner, SchemaMetadata, UpdateBehaviour

METADATA = "metadata"
COLUMNS = "columns"


# TODO Pandera: remove this 
# class Column(BaseModel):
#     name: str
#     partition_index: Optional[int]
#     data_type: str
#     allow_null: bool
#     format: Optional[str] = None
#     unique: bool = False

#     def is_of_data_type(self, d_type: StrEnum) -> bool:
#         return self.data_type in list(d_type)

# TODO Pandera: is this the right place for this?
def is_of_data_type(column: pandera.Column, d_type: StrEnum) -> bool:
    return str(column.dtype) in list(d_type)

class Schema(BaseModel):
    metadata: SchemaMetadata
    columns: List[pandera.Column]

    def column_has_data_type(self, column: pandera.Column, d_type: StrEnum) -> bool:
        return str(column.dtype) in [dt.value for dt in d_type]

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
        return [column.metadata.get("partition_index") for column in sorted_cols]

    def get_data_types(self) -> Set[str]:
        return {column.dtype for column in self.columns}

    def get_columns_by_type(self, d_type: StrEnum) -> List[pandera.Column]:
        return [column for column in self.columns if self.column_has_data_type(column, d_type)]

    def get_column_names_by_type(self, d_type: StrEnum) -> List[str]:
        return [
            column.name for column in self.columns if self.column_has_data_type(column, d_type)
        ]

    def get_non_partition_columns_for_glue(self) -> List[dict]:
        return [
            self.convert_column_to_glue_format(col)
            for col in self.columns
            if col.metadata.get("partition_index") is None
        ]

    def get_partition_columns_for_glue(self) -> List[dict]:
        return [
            self.convert_column_to_glue_format(col)
            for col in self.get_partition_columns()
        ]

    def convert_column_to_glue_format(self, column: pandera.Column):
        return {"Name": column.name, "Type": column.dtype}

    def get_partition_columns(self) -> List[pandera.Column]:
        return sorted(
            [column for column in self.columns
            if column.metadata and column.metadata.get("partition_index") is not None],
            key=lambda x: x.metadata.get("partition_index"),
        )

    def generate_storage_schema(self) -> pa.schema:
        return pa.schema(
            [
                pa.field(column.name, wr._data_types.athena2pyarrow(column.dtype))
                for column in self.columns
            ]
        )
