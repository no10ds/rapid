from strenum import StrEnum
from typing import List, Dict, Optional, Set
from pydantic import BaseModel, EmailStr

import awswrangler as wr
import pyarrow as pa
import pandera

from api.domain.dataset_metadata import DatasetMetadata

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
        name: str, 
        data_type: str, 
        allow_null: bool, 
        partition_index: Optional[int] = None, 
        format: Optional[str] = None, 
        unique: bool = False, 
        **kwargs
    ):
        super().__init__(name=name, dtype=data_type, nullable=allow_null, unique=unique, **kwargs)
        
        self.metadata["partition_index"] = partition_index
        self.metadata["format"] = format

    @property
    def partition_index(self) -> Optional[int]:
        return self.metadata.get("partition_index")
    
    @property
    def format(self) -> Optional[str]:
        return self.metadata.get("format")
    
    def is_of_data_type(self, d_type: StrEnum) -> bool:
        return str(self.dtype) in list(d_type)

class Schema(pandera.DataFrameSchema):
    def __init__(
        self,
        columns,
        dataset_metadata: DatasetMetadata,
        sensitivity: str,
        description: Optional[str] = "",
        key_value_tags: Dict[str, str] = None,
        key_only_tags: List[str] = None,
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
            "schema": {
                "sensitivity": sensitivity,
                "description": description,
                "key_value_tags": key_value_tags,
                "key_only_tags": key_only_tags,
                "owners": owners,
                "update_behaviour": update_behaviour,
                "is_latest_version": is_latest_version,
            }
        }
        
        super().__init__(columns=columns, metadata=metadata, **pandera_kwargs)

    @property
    def dataset_metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            layer=self.get_layer(),
            domain=self.get_domain(),
        )

    def column_has_data_type(self, column: Column, d_type: StrEnum) -> bool:
        return str(column.dtype) in [dt.value for dt in d_type]

    def get_layer(self) -> str:
        return self.metadata["layer"]

    def get_domain(self) -> str:
        return self.metadata["domain"].lower()

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
        return [name for name, _ in sorted_cols]

    def get_partition_indexes(self) -> List[int]:
        sorted_cols = self.get_partition_columns()
        return [column.partition_index for _, column in sorted_cols]

    def get_data_types(self) -> Set[str]:
        return {str(column.dtype) for column in self.columns.values()}

    def get_columns_by_type(self, d_type: StrEnum) -> List[Column]:
        return [column for column in self.columns.values() if self.column_has_data_type(column, d_type)]

    def get_column_names_by_type(self, d_type: StrEnum) -> List[str]:
        return [
            name for name, column in self.columns.items() 
            if self.column_has_data_type(column, d_type)
        ]

    def get_non_partition_columns_for_glue(self) -> List[dict]:
        return [
            self.convert_column_to_glue_format(name, col)
            for name, col in self.columns.items()
            if col.metadata.get("partition_index") is None
        ]

    def get_partition_columns_for_glue(self) -> List[dict]:
        return [
            self.convert_column_to_glue_format(name, col)
            for name, col in self.get_partition_columns()
        ]

    def convert_column_to_glue_format(self, name: str, column: Column):
        return {"Name": name, "Type": str(column.dtype)}

    def get_partition_columns(self) -> List[tuple]:
        partition_cols = [
            (name, column) for name, column in self.columns.items()
            if column.partition_index is not None
        ]
        return sorted(partition_cols, key=lambda x: x[1].metadata.get("partition_index"))

    def generate_storage_schema(self) -> pa.schema:
        return pa.schema(
            [
                pa.field(name, wr._data_types.athena2pyarrow(str(column.dtype)))
                for name, column in self.columns.items()
            ]
        )