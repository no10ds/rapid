from strenum import StrEnum
from typing import List, Dict, Optional, Set
from pydantic import BaseModel, EmailStr

import awswrangler as wr
import pyarrow as pa
import pandera

from api.domain.dataset_metadata import DatasetMetadata
from api.domain.data_types import convert_pandera_column_to_athena

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


class Column(pandera.Column):
    def __init__(
        self,
        dtype,
        nullable: bool,
        partition_index: Optional[int] = None,
        format: Optional[str] = None,
        unique: bool = False,
        **kwargs
    ):
        super().__init__(dtype=dtype, nullable=nullable, unique=unique, **kwargs)

        if self.metadata is None:
            self.metadata = {}

        self.metadata["partition_index"] = partition_index
        self.metadata["format"] = format

    @property
    def partition_index(self) -> Optional[int]:
        return self.metadata.get("partition_index")

    @property
    def format(self) -> Optional[str]:
        return self.metadata.get("format")

    def is_of_data_type(self, d_type: StrEnum) -> bool:
        dtype_values = [item.value for item in d_type]
        dtype_str = str(self.dtype)
        return dtype_str in dtype_values

    def to_dict(self) -> dict:
        return {
            "dtype": convert_pandera_column_to_athena(self.dtype),
            "nullable": self.nullable,
            "unique": self.unique if hasattr(self, 'unique') else False,
            "metadata": {
                "partition_index": self.partition_index,
                "format": self.format,
            }
        }


class Schema(pandera.DataFrameSchema):
    def __init__(
        self,
        columns,
        dataset_metadata: DatasetMetadata,
        sensitivity: str,
        description: Optional[str] = "",
        key_value_tags: Dict[str, str] = dict(),
        key_only_tags: List[str] = list(),
        owners: Optional[List[Owner]] = None,
        update_behaviour: str = UpdateBehaviour.APPEND,
        is_latest_version: bool = True,
        **pandera_kwargs
    ):
        metadata = {
            "layer": dataset_metadata.layer,
            "domain": dataset_metadata.domain,
            "dataset": dataset_metadata.dataset,
            "version": dataset_metadata.version,
            "sensitivity": sensitivity,
            "description": description,
            "key_value_tags": key_value_tags,
            "key_only_tags": key_only_tags,
            "owners": owners,
            "update_behaviour": update_behaviour,
            "is_latest_version": is_latest_version,
        }

        super().__init__(columns=columns, metadata=metadata, **pandera_kwargs)

    @property
    def dataset_metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            layer=self.get_layer(),
            domain=self.get_domain(),
            dataset=self.get_dataset(),
            version=self.get_version(),
        )

    def get_layer(self) -> str:
        return self.metadata["layer"]

    def get_domain(self) -> str:
        return self.metadata["domain"]

    def get_dataset(self) -> str:
        return self.metadata["dataset"]

    def get_description(self) -> str:
        return self.metadata["description"]

    def get_sensitivity(self) -> str:
        return self.metadata["sensitivity"]

    def get_version(self) -> int:
        return self.metadata["version"]

    def get_tags(self) -> Dict[str, str]:
        return {**self.metadata["key_value_tags"], **dict.fromkeys(self.metadata["key_only_tags"], "")}

    def get_owners(self) -> Optional[List[Owner]]:
        return self.metadata["owners"]

    def get_update_behaviour(self) -> str:
        return self.metadata["update_behaviour"]

    def has_overwrite_behaviour(self) -> bool:
        return self.get_update_behaviour() == UpdateBehaviour.OVERWRITE

    def get_column_names(self) -> List[str]:
        return list(self.columns.keys())

    def get_partitions(self) -> List[str]:
        sorted_cols = self.get_partition_columns()
        return [column.name for column in sorted_cols]

    def get_partition_indexes(self) -> List[int]:
        sorted_cols = self.get_partition_columns()
        return [column.partition_index for column in sorted_cols]

    def get_data_types(self) -> Set[str]:
        return {str(column.dtype) for column in self.columns.values()}

    def get_columns_by_type(self, d_type: StrEnum) -> List[Column]:
        return [column for column in self.columns.values() if column.is_of_data_type(d_type)]

    def get_column_names_by_type(self, d_type: StrEnum) -> List[str]:
        return [
            name for name, column in self.columns.items()
            if column.is_of_data_type(d_type)
        ]

    def get_non_partition_columns_for_glue(self) -> List[dict]:
        return [
            self.convert_column_to_glue_format(name, col)
            for name, col in self.columns.items()
            if col.metadata.get("partition_index") is None
        ]

    def get_partition_columns_for_glue(self) -> List[dict]:
        return [
            self.convert_column_to_glue_format(col.name, col)
            for col in self.get_partition_columns()
        ]

    def convert_column_to_glue_format(self, name: str, column: Column):
        return {"Name": name, "Type": str(column.dtype)}

    def get_partition_columns(self) -> List[Column]:
        return sorted(
            [column for column in self.columns.values() if column.partition_index is not None],
            key=lambda x: x.partition_index,
        )

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

    def dict(self, exclude: dict = None) -> dict:
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
                "key_value_tags": self.metadata.get("key_value_tags"),
                "key_only_tags": self.metadata.get("key_only_tags"),
                "owners": owners,
                "is_latest_version": self.metadata.get("is_latest_version"),
            },
            "columns": columns_dict,
        }

        if exclude:
            for key, value in exclude.items():
                if key == "metadata" and isinstance(value, dict):
                    for field in value:
                        result.pop(field, None)
                else:
                    result.pop(key, None)

        return result
    
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        """Provide a JSON schema for OpenAPI documentation"""
        return {
            "type": "object",
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "layer": {"type": "string"},
                        "domain": {"type": "string"},
                        "dataset": {"type": "string"},
                        "version": {"type": "integer"},
                        "sensitivity": {"type": "string"},
                        "description": {"type": "string"},
                        "update_behaviour": {"type": "string", "enum": ["APPEND", "OVERWRITE"]},
                        "tags": {"type": "object", "additionalProperties": {"type": "string"}},
                        "owners": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "email": {"type": "string", "format": "email"}
                                }
                            }
                        }
                    },
                    "required": ["layer", "domain", "dataset", "sensitivity"]
                },
                "columns": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "partition_index": {"type": "integer", "nullable": True},
                            "dtype": {"type": "string"},
                            "nullable": {"type": "boolean"},
                            "format": {"type": "string", "nullable": True},
                            "unique": {"type": "boolean"}
                        }
                    }
                }
            },
            "required": ["metadata", "columns"]
        }