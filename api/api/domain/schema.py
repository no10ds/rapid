from strenum import StrEnum
from typing import List, Dict, Optional, Set, Any

import awswrangler as wr
from pydantic.main import BaseModel
import pyarrow as pa
import pandera

from api.domain.schema_metadata import Owner, SchemaMetadata, UpdateBehaviour

METADATA = "metadata"
COLUMNS = "columns"


class Column(BaseModel):
    name: str
    partition_index: Optional[int]
    data_type: str
    allow_null: bool
    format: Optional[str] = None
    unique: bool = False
    checks: Dict[str, Any] = {}

    def is_of_data_type(self, d_type: StrEnum) -> bool:
        return self.data_type in list(d_type)

    def to_pandera_column(self) -> pandera.Column:
        """
        Convert Column to Pandera Column for Pandera data validation.
        Note: The 'data_type' attribute should not be used in Pandera Column as we
        have our own custom data type validation.
        """

        pandera_checks = []
        for check in self.checks.values():
            if isinstance(check, dict):
                pandera_checks.append(self._dict_to_pandera_check(check))
            else:
                pandera_checks.append(check)

        return pandera.Column(
            name=self.name,
            nullable=self.allow_null,
            unique=self.unique,
            checks=pandera_checks,
        )

    def _dict_to_pandera_check(self, check_dict: Dict[str, Any]) -> pandera.Check:
        """Convert dictionary representation to Pandera check"""
        check_type = check_dict.get("check_type")
        params = check_dict.get("parameters", {})

        print("here")

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

    def pandera_validate(self, df, **kwargs):
        pandera_columns = {
            col.name: col.to_pandera_column()
            for col in self.columns
        }
        pandera_schema = pandera.DataFrameSchema(metadata=self.metadata, columns=pandera_columns)
        return pandera_schema.validate(df, **kwargs)
