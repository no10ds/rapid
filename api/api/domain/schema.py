from strenum import StrEnum
from typing import List, Dict, Optional, Set, Any, Union
from pydantic import BaseModel

import awswrangler as wr
import pyarrow as pa
import pandera as pandera


from api.domain.schema_metadata import Owner, SchemaMetadata, UpdateBehaviour


METADATA = "metadata"
COLUMNS = "columns"


class Column(BaseModel):
    partition_index: Optional[int]
    data_type: str
    nullable: bool
    name: Optional[str] = None
    format: Optional[str] = None
    unique: bool = False
    checks: List[Union[Dict[str, Any], pandera.Check]] = []



    class Config:
        arbitrary_types_allowed = True

    def to_pandera_column(self) -> pandera.Column:
        # TODO: I think this is missing some args
        return pandera.Column(
            name=self.name,
            nullable=self.nullable,
            unique=self.unique,
            checks=self.checks,
        )

    def _dict_to_pandera_check(self, check_dict: Dict[str, Any]) -> pandera.Check:
        """Convert dictionary representation to Pandera check"""
        check_type = check_dict.get("check_type")
        params = check_dict.get("parameters", {})

        if check_type == "in_range":
            min_val = params.get("min_value")
            max_val = params.get("max_value")
            return pandera.Check.in_range(min_value=min_val, max_value=max_val)
        elif check_type == "isin":
            allowed_values = params.get("allowed_values", [])
            return pandera.Check.isin(allowed_values)
        elif check_type == "str_length":
            min_val = params.get("min_value")
            max_val = params.get("max_value")
            return pandera.Check.str_length(min_value=min_val, max_value=max_val)
        elif check_type == "greater_than":
            min_val = params.get("min_value")
            return pandera.Check.greater_than(min_val)
        elif check_type == "less_than":
            max_val = params.get("max_value")
            return pandera.Check.less_than(max_val)
        elif check_type == "str_matches":
            pattern = params.get("pattern")
            return pandera.Check.str_matches(pattern)
        else:
            raise ValueError(f"Unsupported check type: {check_type}")

    def is_of_data_type(self, d_type: StrEnum) -> bool:
        dtype_values = [item.value for item in d_type]
        dtype_str = str(self.data_type)
        return dtype_str in dtype_values


class Schema(BaseModel):
    metadata: SchemaMetadata
    columns: Dict[str, Column]

    class Config:
        arbitrary_types_allowed = True
    
    def pandera_validate(self, df, **kwargs):
        pandera_columns = {
            name: col.to_pandera_column() 
            for name, col in self.columns.items()
        }
        pandera_schema = pandera.DataFrameSchema(metadata=self.metadata, columns=pandera_columns)
        return pandera_schema.validate(df, **kwargs)
    
    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data.pop('BACKEND_REGISTRY', None)
        
        if 'columns' in data:
            for column_name, column_data in data['columns'].items():
                if isinstance(column_data, dict):
                    column_data.pop('BACKEND_REGISTRY', None)
        
        return data
    
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
        return list(self.columns.keys())

    def get_partitions(self) -> List[str]:
        sorted_cols = self.get_partition_columns()
        return [name for name, column in sorted_cols]

    def get_partition_indexes(self) -> List[int]:
        sorted_cols = self.get_partition_columns()
        return [column.partition_index for name, column in sorted_cols]

    def get_data_types(self) -> Set[str]:
        return {column.data_type for column in self.columns.values()}

    def get_columns_by_type(self, d_type: StrEnum) -> List[str]:
        dtype_values = [item.value for item in d_type]
        return [
            name for name, col_def in self.columns.items()
            if col_def.data_type in dtype_values
        ]

    def get_column_names_by_type(self, d_type: StrEnum) -> List[str]:
        return self.get_columns_by_type(d_type)

    def get_non_partition_columns_for_glue(self) -> List[dict]:
        return [
            self.convert_column_to_glue_format(name, col_def)
            for name, col_def in self.columns.items()
            if col_def.partition_index is None
        ]

    def get_partition_columns_for_glue(self) -> List[dict]:
        sorted_cols = self.get_partition_columns()
        return [
            self.convert_column_to_glue_format(name, col_def)
            for name, col_def in sorted_cols
        ]

    def convert_column_to_glue_format(self, name: str, column: Column):
        return {"Name": name, "Type": column.data_type}

    def get_partition_columns(self) -> List[tuple[str, Column]]:
        partition_cols = [
            (name, column) for name, column in self.columns.items()
            if column.partition_index is not None
        ]
        return sorted(partition_cols, key=lambda x: x[1].partition_index)

    def generate_storage_schema(self) -> pa.schema:
        return pa.schema(
            [
                pa.field(name, wr._data_types.athena2pyarrow(column.data_type))
                for name, column in self.columns.items()
            ]
        )
