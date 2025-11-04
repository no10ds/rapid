# Note: This class is replicated in the api code, they should be de-duplicated once the external dependencies are removed from the API
from strenum import StrEnum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, ConfigDict
import pandera


class SensitivityLevel(StrEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    PROTECTED = "PROTECTED"


class UpdateBehaviour(StrEnum):
    APPEND = "APPEND"
    OVERWRITE = "OVERWRITE"


class Owner(BaseModel):
    name: str
    email: str


class SchemaMetadata(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    layer: str
    domain: str
    dataset: str
    sensitivity: SensitivityLevel
    owners: List[Owner]
    version: Optional[int] = None
    key_value_tags: Optional[Dict[str, str]] = {}
    key_only_tags: Optional[List[str]] = []
    description: Optional[str] = ""
    update_behaviour: Optional[str] = "APPEND"
    is_latest_version: Optional[bool] = True


class Column(BaseModel):
    name: str
    partition_index: Optional[int]
    data_type: str
    allow_null: bool
    format: Optional[str] = None
    unique: bool = False
    checks: Dict[str, Any] = {}

    def is_of_data_type(self, d_type: StrEnum) -> bool:
        return self.data_type in list(d_type)
    
    def to_pandera_column(self) -> pandera.Column:
        """
        Convert Column to Pandera Column for Pandera data validation.
        Note: The 'data_type' attribute should not be used in Pandera Column as we
        have our own custom data type validation.
        """

        pandera_checks = []
        for check in self.checks.values():
            if isinstance(check, dict):
                pandera_checks.append(self._dict_to_pandera_check(check))
            else:
                pandera_checks.append(check)

        return pandera.Column(
            name=self.name,
            nullable=self.allow_null,
            unique=self.unique,
            checks=pandera_checks,
        )

    def _dict_to_pandera_check(self, check_dict: Dict[str, Any]) -> pandera.Check:
        """Convert dictionary representation to Pandera check"""
        check_type = check_dict.get("check_type")
        params = check_dict.get("parameters", {})

        if check_type == "in_range":
            min_val = params.get("min_value")
            max_val = params.get("max_value")
            return pandera.Check.in_range(min_value=min_val, max_value=max_val)
        elif check_type == "isin":
            allowed_values = params.get("allowed_values", [])
            return pandera.Check.isin(allowed_values)
        elif check_type == "str_length":
            min_val = params.get("min_value")
            max_val = params.get("max_value")
            return pandera.Check.str_length(min_value=min_val, max_value=max_val)
        elif check_type == "greater_than":
            min_val = params.get("min_value")
            return pandera.Check.greater_than(min_val)
        elif check_type == "less_than":
            max_val = params.get("max_value")
            return pandera.Check.less_than(max_val)
        elif check_type == "str_matches":
            pattern = params.get("pattern")
            return pandera.Check.str_matches(pattern)
        else:
            raise ValueError(f"Unsupported check type: {check_type}. Valid types are: "
                             "in_range, isin, str_length, greater_than, less_than, str_matches.")


class Schema(BaseModel):
    """
    A Schema is a Pydantic class representing a rAPId schema. It allows you to programmatically define
    a schema to generate, create and update within rAPId.

    Example:
        A Schema can be created by setting the values literally into the classes like
        example below::

            schema = Schema(
                metadata=SchemaMetadata(
                    layer='default',
                    domain="domain",
                    dataset="dataset",
                    sensitivity=SensitivityLevel.PUBLIC,
                    owners=[Owner(name="test", version="test@email.com")]
                ),
                columns=[
                    Column(
                        name="column_a",
                        data_type="Float64",
                        allow_null=True
                    )
                ]
            )

        The alternative is you can create a schema directly from a Python dictionary
        specifying the values like in the example below::

            schema = Schema(
                **{
                    "metadata": {
                        ....
                    },
                    "columns": {
                        ....
                    }
                }
            )
    """

    metadata: SchemaMetadata
    columns: List[Column]

    def are_columns_the_same(
        self, new_columns: Union[List[Column], List[dict]]
    ) -> bool:
        """
        Checks that for a given Schema, does it's columns match the columns being passed
        into this function.

        Args:
            new_columns (Union[List[Column], List[dict]]): The new columns can be passed as either
                a list of Column defined classes or as a list of Python dictionaries representing
                the values. If the later is chosen and there is an incorrect value passed the function
                will raise a `rapid.exceptions.ColumnNotDifferentException`.

        Returns:
            bool: True If the new columns match the columns in the Schema otherwise False
        """
        if all(isinstance(col, dict) for col in new_columns):
            new_columns = [Column(**col) for col in new_columns]

        return self.columns == new_columns
