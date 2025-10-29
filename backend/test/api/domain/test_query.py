import pytest

from rapid.items.query import Query, QueryOrderBy


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
        sql_query = Query(filter="col1 > 16")
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

    @pytest.mark.parametrize(
        "select_columns,filter,group_by_columns,aggregation_conditions,order_by_columns,limit,expected_sql",
        [
            (
                ["col1", "col2", "col3"],  # noqa: E126
                "col2 = 123",
                ["col4", "col5"],
                "col4 in ('some value', 'another value')",
                [
                    QueryOrderBy(column="col1"),
                    QueryOrderBy(column="col2", direction="DESC"),
                ],
                10,
                "SELECT col1,col2,col3 FROM test_domain WHERE col2 = 123 GROUP BY col4,col5 HAVING col4 in ('some value', 'another value') ORDER BY col1 ASC,col2 DESC LIMIT 10",
            ),
            (
                [],  # noqa: E126
                "col2 = 123",
                ["col4", "col5"],
                None,
                [],
                10,
                "SELECT * FROM test_domain WHERE col2 = 123 GROUP BY col4,col5 LIMIT 10",
            ),
            (
                [],  # noqa: E126
                "col2 = 123",
                ["col4", "col5"],
                "",
                [],
                10,
                "SELECT * FROM test_domain WHERE col2 = 123 GROUP BY col4,col5 LIMIT 10",
            ),
            (
                ["avg(col2)"],  # noqa: E126
                "col2 >= 100",
                ["col4", "col5"],
                None,
                [],
                50,
                "SELECT avg(col2) FROM test_domain WHERE col2 >= 100 GROUP BY col4,col5 LIMIT 50",
            ),
            (
                ["avg(col2)"],  # noqa: E126
                "col2 >= 100",
                ["col4", "col5"],
                "",
                [],
                50,
                "SELECT avg(col2) FROM test_domain WHERE col2 >= 100 GROUP BY col4,col5 LIMIT 50",
            ),
            (
                ["col1", "avg(col2)", ""],  # noqa: E126
                None,
                ["col1"],
                "",
                [],
                675,
                "SELECT col1,avg(col2) FROM test_domain GROUP BY col1 LIMIT 675",
            ),
            (
                ["col1", "avg(col2)", ""],  # noqa: E126
                "",
                ["col1"],
                "",
                [],
                None,
                "SELECT col1,avg(col2) FROM test_domain GROUP BY col1",
            ),
        ],
    )
    def test_query_operation_combinations(
        self,
        select_columns,
        filter,
        group_by_columns,
        aggregation_conditions,
        order_by_columns,
        limit,
        expected_sql,
    ):
        sql_query = Query(
            select_columns=select_columns,
            filter=filter,
            group_by_columns=group_by_columns,
            aggregation_conditions=aggregation_conditions,
            order_by_columns=order_by_columns,
            limit=limit,
        )

        assert sql_query.to_sql("test_domain") == expected_sql
