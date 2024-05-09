from enum import Enum
from typing import Optional, List
from pydantic.main import BaseModel


class SortDirection(Enum):
    ASC = "ASC"
    DESC = "DESC"


class SQLQueryOrderBy(BaseModel):
    column: str
    direction: SortDirection = SortDirection("ASC")


class Query(BaseModel):
    """
    A Query is a Pydantic class representing a rAPId compatible data query. It allows for programmatic definition
    of data queries. See the rAPId specific [documentation](</api/query>)
    on how to write a valid query.

    Example:
        A query can created by setting the values literally into the class like::

            query = Query(
                select_columns=["column_a", "column_b"],
                limit="5"
            )

        The alternative is you can create a schema directly from a Python dictionary::

            query = Query(
                **{
                    "select_columns": ["column_a", "column_b"],
                    "limit": "5"
                }
            )

    """

    select_columns: Optional[List[str]] = None
    filter: Optional[str] = None
    group_by_columns: Optional[List[str]] = None
    aggregation_conditions: Optional[str] = None
    order_by_columns: Optional[List[SQLQueryOrderBy]] = None
    limit: Optional[str] = None
