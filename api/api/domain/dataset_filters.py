from typing import Optional, Dict, List

from pydantic.main import BaseModel

from api.common.custom_exceptions import UserError


class DatasetFilters(BaseModel):
    sensitivity: Optional[str] = None
    key_value_tags: Optional[Dict[str, Optional[str]]] = dict()
    key_only_tags: Optional[List[str]] = list()

    def format_resource_query(self):
        if self.sensitivity and any(
            [key == "sensitivity" for key, _ in self.key_value_tags.items()]
        ):
            raise UserError(
                "You cannot specify sensitivity both at the root level and in the tags"
            )
        return [*self._tag_filters(), *self._sensitivity_filters()]

    def _tag_filters(self) -> List[Dict]:

        key_value_tags_dict_list = self._build_key_value_tags()

        key_only_tags_dict_list = self._build_key_only_tags()

        return key_value_tags_dict_list + key_only_tags_dict_list

    def _build_key_only_tags(self):
        return [{"Key": key, "Values": []} for key in self.key_only_tags]

    def _build_key_value_tags(self):
        return [
            {"Key": key, "Values": [value] if value is not None and value != "" else []}
            for key, value in self.key_value_tags.items()
        ]

    def _sensitivity_filters(self) -> List[Dict]:
        return (
            [{"Key": "sensitivity", "Values": [self.sensitivity]}]
            if self.sensitivity is not None
            else []
        )
