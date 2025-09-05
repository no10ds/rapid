from strenum import StrEnum
from typing import List, Dict, Optional, Set, Any, Union
from pydantic import BaseModel, EmailStr

import awswrangler as wr
import pyarrow as pa
import pandera.pandas as pandera
from pandera.backends.pandas.container import DataFrameSchemaBackend
from pandera.backends.pandas.components import ColumnBackend

from api.domain.schema_metadata import Owner, SchemaMetadata, UpdateBehaviour
from api.domain.data_types import convert_pandera_column_to_athena, PANDERA_ENGINE_TO_ATHENA_CONVERTER
from api.common.custom_exceptions import SchemaValidationError

METADATA = "metadata"
COLUMNS = "columns"

class Column(BaseModel):
    partition_index: Optional[int]
    dtype: str
    nullable: bool
    format: Optional[str] = None
    unique: bool = False
    checks: List[Union[Dict[str, Any], pandera.Check]] = []
    
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        try:
            pandera_checks = []

            for i, check in enumerate(self.checks):
                if isinstance(check, dict):
                    pandera_check = self._dict_to_pandera_check(check)
                    pandera_checks.append(pandera_check)
                elif isinstance(check, pandera.Check):
                    pandera_checks.append(check)
                elif check is None:
                    continue
                else:
                    raise ValueError(f"Invalid check type: {type(check)}")
                            
            self._pandera_column = pandera.Column(
                dtype=self.dtype, 
                nullable=self.nullable, 
                unique=self.unique,
                checks=pandera_checks
            )
            if self._pandera_column.metadata is None:
                self._pandera_column.metadata = {}
            self._pandera_column.metadata["partition_index"] = self.partition_index
            self._pandera_column.metadata["format"] = self.format
        except TypeError as e:
            raise SchemaValidationError(
                "You are specifying one or more unaccepted data types",
            )
  
    @classmethod
    def get_backend(cls, check_obj=None, check_type=None):
        """Override to use the standard ColumnBackend"""
        return ColumnBackend()
    
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
        dtype_str = str(self.dtype)
        return dtype_str in dtype_values



class Schema(BaseModel):
    metadata: SchemaMetadata
    columns: Dict[str, Column]
    
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        
        metadata = self.metadata
        
        if isinstance(metadata, SchemaMetadata):
            self._metadata = metadata
        else:
            self._metadata = SchemaMetadata(
                layer=metadata.get("layer"),
                domain=metadata.get("domain"), 
                dataset=metadata.get("dataset"),
                version=metadata.get("version"),
                sensitivity=metadata.get("sensitivity", ""),
                description=metadata.get("description", ""),
                key_value_tags=metadata.get("key_value_tags", {}),
                key_only_tags=metadata.get("key_only_tags", []),
                owners=[Owner(**owner) for owner in metadata.get("owners", [])] if metadata.get("owners") else None,
                update_behaviour=metadata.get("update_behaviour", UpdateBehaviour.APPEND),
                is_latest_version=metadata.get("is_latest_version", True),
            )

        pandera_metadata = {
            "layer": self._metadata.layer,
            "domain": self._metadata.domain,
            "dataset": self._metadata.dataset,
            "version": self._metadata.version,
            "sensitivity": self._metadata.sensitivity,
            "description": self._metadata.description,
            "key_value_tags": self._metadata.key_value_tags,
            "key_only_tags": self._metadata.key_only_tags,
            "owners": self._metadata.owners,
            "update_behaviour": self._metadata.update_behaviour,
            "is_latest_version": self._metadata.is_latest_version,
        }

        pandera_columns = {}
        for name, column in self.columns.items():
            pandera_columns[name] = column._pandera_column

        self._pandera_schema = pandera.DataFrameSchema(
            columns=pandera_columns, 
            metadata=pandera_metadata
        )

    @classmethod
    def get_backend(cls, check_obj=None, check_type=None):
        if check_obj is not None:
            check_obj_cls = type(check_obj)
        elif check_type is not None:
            check_obj_cls = check_type
        else:
            raise ValueError("Must pass in one of `check_obj` or `check_type`.")
        
        cls.register_default_backends(check_obj_cls)
        return DataFrameSchemaBackend()

    def validate(self, df, **kwargs):
        return self._pandera_schema.validate(df, **kwargs)
    
    @property
    def pandera_metadata(self):
        return self._pandera_schema.metadata

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
        return {column.dtype for column in self.columns.values()}

    def get_columns_by_type(self, d_type: StrEnum) -> List[str]:
        dtype_values = [item.value for item in d_type]
        return [
            name for name, col_def in self.columns.items()
            if col_def.dtype in dtype_values
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
        
        athena_type = convert_pandera_column_to_athena(column.dtype)
        return {"Name": name, "Type": athena_type}

    def get_partition_columns(self) -> List[tuple[str, Column]]:
        partition_cols = [
            (name, column) for name, column in self.columns.items()
            if column.partition_index is not None
        ]
        return sorted(partition_cols, key=lambda x: x[1].partition_index)

    def generate_storage_schema(self) -> pa.schema:
        return pa.schema(
            [
                pa.field(name, wr._data_types.athena2pyarrow(convert_pandera_column_to_athena(column.dtype)))
                for name, column in self.columns.items()
            ]
        )
