from strenum import StrEnum
from typing import List, Dict, Optional, Set, Any
from pydantic import BaseModel, EmailStr

import awswrangler as wr
import pyarrow as pa
import pandera.pandas as pandera
from pandera.backends.pandas.container import DataFrameSchemaBackend
from pandera.backends.pandas.components import ColumnBackend

from api.domain.dataset_metadata import DatasetMetadata
from api.domain.data_types import convert_pandera_column_to_athena
from api.common.custom_exceptions import SchemaValidationError

METADATA = "metadata"
COLUMNS = "columns"

SENSITIVITY = "sensitivity"
DESCRIPTION = "description"
KEY_VALUE_TAGS = "key_value_tags"
KEY_ONLY_TAGS = "key_only_tags"
OWNERS = "owners"
UPDATE_BEHAVIOUR = "update_behaviour"
IS_LATEST_VERSION = "is_latest_version"


class Owner(BaseModel):
    name: str
    email: EmailStr


class UpdateBehaviour(StrEnum):
    APPEND = "APPEND"
    OVERWRITE = "OVERWRITE"


class Column(BaseModel):
    dtype: str
    nullable: bool
    unique: bool = False
    partition_index: Optional[int] = None
    format: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        try:
            self._pandera_column = pandera.Column(
                dtype=self.dtype, 
                nullable=self.nullable, 
                unique=self.unique
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

    def is_of_data_type(self, d_type: StrEnum) -> bool:
        dtype_values = [item.value for item in d_type]
        dtype_str = str(self.dtype)
        return dtype_str in dtype_values

    def to_dict(self) -> dict:
        return {
            "dtype": self.dtype,
            "nullable": self.nullable,
            "unique": self.unique if hasattr(self, 'unique') else False,
            "partition_index": self.partition_index,
            "format": self.format,
        }


class Schema(BaseModel):
    metadata: Dict[str, Any]
    columns: Dict[str, Column]
    
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        
        metadata = self.metadata
        self._dataset_metadata = DatasetMetadata(
            layer=metadata.get("layer"),
            domain=metadata.get("domain"), 
            dataset=metadata.get("dataset"),
            version=metadata.get("version")
        )
        self._sensitivity = metadata.get("sensitivity", "")
        self._description = metadata.get("description", "")
        self._key_value_tags = metadata.get("key_value_tags", {})
        self._key_only_tags = metadata.get("key_only_tags", [])
        self._owners = [Owner(**owner) for owner in metadata.get("owners", [])] if metadata.get("owners") else None
        self._update_behaviour = metadata.get("update_behaviour", UpdateBehaviour.APPEND)
        self._is_latest_version = metadata.get("is_latest_version", True)
        
        pandera_metadata = {
            "layer": self._dataset_metadata.layer,
            "domain": self._dataset_metadata.domain,
            "dataset": self._dataset_metadata.dataset,
            "version": self._dataset_metadata.version,
            "sensitivity": self._sensitivity,
            "description": self._description,
            "key_value_tags": self._key_value_tags,
            "key_only_tags": self._key_only_tags,
            "owners": self._owners,
            "update_behaviour": self._update_behaviour,
            "is_latest_version": self._is_latest_version,
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

    @property
    def dataset_metadata(self) -> DatasetMetadata:
        return self._dataset_metadata

    def get_layer(self) -> str:
        return self._dataset_metadata.layer

    def get_domain(self) -> str:
        return self._dataset_metadata.domain

    def get_dataset(self) -> str:
        return self._dataset_metadata.dataset

    def get_description(self) -> str:
        return self._description

    def get_sensitivity(self) -> str:
        return self._sensitivity

    def get_version(self) -> int:
        return self._dataset_metadata.version

    def get_tags(self) -> Dict[str, str]:
        return {**self._key_value_tags, **dict.fromkeys(self._key_only_tags, "")}

    def get_owners(self) -> Optional[List[Owner]]:
        return self._owners

    def get_update_behaviour(self) -> str:
        return self._update_behaviour

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
        return {"Name": name, "Type": column.dtype}

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

    def string_representation(self) -> str:
        return f"{self.get_layer()}_{self.get_domain()}_{self.get_dataset()}_v{self.get_version()}"

    def dataset_identifier(self, with_version: bool = True) -> str:
        base = f"{self.get_layer()}_{self.get_domain()}_{self.get_dataset()}"
        if with_version:
            return f"{base}_v{self.get_version()}"
        return base

    def dict(self, exclude: str = None) -> dict:
        layer_value = self.get_layer()
        if hasattr(layer_value, "value"):
            layer_value = layer_value.value

        update_behaviour = self.get_update_behaviour()
        if hasattr(update_behaviour, "value"):
            update_behaviour = update_behaviour.value

        owners = self.get_owners()
        if owners:
            owners = [owner.dict() if hasattr(owner, 'dict') else owner for owner in owners]

        columns_dict = {}
        for column_name, column in self.columns.items():
            columns_dict[column_name] = column.to_dict()

        result = {
            "metadata": {
                "layer": layer_value,
                "domain": self.get_domain(),
                "dataset": self.get_dataset(),
                "version": self.get_version(),
                "sensitivity": self.get_sensitivity(),
                "description": self.get_description(),
                "update_behaviour": update_behaviour,
                "key_value_tags": self._key_value_tags,
                "key_only_tags": self._key_only_tags,
                "owners": owners,
                "is_latest_version": self._is_latest_version,
            },
            "columns": columns_dict,
        }

        if exclude:
            result.pop(exclude, None)

        return result