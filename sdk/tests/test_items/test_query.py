from rapid.items.query import SQLQueryOrderBy, Query, SortDirection


class TestSQLQueryOrderBy:
    def test_create_sql_query_order_by(self):
        sort_direction = SQLQueryOrderBy(
            column="column_a", sort_direction=SortDirection.ASC
        )
        assert sort_direction.column == "column_a"


class TestQuery:
    def test_create_query_from_dict(self):
        _query = {"select_columns": ["column_a"], "limit": "1"}
        query = Query(**_query)

        assert query.select_columns == ["column_a"]
        assert query.limit == "1"

    def test_create_query_returns_dictionary(self):
        _query = {"select_columns": ["column_a"], "limit": "1"}
        query = Query(**_query)

        assert query.dict(exclude_none=True) == _query

    def test_create_empty_query_returns_dictionary(self):
        query = Query()
        assert query.dict(exclude_none=True) == {}
