from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Extra

from api.common.logger import AppLogger


class SortDirection(Enum):
    ASC = "ASC"
    DESC = "DESC"


class SQLQueryOrderBy(BaseModel):
    column: str
    direction: SortDirection = SortDirection("ASC")


class SQLQuery(BaseModel):
    select_columns: Optional[List[str]] = None
    filter: Optional[str] = None
    group_by_columns: Optional[List[str]] = None
    aggregation_conditions: Optional[str] = None
    order_by_columns: Optional[List[SQLQueryOrderBy]] = None
    limit: Optional[str] = None

    class Config:
        extra = Extra.forbid

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
        AppLogger.info(f"Constructed SQL from input query: {constructed_sql}")
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
                f"{order_by.column} {order_by.direction.value}"
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
