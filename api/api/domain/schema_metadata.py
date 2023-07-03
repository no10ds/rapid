from dataclasses import dataclass
from typing import Dict, List, Optional, TYPE_CHECKING
import json

from pydantic import BaseModel, EmailStr

from api.common.config.auth import SensitivityLevel
from api.common.config.aws import SCHEMAS_LOCATION
from api.common.custom_exceptions import SchemaNotFoundError
from api.common.data_parsers import parse_categorisation
from api.common.utilities import BaseEnum

if TYPE_CHECKING:
    from api.adapter.s3_adapter import S3Adapter


class Owner(BaseModel):
    name: str
    email: EmailStr


class UpdateBehaviour(BaseEnum):
    APPEND = "APPEND"
    OVERWRITE = "OVERWRITE"


class SchemaMetadata(BaseModel):
    domain: str
    dataset: str
    sensitivity: str
    version: Optional[int]
    description: Optional[str] = ""
    key_value_tags: Dict[str, str] = dict()
    key_only_tags: List[str] = list()
    owners: Optional[List[Owner]] = None
    update_behaviour: str = UpdateBehaviour.APPEND.value

    def get_domain(self) -> str:
        return self.domain

    def get_dataset(self) -> str:
        return self.dataset

    def get_sensitivity(self) -> str:
        return self.sensitivity

    def get_version(self) -> int:
        return self.version

    def get_description(self) -> str:
        return self.description

    def schema_path(self) -> str:
        return f"{SCHEMAS_LOCATION}/{self.sensitivity}/{self.schema_name()}"

    def schema_name(self) -> str:
        return f"{self.domain}/{self.dataset}/{self.version}/schema.json"

    @classmethod
    def from_path(cls, path: str, s3_adapter: "S3Adapter"):
        sensitivity = parse_categorisation(path, SensitivityLevel.values(), "PUBLIC")
        if path.endswith("schema.json"):
            try:
                data = s3_adapter.retrieve_data(path).read()
                data_json = json.loads(data)
                metadata = data_json["metadata"]

                if metadata:
                    return cls(
                        domain=metadata["domain"],
                        dataset=metadata["dataset"],
                        sensitivity=metadata["sensitivity"],
                        description=metadata["description"],
                        version=metadata["version"],
                    )
                else:
                    raise Exception
            except Exception:
                split_path = path.split("/")
                domain = split_path[-4]
                dataset = split_path[-3]
                version = split_path[-2]
                return cls(
                    domain=domain,
                    dataset=dataset,
                    sensitivity=sensitivity,
                    description="",
                    version=version,
                )

        else:
            domain, dataset = path.split("/")[-1].replace(".json", "").split("-")
            return cls(
                domain=domain, dataset=dataset, sensitivity=sensitivity, description=""
            )

    def get_custom_tags(self) -> Dict[str, str]:
        return {**self.key_value_tags, **dict.fromkeys(self.key_only_tags, "")}

    def get_tags(self) -> Dict[str, str]:
        return {
            **self.get_custom_tags(),
            "sensitivity": self.get_sensitivity(),
            "no_of_versions": str(self.get_version()),
        }

    def get_owners(self) -> Optional[List[Owner]]:
        return self.owners

    def get_update_behaviour(self) -> str:
        return self.update_behaviour

    def remove_duplicates(self):
        updated_key_only_list = []

        if len(self.key_only_tags) != 0 and self.key_value_tags:
            for key in self.key_only_tags:
                if key not in self.key_value_tags.keys():
                    updated_key_only_list.append(key)

        self.key_only_tags = updated_key_only_list


@dataclass
class SchemaMetadatas:
    metadatas: List[SchemaMetadata]

    def find(self, domain: str, dataset: str, version: int) -> SchemaMetadata:
        try:
            return list(
                filter(
                    lambda data: data.domain == domain
                    and data.dataset == dataset
                    and data.version == version,
                    self.metadatas,
                )
            )[0]
        except IndexError:
            raise SchemaNotFoundError(
                f"Schema not found for domain={domain} and dataset={dataset} and version={version}"
            )

    @classmethod
    def empty(cls):
        return cls([])
