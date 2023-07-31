from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
from strenum import StrEnum

from api.domain.dataset_metadata import DatasetMetadata


class Owner(BaseModel):
    name: str
    email: EmailStr


class UpdateBehaviour(StrEnum):
    APPEND = "APPEND"
    OVERWRITE = "OVERWRITE"


class SchemaMetadata(DatasetMetadata):
    sensitivity: str
    description: Optional[str] = ""
    key_value_tags: Dict[str, str] = dict()
    key_only_tags: List[str] = list()
    owners: Optional[List[Owner]] = None
    update_behaviour: str = UpdateBehaviour.APPEND
    is_latest_version: bool = True

    def get_sensitivity(self) -> str:
        return self.sensitivity

    def get_description(self) -> str:
        return self.description

    def get_custom_tags(self) -> Dict[str, str]:
        return {**self.key_value_tags, **dict.fromkeys(self.key_only_tags, "")}

    def get_tags(self) -> Dict[str, str]:
        return {
            **self.get_custom_tags(),
            "sensitivity": self.get_sensitivity(),
            "no_of_versions": str(self.get_version()),
            "layer": self.get_layer(),
            "domain": self.get_domain(),
        }

    def get_owners(self) -> Optional[List[Owner]]:
        return self.owners

    def get_update_behaviour(self) -> str:
        return self.update_behaviour

    def get_is_latest_version(self) -> bool:
        return self.is_latest_version

    def remove_duplicates(self):
        updated_key_only_list = []

        if len(self.key_only_tags) != 0 and self.key_value_tags:
            for key in self.key_only_tags:
                if key not in self.key_value_tags.keys():
                    updated_key_only_list.append(key)

        self.key_only_tags = updated_key_only_list
