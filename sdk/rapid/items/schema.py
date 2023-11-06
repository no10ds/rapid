from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic.main import BaseModel


class SensitivityLevel(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    PROTECTED = "PROTECTED"


class UpdateBehaviour(Enum):
    APPEND = "APPEND"
    OVERWRITE = "OVERWRITE"


class Owner(BaseModel):
    name: str
    email: str


class SchemaMetadata(BaseModel):
    layer: str
    domain: str
    dataset: str
    sensitivity: SensitivityLevel
    owners: List[Owner]
    version: Optional[int] = None
    key_value_tags: Optional[Dict[str, str]] = {}
    key_only_tags: Optional[List[str]] = []

    class Config:
        use_enum_values = True


class Column(BaseModel):
    name: str
    data_type: str
    partition_index: Optional[int] = None
    allow_null: bool = True
    format: Optional[str] = None


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
