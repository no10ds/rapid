from strenum import StrEnum
from typing import Optional, List, Union
from pydantic import BaseModel, ConfigDict, field_validator


def _validate_column_name(column: str, allow_empty: bool = False, allow_functions: bool = False) -> str:
    """Shared column name validation to prevent SQL injection"""
    if not column:
        if allow_empty:
            return column
        raise ValueError("Column name cannot be empty")

    allowed = ('_', '.')

    # Add function characters if needed
    if allow_functions:
        allowed = allowed + ('(', ')', '*', ',')

    if not all(c.isalnum() or c in allowed for c in column):
        raise ValueError(f"Invalid column name: {column}")

    return column


class SortDirection(StrEnum):
    ASC = "ASC"
    DESC = "DESC"

class LogicOperator(StrEnum):
    AND = "AND"
    OR = "OR"

class FilterOperator(StrEnum):
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"

class FilterCondition(BaseModel):
    column: str
    operator: FilterOperator
    value: Optional[Union[str, int, float, bool, List[Union[str, int, float, bool]]]] = None

    @field_validator('column')
    @classmethod
    def validate_column_name(cls, v: str) -> str:
        return _validate_column_name(v, allow_empty=False, allow_functions=True)

    @field_validator('value')
    @classmethod
    def validate_value_required(cls, v, info):
        operator = info.data.get('operator')
        if operator in [FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL]:
            if v is not None:
                raise ValueError(f"Operator {operator} should not have a value")
        else:
            if v is None:
                raise ValueError(f"Operator {operator} requires a value")
        return v

    def to_sql(self) -> str:
        """Convert filter condition to SQL string"""
        operator_str = self.operator.value

        # Handle NULL checks
        if self.operator in [FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL]:
            return f"{self.column} {operator_str}"

        # Handle IN and NOT IN operators
        if self.operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
            if not isinstance(self.value, list):
                raise ValueError(f"Operator {self.operator} requires a list value")
            escaped_values = [self._escape_value(v) for v in self.value]
            values_str = ", ".join(escaped_values)
            return f"{self.column} {operator_str} ({values_str})"

        # Handle standard comparison operators
        escaped_value = self._escape_value(self.value)
        return f"{self.column} {operator_str} {escaped_value}"

    @staticmethod
    def _escape_value(value: Union[str, int, float, bool]) -> str:
        """Escape a value for SQL usage"""
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # Escape single quotes by doubling them
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")

class FilterGroup(BaseModel):
    """
    A group of filter conditions combined with AND or OR logic.
    Supports nesting for complex boolean expressions.
    """
    logic_operator: Optional[LogicOperator] = None
    conditions: Optional[List[FilterCondition]] = None
    groups: Optional[List['FilterGroup']] = None

    def to_sql(self) -> str:
        """Convert filter group to SQL string"""
        parts = []

        if self.conditions:
            parts.extend([condition.to_sql() for condition in self.conditions])

        if self.groups:
            parts.extend([f"({group.to_sql()})" for group in self.groups])

        if not parts:
            return ""

        if len(parts) == 1:
            return parts[0]

        if not self.logic_operator:
            raise ValueError("logic_operator is required when you have multiple conditions or groups")

        return f" {self.logic_operator.value} ".join(parts)

class QueryOrderBy(BaseModel):
    column: str
    direction: SortDirection = SortDirection("ASC")

    @field_validator('column')
    @classmethod
    def validate_column_name(cls, v: str) -> str:
        return _validate_column_name(v, allow_empty=True, allow_functions=False)

class Query(BaseModel):
    """
    A Query is a Pydantic class representing a rAPId compatible data query. It allows for programmatic definition
    of data queries. See the rAPId specific [documentation](</api/query>)
    on how to write a valid query.

    Example:
        query = Query(
            **{
                "select_columns": ["column_a", "column_b"],
                "filter": {
                    "logic_operator": "AND",
                    "conditions": [
                        {"column": "column_one", "operator": ">", "value": 10}
                    ]
                },
                "limit": 5
            }
        )

    """

    model_config = ConfigDict(extra='forbid')

    select_columns: Optional[List[str]] = None
    filter: Optional[FilterGroup] = None
    group_by_columns: Optional[List[str]] = None
    aggregation_conditions: Optional[FilterGroup] = None
    order_by_columns: Optional[List[QueryOrderBy]] = None
    limit: Optional[int] = None

    @field_validator('select_columns')
    @classmethod
    def validate_select_columns(cls, v):
        if v is not None:
            for col in v:
                _validate_column_name(col, allow_empty=True, allow_functions=True)
        return v

    @field_validator('group_by_columns')
    @classmethod
    def validate_group_by_columns(cls, v):
        if v is not None:
            for col in v:
                _validate_column_name(col, allow_empty=True, allow_functions=False)
        return v

    def to_sql(self, table_name: str) -> str:
        select = f"SELECT {self._generate_select_columns()} FROM {table_name}"  # nosec: B608
        filter = self._generate_filter()
        group_by = self._generate_group_by_columns()
        aggregation_conditions = self._generate_aggregation_conditions()
        order_by = self._generate_order_by_columns()
        limit = self._generate_limit()
        return f"{select}{filter}{group_by}{aggregation_conditions}{order_by}{limit}"

    def _generate_select_columns(self):
        columns = self._generate_columns(self.select_columns, "")
        if columns == "":
            return "*"
        else:
            return columns

    def _generate_filter(self):
        if self.filter is None:
            return ""
        sql = self.filter.to_sql()
        return f" WHERE {sql}" if sql else ""

    def _generate_group_by_columns(self):
        return self._generate_columns(self.group_by_columns, " GROUP BY ")

    def _generate_aggregation_conditions(self):
        if self.aggregation_conditions is None:
            return ""
        sql = self.aggregation_conditions.to_sql()
        return f" HAVING {sql}" if sql else ""

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
