from typing import List, Dict, Optional

from pydantic import BaseModel

from rapid.items.schema import Column
from api.domain.schema_metadata import SchemaMetadata


class EnrichedColumn(Column):
    statistics: Optional[Dict[str, str]] = None


class EnrichedSchemaMetadata(SchemaMetadata):
    number_of_rows: int
    number_of_columns: int
    last_updated: str


class EnrichedSchema(BaseModel):
    metadata: EnrichedSchemaMetadata
    columns: List[EnrichedColumn]
