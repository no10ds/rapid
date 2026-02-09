import pytest

from rapid.items.query import Query, QueryOrderBy, FilterCondition, FilterGroup


class TestQuery:
    def test_all_parameters_empty_selects_all_rows_and_columns(self):
        sql_query = Query()
        assert sql_query.to_sql("test_domain") == "SELECT * FROM test_domain"

    def test_all_parameters_provided_with_empty_values(self):
        sql_query = Query(
            select_columns=[], order_by_columns=[], group_by_columns=[]
        )
        assert sql_query.to_sql("test_domain") == "SELECT * FROM test_domain"

    def test_only_select_columns_provided(self):
        sql_query = Query(select_columns=["col1", "col2", "col3"])
        assert (
            sql_query.to_sql("test_domain") == "SELECT col1,col2,col3 FROM test_domain"
        )

    def test_only_filters_provided(self):
        sql_query = Query(
            filter=FilterGroup(
                logic_operator="AND",
                conditions=[FilterCondition(column="col1", operator=">", value=16)]
            )
        )
        assert (
            sql_query.to_sql("test_domain")
            == "SELECT * FROM test_domain WHERE col1 > 16"
        )

    def test_single_filter_without_logic_operator(self):
        """Test single filter condition without specifying logic_operator"""
        sql_query = Query(
            filter=FilterGroup(
                conditions=[FilterCondition(column="col1", operator=">", value=16)]
            )
        )
        assert (
            sql_query.to_sql("test_domain")
            == "SELECT * FROM test_domain WHERE col1 > 16"
        )

    def test_only_order_by_columns_provided(self):
        sql_query = Query(
            order_by_columns=[
                QueryOrderBy(column=""),
                QueryOrderBy(column="col1"),
                QueryOrderBy(column="col2", direction="ASC"),
                QueryOrderBy(column="col3", direction="DESC"),
            ]
        )
        assert (
            sql_query.to_sql("test_domain")
            == "SELECT * FROM test_domain ORDER BY col1 ASC,col2 ASC,col3 DESC"
        )

    def test_only_group_by_columns_provided(self):
        sql_query = Query(group_by_columns=["col4", "col5"])
        assert (
            sql_query.to_sql("test_domain")
            == "SELECT * FROM test_domain GROUP BY col4,col5"
        )

    def test_only_limit_provided(self):
        sql_query = Query(limit="10")
        assert sql_query.to_sql("test_domain") == "SELECT * FROM test_domain LIMIT 10"

    def test_complex_query_with_all_clauses(self):
        sql_query = Query(
            select_columns=["col1", "col2", "col3"],
            filter=FilterGroup(
                logic_operator="AND",
                conditions=[FilterCondition(column="col2", operator="=", value=123)]
            ),
            group_by_columns=["col4", "col5"],
            aggregation_conditions=FilterGroup(
                logic_operator="AND",
                conditions=[FilterCondition(column="col4", operator="IN", value=['some value', 'another value'])]
            ),
            order_by_columns=[
                QueryOrderBy(column="col1"),
                QueryOrderBy(column="col2", direction="DESC"),
            ],
            limit=10
        )
        assert sql_query.to_sql("test_domain") == "SELECT col1,col2,col3 FROM test_domain WHERE col2 = 123 GROUP BY col4,col5 HAVING col4 IN ('some value', 'another value') ORDER BY col1 ASC,col2 DESC LIMIT 10"

    def test_query_with_aggregate_functions(self):
        sql_query = Query(
            select_columns=["col1", "avg(col2)"],
            filter=FilterGroup(
                logic_operator="AND",
                conditions=[FilterCondition(column="col2", operator=">=", value=100)]
            ),
            group_by_columns=["col1"],
            limit=50
        )
        assert sql_query.to_sql("test_domain") == "SELECT col1,avg(col2) FROM test_domain WHERE col2 >= 100 GROUP BY col1 LIMIT 50"


class TestFilterCondition:
    def test_filter_with_greater_than_operator(self):
        filter_condition = FilterCondition(column="age", operator=">", value=18)
        assert filter_condition.to_sql() == "age > 18"

    def test_filter_with_equals_operator(self):
        filter_condition = FilterCondition(column="status", operator="=", value="active")
        assert filter_condition.to_sql() == "status = 'active'"

    def test_filter_with_like_operator(self):
        filter_condition = FilterCondition(column="name", operator="LIKE", value="John%")
        assert filter_condition.to_sql() == "name LIKE 'John%'"

    def test_filter_with_in_operator(self):
        filter_condition = FilterCondition(column="status", operator="IN", value=["active", "pending"])
        assert filter_condition.to_sql() == "status IN ('active', 'pending')"

    def test_filter_with_is_null_operator(self):
        filter_condition = FilterCondition(column="deleted_at", operator="IS NULL")
        assert filter_condition.to_sql() == "deleted_at IS NULL"

    def test_filter_with_is_not_null_operator(self):
        filter_condition = FilterCondition(column="created_at", operator="IS NOT NULL")
        assert filter_condition.to_sql() == "created_at IS NOT NULL"

    def test_filter_with_boolean_value(self):
        filter_condition = FilterCondition(column="is_active", operator="=", value=True)
        assert filter_condition.to_sql() == "is_active = TRUE"

    def test_sql_injection_prevention_in_column_name(self):
        with pytest.raises(ValueError, match="Invalid column name"):
            FilterCondition(column="col1; DROP TABLE users; --", operator="=", value="test")

    def test_sql_injection_prevention_in_value(self):
        filter_condition = FilterCondition(column="name", operator="=", value="O'Brien")
        # Single quotes should be escaped by doubling them
        assert filter_condition.to_sql() == "name = 'O''Brien'"

    def test_sql_injection_prevention_complex_value(self):
        filter_condition = FilterCondition(column="comment", operator="=", value="test'; DROP TABLE users; --")
        assert filter_condition.to_sql() == "comment = 'test''; DROP TABLE users; --'"

    def test_invalid_column_name_with_special_chars(self):
        with pytest.raises(ValueError, match="Invalid column name"):
            FilterCondition(column="col1 OR 1=1", operator="=", value="test")

    def test_valid_column_name_with_dot(self):
        filter_condition = FilterCondition(column="users.age", operator=">", value=18)
        assert filter_condition.to_sql() == "users.age > 18"

    def test_null_operator_rejects_value(self):
        with pytest.raises(ValueError, match="should not have a value"):
            FilterCondition(column="deleted_at", operator="IS NULL", value="something")

    def test_comparison_operator_requires_value(self):
        with pytest.raises(ValueError, match="requires a value"):
            FilterCondition(column="age", operator=">", value=None)


class TestFilterGroup:
    def test_single_condition_no_logic_operator(self):
        group = FilterGroup(
            conditions=[
                FilterCondition(column="age", operator=">", value=18)
            ]
        )
        assert group.to_sql() == "age > 18"

    def test_logic_operator_required_for_multiple_conditions(self):
        with pytest.raises(ValueError, match="logic_operator is required"):
            group = FilterGroup(
                conditions=[
                    FilterCondition(column="age", operator=">", value=18),
                    FilterCondition(column="status", operator="=", value="active")
                ]
            )
            group.to_sql()

    def test_simple_or_group(self):
        group = FilterGroup(
            logic_operator="OR",
            conditions=[
                FilterCondition(column="column1", operator="=", value=7),
                FilterCondition(column="column1", operator="=", value=8)
            ]
        )
        assert group.to_sql() == "column1 = 7 OR column1 = 8"

    def test_simple_and_group(self):
        group = FilterGroup(
            logic_operator="AND",
            conditions=[
                FilterCondition(column="age", operator=">", value=18),
                FilterCondition(column="status", operator="=", value="active")
            ]
        )
        assert group.to_sql() == "age > 18 AND status = 'active'"

    def test_or_group_in_query(self):
        query = Query(
            filter=FilterGroup(
                logic_operator="OR",
                conditions=[
                    FilterCondition(column="column1", operator="=", value=7),
                    FilterCondition(column="column1", operator="=", value=8)
                ]
            )
        )
        assert query.to_sql("users") == "SELECT * FROM users WHERE column1 = 7 OR column1 = 8"

    def test_and_group_in_query(self):
        query = Query(
            filter=FilterGroup(
                logic_operator="AND",
                conditions=[
                    FilterCondition(column="age", operator=">", value=18),
                    FilterCondition(column="status", operator="=", value="active")
                ]
            )
        )
        assert query.to_sql("users") == "SELECT * FROM users WHERE age > 18 AND status = 'active'"

    def test_nested_groups_or_within_and(self):
        query = Query(
            filter=FilterGroup(
                logic_operator="AND",
                conditions=[
                    FilterCondition(column="column2", operator=">", value=10)
                ],
                groups=[
                    FilterGroup(
                        logic_operator="OR",
                        conditions=[
                            FilterCondition(column="column1", operator="=", value=7),
                            FilterCondition(column="column1", operator="=", value=8)
                        ]
                    )
                ]
            )
        )
        assert query.to_sql("users") == "SELECT * FROM users WHERE column2 > 10 AND (column1 = 7 OR column1 = 8)"

    def test_nested_groups_and_within_or(self):
        query = Query(
            filter=FilterGroup(
                logic_operator="OR",
                conditions=[
                    FilterCondition(column="is_admin", operator="=", value=True)
                ],
                groups=[
                    FilterGroup(
                        logic_operator="AND",
                        conditions=[
                            FilterCondition(column="age", operator=">", value=18),
                            FilterCondition(column="status", operator="=", value="active")
                        ]
                    )
                ]
            )
        )
        assert query.to_sql("users") == "SELECT * FROM users WHERE is_admin = TRUE OR (age > 18 AND status = 'active')"

    def test_complex_nested_groups(self):
        query = Query(
            filter=FilterGroup(
                logic_operator="AND",
                groups=[
                    FilterGroup(
                        logic_operator="OR",
                        conditions=[
                            FilterCondition(column="a", operator="=", value=1),
                            FilterCondition(column="a", operator="=", value=2)
                        ]
                    ),
                    FilterGroup(
                        logic_operator="OR",
                        conditions=[
                            FilterCondition(column="b", operator="=", value=3),
                            FilterCondition(column="b", operator="=", value=4)
                        ]
                    )
                ]
            )
        )
        assert query.to_sql("test") == "SELECT * FROM test WHERE (a = 1 OR a = 2) AND (b = 3 OR b = 4)"

    def test_or_with_in_operator(self):
        query = Query(
            filter=FilterGroup(
                logic_operator="OR",
                conditions=[
                    FilterCondition(column="status", operator="IN", value=["active", "pending"]),
                    FilterCondition(column="is_admin", operator="=", value=True)
                ]
            )
        )
        assert query.to_sql("users") == "SELECT * FROM users WHERE status IN ('active', 'pending') OR is_admin = TRUE"

    def test_aggregation_with_or(self):
        query = Query(
            select_columns=["category", "COUNT(*)"],
            group_by_columns=["category"],
            aggregation_conditions=FilterGroup(
                logic_operator="OR",
                conditions=[
                    FilterCondition(column="COUNT(*)", operator=">", value=100),
                    FilterCondition(column="SUM(price)", operator=">", value=1000)
                ]
            )
        )
        assert query.to_sql("products") == "SELECT category,COUNT(*) FROM products GROUP BY category HAVING COUNT(*) > 100 OR SUM(price) > 1000"
