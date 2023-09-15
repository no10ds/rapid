from functools import reduce
from typing import Callable, Optional, Dict, List, Union

from boto3.dynamodb.conditions import Attr, And, ConditionBase, Contains, Equals, In
from pydantic.main import BaseModel


from api.common.custom_exceptions import UserError
from api.common.config.auth import Layer
from api.domain.dataset_metadata import LAYER, DOMAIN
from api.domain.schema_metadata import SENSITIVITY, KEY_ONLY_TAGS, KEY_VALUE_TAGS


class DatasetFilters(BaseModel):
    layer: Optional[Union[List[Layer], Layer]] = None
    domain: Optional[Union[List[str], str]] = None
    sensitivity: Optional[Union[List[str], str]] = None
    key_value_tags: Optional[Dict[str, Optional[str]]] = dict()
    key_only_tags: Optional[List[str]] = list()

    def combine_conditions(func: Callable[..., List[ConditionBase]]) -> And:
        """Combines a list of conditions into a single And condition"""

        def inner(*args, **kwargs):
            conditions = func(*args, **kwargs)
            conditions = [condition for condition in conditions if condition]
            if conditions:
                if len(conditions) == 1:
                    return conditions[0]
                else:
                    return reduce(lambda x, y: x & y, conditions)

        return inner

    @combine_conditions
    def format_resource_query(self):
        if self.sensitivity and any(
            [key == SENSITIVITY for key, _ in self.key_value_tags.items()]
        ):
            raise UserError(
                "You cannot specify sensitivity both at the root level and in the tags"
            )
        return [
            self.build_key_value_tags(),
            self.build_key_only_tags(),
            self.build_generic_filter(SENSITIVITY, self.sensitivity),
            self.build_generic_filter(LAYER, self.layer),
            self.build_generic_filter(DOMAIN, self.domain.lower()),
        ]

    @combine_conditions
    def build_key_only_tags(self) -> List[Contains]:
        return [Attr(KEY_ONLY_TAGS).contains(key) for key in self.key_only_tags]

    @combine_conditions
    def build_key_value_tags(self) -> List[Equals]:
        return [
            Attr(f"{KEY_VALUE_TAGS}.{key}").eq(value)
            for key, value in self.key_value_tags.items()
            if value is not None and value != ""
        ]

    @staticmethod
    def build_generic_filter(
        name: str, value: Union[List[str], str]
    ) -> Union[Equals, In]:
        if value:
            if isinstance(value, list):
                return Attr(name).is_in(value)
            else:
                return Attr(name).eq(value)
