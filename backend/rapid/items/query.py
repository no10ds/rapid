import logging
from strenum import StrEnum
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlidps import SQLi, PotentialSQLiPayload

logger = logging.getLogger(__name__)


class SortDirection(StrEnum):
    ASC = "ASC"
    DESC = "DESC"


class QueryOrderBy(BaseModel):
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

    model_config = ConfigDict(extra='forbid')

    select_columns: Optional[List[str]] = None
    filter: Optional[str] = None
    group_by_columns: Optional[List[str]] = None
    aggregation_conditions: Optional[str] = None
    order_by_columns: Optional[List[QueryOrderBy]] = None
    limit: Optional[int] = None

    def validate_for_sql_injection(self) -> None:
        """
        Validates the query for SQL injection attacks using sqlidps library.

        Raises:
            ValueError: If query contains potential SQL injection
        """
        logger.info("Starting SQL injection validation")

        if self.filter:
            logger.info(f"Checking filter: {self.filter}")
            try:
                SQLi.check(self.filter)
            except PotentialSQLiPayload:
                logger.warning(f"SQL injection detected in filter: '{self.filter}'")
                raise ValueError(f"Potential SQL injection detected in filter: '{self.filter}'")

        if self.aggregation_conditions:
            logger.info(f"Checking aggregation_conditions: {self.aggregation_conditions}")
            try:
                SQLi.check(self.aggregation_conditions)
            except PotentialSQLiPayload:
                logger.warning(f"SQL injection detected in aggregation_conditions: '{self.aggregation_conditions}'")
                raise ValueError(f"Potential SQL injection detected in aggregation_conditions: '{self.aggregation_conditions}'")

        logger.info("SQL injection validation passed")

    def to_sql(self, table_name: str) -> str:
        select = (
            f"SELECT {self._generate_select_columns()} FROM {table_name}"  # nosec: B608
        )
        filter = self._generate_filter()
        group_by = self._generate_group_by_columns()
        aggregation_conditions = self._generate_aggregation_conditions()
        order_by = self._generate_order_by_columns()
        limit = self._generate_limit()
        constructed_sql = (
            f"{select}{filter}{group_by}{aggregation_conditions}{order_by}{limit}"
        )
        return constructed_sql

    def _generate_select_columns(self):
        columns = self._generate_columns(self.select_columns, "")
        if columns == "":
            return "*"
        else:
            return columns

    def _generate_filter(self):
        if self.filter is not None and self.filter != "":
            return f" WHERE {self.filter}"
        return ""

    def _generate_group_by_columns(self):
        return self._generate_columns(self.group_by_columns, " GROUP BY ")

    def _generate_aggregation_conditions(self):
        if (
            self.aggregation_conditions is not None
            and self.aggregation_conditions != ""
        ):
            return f" HAVING {self.aggregation_conditions}"
        return ""

    def _generate_order_by_columns(self):
        if self.order_by_columns is None or len(self.order_by_columns) == 0:
            return ""
        columns = ",".join(
            [
                f"{order_by.column} {order_by.direction}"
                for order_by in self.order_by_columns
                if order_by is not None and order_by.column != ""
            ]
        )
        return " ORDER BY " + columns

    def _generate_limit(self):
        if self.limit is not None and self.limit != "":
            return " LIMIT " + str(self.limit)
        return ""

    def _generate_columns(self, column_list, prefix):
        if column_list is None or len(column_list) == 0:
            return ""
        columns = ",".join(
            [column for column in column_list if column != "" and column is not None]
        )
        return prefix + columns
