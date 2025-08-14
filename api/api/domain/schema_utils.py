from strenum import StrEnum
from typing import List, Dict, Optional, Set
from pydantic import BaseModel, EmailStr

import awswrangler as wr
from pydantic.main import BaseModel
import pyarrow as pa
import pandera

from api.domain.schema_metadata import Owner, UpdateBehaviour


METADATA = "metadata"
COLUMNS = "columns"

def column_has_data_type(column: pandera.Column, d_type: StrEnum) -> bool:
    return str(column.dtype) in [dt.value for dt in d_type]

def get_layer(schema: pandera.DataFrameSchema) -> str:
    return schema.metadata.get("layer")

def get_domain(schema: pandera.DataFrameSchema) -> str:
    return schema.metadata.get("domain").lower()

def get_dataset(schema: pandera.DataFrameSchema) -> str:
    return schema.metadata.get("dataset")

def get_description(schema: pandera.DataFrameSchema) -> str:
    return schema.metadata.get("description")

def get_sensitivity(schema: pandera.DataFrameSchema) -> str:
    return schema.metadata.get("sensitivity")

def get_version(schema: pandera.DataFrameSchema) -> int:
    return schema.metadata.get("version")

def get_tags(schema: pandera.DataFrameSchema) -> Dict[str, str]:
    return {**schema.metadata.get("key_value_tags"), **dict.fromkeys(schema.metadata.get("key_only_tags"), "")}

def get_owners(schema: pandera.DataFrameSchema) -> Optional[List[Owner]]:
    return schema.metadata.get("owners")

def get_update_behaviour(schema: pandera.DataFrameSchema) -> str:
    return schema.metadata.get("update_behaviour")

def has_overwrite_behaviour(schema: pandera.DataFrameSchema) -> bool:
    return get_update_behaviour(schema) == UpdateBehaviour.OVERWRITE

def get_column_names(schema: pandera.DataFrameSchema) -> List[str]:
    return list(schema.columns.keys())

def get_partitions(schema: pandera.DataFrameSchema) -> List[str]:
    sorted_cols = get_partition_columns(schema)
    return [column.name for column in sorted_cols]

def get_partition_indexes(schema: pandera.DataFrameSchema) -> List[int]:
    sorted_cols = get_partition_columns(schema)
    return [column.metadata.get("partition_index") for column in sorted_cols]

def get_data_types(schema: pandera.DataFrameSchema) -> Set[str]:
    return {str(column.dtype) for column in schema.columns.values()}

def get_columns_by_type(schema: pandera.DataFrameSchema, d_type: StrEnum) -> List[pandera.Column]:
    return [column for column in schema.columns.values() if column_has_data_type(column, d_type)]

def get_column_names_by_type(schema: pandera.DataFrameSchema, d_type: StrEnum) -> List[str]:
    return [
        column.name for column in schema.columns.values() if column_has_data_type(column, d_type)
    ]

def get_non_partition_columns_for_glue(schema: pandera.DataFrameSchema) -> List[dict]:
    return [
        convert_column_to_glue_format(col)
        for col in schema.columns.values()
        if col.metadata.get("partition_index") is None
    ]

def get_partition_columns_for_glue(schema: pandera.DataFrameSchema) -> List[dict]:
    return [
        convert_column_to_glue_format(col)
        for col in get_partition_columns(schema)
    ]

# TODO Pandera: I think this is where we should convert the data types to athena format
def convert_column_to_glue_format(column: pandera.Column):
    return {"Name": column.name, "Type": column.dtype}

def get_partition_columns(schema: pandera.DataFrameSchema) -> List[pandera.Column]:
    return sorted(
        [column for column in schema.columns.values()
        if column.metadata and column.metadata.get("partition_index") is not None],
        key=lambda x: x.metadata.get("partition_index"),
    )

def generate_storage_schema(schema: pandera.DataFrameSchema) -> pa.schema:
    return pa.schema(
        [
            pa.field(column.name, wr._data_types.athena2pyarrow(column.dtype))
            for column in schema.columns
        ]
    )
