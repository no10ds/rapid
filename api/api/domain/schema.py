from strenum import StrEnum
from typing import List, Dict, Optional, Set, Any

import awswrangler as wr
from pydantic.main import BaseModel
import pyarrow as pa
import pandera

from api.domain.schema_metadata import Owner, SchemaMetadata, UpdateBehaviour
from api.domain.data_types import convert_athena_to_pandera_type

METADATA = "metadata"
COLUMNS = "columns"


class Column(BaseModel):
    name: str
    partition_index: Optional[int]
    data_type: str
    allow_null: bool
    format: Optional[str] = None
    unique: bool = False
    validation_checks: Optional[List[Dict[str, Any]]] = None

    def is_of_data_type(self, d_type: StrEnum) -> bool:
        return self.data_type in list(d_type)


class Schema(BaseModel):
    metadata: SchemaMetadata
    columns: List[Column]

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
    
    def _convert_data_type(self, data_type: str) -> str:
        """Convert Athena data type to Pandera data type for Pandera validation."""
        return convert_athena_to_pandera_type(data_type)
    
    def _convert_validation_checks(self, validation_checks: Optional[List[Dict[str, Any]]]) -> List[pandera.Check]:
        """Convert validation check configs to Pandera Check objects."""
        if not validation_checks:
            return []
        
        check_mappings = {
            "in_range": {
                "constructor": pandera.Check.in_range,
                "param_mapping": {
                    "min_value": "min_val",
                    "max_value": "max_val"
                }
            },
            "isin": {
                "constructor": pandera.Check.isin,
                "param_mapping": {
                    "values": "values"
                }
            }
        }
        
        pandera_checks = []
        
        for check in validation_checks:
            check_type = check["type"]
            params = check["params"]
            
            if check_type not in check_mappings:
                raise ValueError(f"Unsupported validation check: {check_type}")
            
            mapping = check_mappings[check_type]
            
            try:
                pandera_params = {
                    pandera_param: params.get(config_param)
                    for pandera_param, config_param in mapping["param_mapping"].items()
                }
                
                pandera_checks.append(mapping["constructor"](**pandera_params))
                
            except Exception as e:
                raise ValueError(f"Invalid parameters for '{check_type}' check: {params}. Error: {str(e)}")
        
        return pandera_checks
    
    def generate_pandera_schema(self) -> pandera.DataFrameSchema:
        """Convert our rapid schema to Pandera schema format."""
        pandera_columns = {}

        for column in self.columns:
            converted_checks = self._convert_validation_checks(column.validation_checks)
            
            pandera_columns[column.name] = pandera.Column(
                dtype=self._convert_data_type(column.data_type),
                checks=converted_checks, 
                nullable=column.allow_null,
                unique=column.unique,
            )

        return pandera.DataFrameSchema(
            columns=pandera_columns,
        )
