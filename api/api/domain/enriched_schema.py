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
    
    def __eq__(self, other):
        if not isinstance(other, EnrichedColumn):
            return False
        return (self.dtype == other.dtype and 
                self.nullable == other.nullable and
                self.partition_index == other.partition_index and
                self.format == other.format and
                self.unique == other.unique and
                self.statistics == other.statistics)


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

    def __eq__(self, other):
        if not isinstance(other, EnrichedSchema):
            return False
        
        base_equal = (
            self.columns == other.columns and
            self.dataset_metadata == other.dataset_metadata and
            self.get_sensitivity() == other.get_sensitivity() and
            self.get_description() == other.get_description() and
            self.get_tags() == other.get_tags() and
            self.get_owners() == other.get_owners() and
            self.get_update_behaviour() == other.get_update_behaviour() and
            self.metadata.get("is_latest_version") == other.metadata.get("is_latest_version")
        )
        
        enriched_equal = (
            self.number_of_rows == other.number_of_rows and
            self.number_of_columns == other.number_of_columns and
            self.last_updated == other.last_updated
        )
        
        return base_equal and enriched_equal