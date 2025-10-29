from typing import List, Union
from strenum import StrEnum

from api.domain.dataset_metadata import DatasetMetadata, DATASET
from api.domain.schema_metadata import DESCRIPTION
from api.domain.schema import COLUMNS


class MatchField(StrEnum):
    Dataset = DATASET
    Description = DESCRIPTION
    Columns = COLUMNS


class SearchMetadata(DatasetMetadata):
    matching_data: Union[str, List[str]]
    matching_field: MatchField
