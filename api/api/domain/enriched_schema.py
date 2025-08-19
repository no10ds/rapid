from typing import Dict, Optional

from api.domain.schema import Column, Schema

class EnrichedColumn(Column):
    def __init__(
        self,
        dtype: str,
        nullable: bool,
        partition_index: Optional[int] = None,
        format: Optional[str] = None,
        unique: bool = False,
        statistics: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        super().__init__(
            dtype=dtype,
            nullable=nullable,
            partition_index=partition_index,
            format=format,
            unique=unique,
            **kwargs
        )
        self.statistics = statistics


class EnrichedSchema(Schema):
    def __init__(
        self,
        columns,
        dataset_metadata,
        sensitivity: str,
        number_of_rows: int,
        number_of_columns: int,
        last_updated: str,
        **kwargs
    ):
        super().__init__(
            columns=columns,
            dataset_metadata=dataset_metadata,
            sensitivity=sensitivity,
            **kwargs
        )
        self.number_of_rows = number_of_rows
        self.number_of_columns = number_of_columns
        self.last_updated = last_updated