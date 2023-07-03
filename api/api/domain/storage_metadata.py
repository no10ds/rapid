from dataclasses import dataclass
from typing import Optional

from api.common.config.aws import DATA_BUCKET


@dataclass(frozen=True)
class StorageMetaData:
    domain: str
    dataset: str
    version: Optional[int] = 1
    description: Optional[str] = ""

    def dataset_location(self) -> str:
        return self.construct_dataset_location()

    def file_location(self) -> str:
        return f"{self.construct_dataset_location()}/{self.version}"

    def raw_data_location(self) -> str:
        return f"{self.construct_raw_dataset_uploads_location()}/{self.version}"

    def raw_data_path(self, filename: str) -> str:
        return f"{self.raw_data_location()}/{filename}"

    def glue_table_prefix(self):
        return f"{self.domain}_{self.dataset}_"

    def get_ui_upload_path(self):
        return f"{self.domain}/{self.dataset}/{self.version}"

    def glue_table_name(self) -> str:
        return f"{self.glue_table_prefix()}{self.version}"

    def s3_path(self) -> str:
        return f"s3://{DATA_BUCKET}/{self.dataset_location()}/"

    def construct_dataset_location(self):
        return f"data/{self.domain}/{self.dataset}"

    def construct_raw_dataset_uploads_location(self):
        return f"raw_data/{self.domain}/{self.dataset}"

    def construct_schema_dataset_location(self, sensitvity: str):
        return f"data/schemas/{sensitvity}/{self.domain}/{self.dataset}"
