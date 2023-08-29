from typing import Dict, List, Optional, Union
from strenum import StrEnum

from api.domain.dataset_metadata import DatasetMetadata


class MatchField(StrEnum):
    Dataset = "Dataset"
    Description = "Description"
    Columns = "Columns"


class SearchMetadata(DatasetMetadata):
    matching_data: Union[str, List[str]]
    matching_field: MatchField
