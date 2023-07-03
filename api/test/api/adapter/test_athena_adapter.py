from unittest.mock import Mock, patch, call

import pandas as pd
import pytest
from awswrangler.exceptions import QueryFailed
from botocore.exceptions import ClientError

from api.adapter.athena_adapter import AthenaAdapter
from api.common.custom_exceptions import UserError, AWSServiceError, QueryExecutionError
from api.domain.sql_query import SQLQuery, SQLQueryOrderBy


class TestQuery:
    def setup_method(self):
        self.mock_athena_read_sql_query = Mock()
        self.athena_adapter = AthenaAdapter(
            database="my_database",
            athena_read_sql_query=self.mock_athena_read_sql_query,
            s3_output="out",
        )

    def test_returns_query_result_dataframe(self):
        query_result_df = pd.DataFrame(
            {"column1": [1, 2], "column2": ["item1", "item2"]}
        )

        self.mock_athena_read_sql_query.return_value = query_result_df

        result = self.athena_adapter.query("my", "table", 1, SQLQuery())

        self.mock_athena_read_sql_query.assert_called_once_with(
            sql="SELECT * FROM my_table_1",
            database="my_database",
            ctas_approach=False,
            workgroup="rapid_athena_workgroup",
            s3_output="out",
        )

        assert result.equals(query_result_df)

    def test_no_query_provided(self):
        self.athena_adapter.query("my", "table", 1, SQLQuery())

        self.mock_athena_read_sql_query.assert_called_once_with(
            sql="SELECT * FROM my_table_1",
            database="my_database",
            ctas_approach=False,
            workgroup="rapid_athena_workgroup",
            s3_output="out",
        )

    def test_query_provided(self):
        self.athena_adapter.query(
            "my",
            "table",
            1,
            SQLQuery(
                select_columns=["column1", "column2"],
                group_by_columns=["column2"],
                order_by_columns=[SQLQueryOrderBy(column="column1")],
                limit=2,
            ),
        )

        self.mock_athena_read_sql_query.assert_called_once_with(
            sql="SELECT column1,column2 FROM my_table_1 GROUP BY column2 ORDER BY column1 ASC LIMIT 2",
            database="my_database",
            ctas_approach=False,
            workgroup="rapid_athena_workgroup",
            s3_output="out",
        )

    @patch("api.adapter.athena_adapter.handle_version_retrieval")
    def test_version_not_provided(self, mock_handle_version_retrieval):
        mock_handle_version_retrieval.return_value = 4

        self.athena_adapter.query(
            "my",
            "table",
            None,
            SQLQuery(
                select_columns=["column1", "column2"],
                group_by_columns=["column2"],
                order_by_columns=[SQLQueryOrderBy(column="column1")],
                limit=2,
            ),
        )

        self.mock_athena_read_sql_query.assert_called_once_with(
            sql="SELECT column1,column2 FROM my_table_4 GROUP BY column2 ORDER BY column1 ASC LIMIT 2",
            database="my_database",
            ctas_approach=False,
            workgroup="rapid_athena_workgroup",
            s3_output="out",
        )

        mock_handle_version_retrieval.assert_called_once_with("my", "table", None)

    def test_query_fails(self):
        self.mock_athena_read_sql_query.side_effect = QueryFailed("Some error")

        with pytest.raises(UserError, match="Query failed to execute: Some error"):
            self.athena_adapter.query("my", "table", 1, SQLQuery())

    def test_query_fails_because_of_invalid_format(self):
        self.mock_athena_read_sql_query.side_effect = ClientError(
            error_response={
                "Error": {"Code": "InvalidRequestException"},
                "Message": "Failed to execute query: The error message",
            },
            operation_name="StartQueryExecution",
        )

        with pytest.raises(
            UserError, match="Failed to execute query: The error message"
        ):
            self.athena_adapter.query("my", "table", 10, SQLQuery())

    def test_query_fails_because_table_does_not_exist(self):
        self.mock_athena_read_sql_query.side_effect = QueryFailed(
            "SYNTAX_ERROR: line 1:15: Table awsdatacatalog.rapid_catalogue_db.my_table_1 does not exist"
        )

        expected_message = r"Query failed to execute: The table does not exist. The data could be currently processing or you might need to upload it."

        with pytest.raises(UserError, match=expected_message):
            self.athena_adapter.query("my", "table", 1, SQLQuery())


class TestLargeQuery:
    def setup_method(self):
        self.mock_athena_read_sql_query = Mock()
        self.mock_athena_client = Mock()
        self.athena_adapter = AthenaAdapter(
            database="my_database",
            athena_read_sql_query=self.mock_athena_read_sql_query,
            s3_output="out",
            athena_client=self.mock_athena_client,
        )

    def test_returns_query_execution_id(self):
        self.mock_athena_client.start_query_execution.return_value = {
            "QueryExecutionId": "111-222-333"
        }

        result = self.athena_adapter.query_async("my", "table", 1, SQLQuery())

        self.mock_athena_client.start_query_execution.assert_called_once_with(
            QueryString="SELECT * FROM my_table_1",
            WorkGroup="rapid_athena_workgroup",
            QueryExecutionContext={"Database": "my_database"},
            ResultConfiguration={"OutputLocation": "out"},
        )

        assert result == "111-222-333"

    def test_uses_the_query_provided(self):
        self.mock_athena_client.start_query_execution.return_value = {
            "QueryExecutionId": "111-222-333"
        }

        self.athena_adapter.query_async(
            "my",
            "table",
            1,
            SQLQuery(
                select_columns=["column1", "column2"],
                group_by_columns=["column2"],
                order_by_columns=[SQLQueryOrderBy(column="column1")],
                limit=2,
            ),
        )

        self.mock_athena_client.start_query_execution.assert_called_once_with(
            QueryString="SELECT column1,column2 FROM my_table_1 GROUP BY column2 ORDER BY column1 ASC LIMIT 2",
            WorkGroup="rapid_athena_workgroup",
            QueryExecutionContext={"Database": "my_database"},
            ResultConfiguration={"OutputLocation": "out"},
        )

    @patch("api.adapter.athena_adapter.handle_version_retrieval")
    def test_version_not_provided(self, mock_handle_version_retrieval):
        self.mock_athena_client.start_query_execution.return_value = {
            "QueryExecutionId": "111-222-333"
        }
        mock_handle_version_retrieval.return_value = 4

        self.athena_adapter.query_async(
            "my",
            "table",
            None,
            SQLQuery(
                select_columns=["column1", "column2"],
                group_by_columns=["column2"],
                order_by_columns=[SQLQueryOrderBy(column="column1")],
                limit=2,
            ),
        )

        mock_handle_version_retrieval.assert_called_once_with("my", "table", None)

        self.mock_athena_client.start_query_execution.assert_called_once_with(
            QueryString="SELECT column1,column2 FROM my_table_4 GROUP BY column2 ORDER BY column1 ASC LIMIT 2",
            WorkGroup="rapid_athena_workgroup",
            QueryExecutionContext={"Database": "my_database"},
            ResultConfiguration={"OutputLocation": "out"},
        )

    def test_query_fails(self):
        self.mock_athena_client.start_query_execution.side_effect = QueryFailed(
            "Some error"
        )

        with pytest.raises(UserError, match="Query failed to execute: Some error"):
            self.athena_adapter.query_async("my", "table", 1, SQLQuery())

    def test_query_fails_because_of_invalid_format(self):
        self.mock_athena_client.start_query_execution.side_effect = ClientError(
            error_response={
                "Error": {"Code": "InvalidRequestException"},
                "Message": "Failed to execute query: The error message",
            },
            operation_name="StartQueryExecution",
        )

        with pytest.raises(
            UserError, match="Failed to execute query: The error message"
        ):
            self.athena_adapter.query_async("my", "table", 10, SQLQuery())

    def test_query_fails_because_table_does_not_exist(self):
        self.mock_athena_client.start_query_execution.side_effect = QueryFailed(
            "SYNTAX_ERROR: line 1:15: Table awsdatacatalog.rapid_catalogue_db.my_table_1 does not exist"
        )

        expected_message = r"Query failed to execute: The table does not exist. The data could be currently processing or you might need to upload it."

        with pytest.raises(UserError, match=expected_message):
            self.athena_adapter.query_async("my", "table", 1, SQLQuery())


class TestWaitForQueryToComplete:
    def setup_method(self):
        self.mock_athena_read_sql_query = Mock()
        self.mock_athena_client = Mock()
        self.athena_adapter = AthenaAdapter(
            database="my_database",
            athena_read_sql_query=self.mock_athena_read_sql_query,
            s3_output="out",
            athena_client=self.mock_athena_client,
        )

    @patch("api.adapter.athena_adapter.sleep")
    def test_successful_when_query_succeeds_within_retires(self, _mock_sleep):
        self.mock_athena_client.get_query_execution.side_effect = [
            {"QueryExecution": {"Status": {"State": "QUEUED"}}},
            {"QueryExecution": {"Status": {"State": "RUNNING"}}},
            {"QueryExecution": {"Status": {"State": "SUCCEEDED"}}},
        ]

        expected_calls = [
            call(QueryExecutionId="the-execution-id"),
            call(QueryExecutionId="the-execution-id"),
            call(QueryExecutionId="the-execution-id"),
        ]

        self.athena_adapter.wait_for_query_to_complete("the-execution-id")

        self.mock_athena_client.get_query_execution.assert_has_calls(expected_calls)

    @patch("api.adapter.athena_adapter.sleep")
    def test_successful_when_query_succeeds_within_retires_after_at_least_once_client_error(
        self, _mock_sleep
    ):
        self.mock_athena_client.get_query_execution.side_effect = [
            {"QueryExecution": {"Status": {"State": "RUNNING"}}},
            ClientError(
                error_response={
                    "Error": {"Code": "ConnectionFailure"},
                },
                operation_name="GetQueryExecution",
            ),
            {"QueryExecution": {"Status": {"State": "SUCCEEDED"}}},
        ]

        expected_calls = [
            call(QueryExecutionId="the-execution-id"),
            call(QueryExecutionId="the-execution-id"),
            call(QueryExecutionId="the-execution-id"),
        ]

        self.athena_adapter.wait_for_query_to_complete("the-execution-id")

        self.mock_athena_client.get_query_execution.assert_has_calls(expected_calls)

    @patch("api.adapter.athena_adapter.sleep")
    def test_raises_error_when_retries_exhausted(self, _mock_sleep):
        self.mock_athena_client.get_query_execution.return_value = {
            "QueryExecution": {"Status": {"State": "RUNNING"}}
        }

        with pytest.raises(AWSServiceError, match="Query took too long to execute"):
            self.athena_adapter.wait_for_query_to_complete("the-execution-id")

        assert self.mock_athena_client.get_query_execution.call_count == 8

    @patch("api.adapter.athena_adapter.sleep")
    def test_raises_error_when_query_execution_has_failed(self, _mock_sleep):
        self.mock_athena_client.get_query_execution.return_value = {
            "QueryExecution": {
                "Status": {"State": "FAILED", "StateChangeReason": "Column not found"}
            }
        }

        with pytest.raises(
            QueryExecutionError, match="Query did not complete: Column not found"
        ):
            self.athena_adapter.wait_for_query_to_complete("the-execution-id")

    @patch("api.adapter.athena_adapter.sleep")
    def test_raises_error_when_query_execution_has_been_cancelled(self, _mock_sleep):
        self.mock_athena_client.get_query_execution.return_value = {
            "QueryExecution": {
                "Status": {
                    "State": "CANCELLED",
                    "StateChangeReason": "Insufficient memory",
                }
            }
        }

        with pytest.raises(
            QueryExecutionError, match="Query did not complete: Insufficient memory"
        ):
            self.athena_adapter.wait_for_query_to_complete("the-execution-id")
