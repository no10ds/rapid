import json
from typing import List, Optional, TYPE_CHECKING

from pydantic import BaseModel
from api.common.config.aws import DATA_BUCKET
from api.common.config.layers import Layer
from api.common.logger import AppLogger

if TYPE_CHECKING:
    from api.application.services.schema_service import SchemaService


LAYER = "layer"
DOMAIN = "domain"
DATASET = "dataset"
VERSION = "version"


class DatasetMetadata(BaseModel):
    layer: Layer
    domain: str
    dataset: str
    version: Optional[int] = None

    def __init__(
        self,
        layer: Layer = None,
        domain: str = None,
        dataset: str = None,
        version: Optional[int] = None,
        **kwargs,
    ) -> None:
        """
        Override the default BaseModel init so that the class can be instantiated without keyword arguments.
        This is for our ease of use, given how widely used the class is.
        """
        expected_inputs = {
            LAYER: layer,
            DOMAIN: domain.lower() if domain else None,
            DATASET: dataset,
            VERSION: version,
        }
        # Only include arguments if they're not None.
        # This code ensures that Pydantic returns a descriptive error: `ValidationError: field <field> missing`.
        # Without this, we get the less intuitive error: `ValidationError: None passed for field <field>`.
        kwargs |= {key: value for key, value in expected_inputs.items() if value}
        super(DatasetMetadata, self).__init__(
            **kwargs,
        )

    @classmethod
    def get_fields(cls) -> List[str]:
        return list(cls.model_fields.keys())

    def to_dict(self):
        return {
            LAYER: self.layer,
            DOMAIN: self.domain,
            DATASET: self.dataset,
            VERSION: self.version,
        }

    def __hash__(self):
        return hash(json.dumps(self.to_dict()))

    def __lt__(self, other):
        return self.dataset_location() < other.dataset_location()

    def get_layer(self) -> str:
        return self.layer

    def get_domain(self) -> str:
        return self.domain

    def get_dataset(self) -> str:
        return self.dataset

    def get_version(self) -> int:
        return self.version

    def dataset_identifier(self, with_version: bool = True) -> str:
        """Dataset unique path, lower the case of dataset to make the paths that it uses case insensitive."""
        if with_version:
            return f"{self.layer}/{self.domain}/{self.dataset.lower()}/{self.version}"
        else:
            return f"{self.layer}/{self.domain}/{self.dataset.lower()}"

    def dataset_location(self, with_version: bool = True) -> str:
        return f"data/{self.dataset_identifier(with_version=with_version)}"

    def raw_data_location(self) -> str:
        return f"{self.construct_raw_dataset_uploads_location()}/{self.version}"

    def raw_data_path(self, filename: str) -> str:
        return f"{self.raw_data_location()}/{filename}"

    def glue_table_prefix(self):
        return f"{self.layer}_{self.domain}_{self.dataset.lower()}_"

    def glue_table_name(self) -> str:
        return f"{self.glue_table_prefix()}{self.version}"

    def s3_path(self) -> str:
        return f"s3://{DATA_BUCKET}/{self.dataset_location(with_version=False)}/"

    def s3_file_location(self) -> str:
        return f"s3://{DATA_BUCKET}/{self.dataset_location()}"

    def construct_raw_dataset_uploads_location(self):
        return f"raw_data/{self.dataset_identifier(with_version=False)}"

    def string_representation(self) -> str:
        if self.version:
            return f"layer [{self.layer}], domain [{self.domain}], dataset [{self.dataset}] and version [{self.version}]"
        else:
            return f"layer [{self.layer}], domain [{self.domain}] and dataset [{self.dataset}]"

    def set_version(self, schema_service: "SchemaService"):
        if not self.version:
            AppLogger.info(
                "No version provided by the user. Retrieving the latest version from the schema"
            )
            self.version = schema_service.get_latest_schema_version(self)
