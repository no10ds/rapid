import re
from time import sleep
from typing import Callable, Dict

import awswrangler as wr
import boto3
from awswrangler.exceptions import QueryFailed
from botocore.exceptions import ClientError
from pandas import DataFrame

from api.common.config.aws import (
    ATHENA_DATABASE,
    ATHENA_WORKGROUP,
    OUTPUT_QUERY_BUCKET,
    AWS_REGION,
)
from api.common.custom_exceptions import AWSServiceError, QueryExecutionError, UserError
from api.common.logger import AppLogger
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.sql_query import SQLQuery


class AthenaAdapter:
    def __init__(
        self,
        database: str = ATHENA_DATABASE,
        s3_output: str = OUTPUT_QUERY_BUCKET,
        workgroup: str = ATHENA_WORKGROUP,
        athena_read_sql_query: Callable[
            [str, str], DataFrame
        ] = wr.athena.read_sql_query,
        athena_client=boto3.client("athena", region_name=AWS_REGION),
    ):
        self.__database = database
        self.__workgroup = workgroup
        self.__s3_output = s3_output
        self.__athena_read_sql_query = athena_read_sql_query
        self.__athena_client = athena_client

    def query(
        self,
        dataset: DatasetMetadata,
        query: SQLQuery,
    ) -> DataFrame:
        table_name = dataset.glue_table_name()
        return self.query_sql(query.to_sql(table_name))

    def query_sql(self, query_string: str) -> DataFrame:
        try:
            return self.__athena_read_sql_query(
                sql=query_string,
                database=self.__database,
                ctas_approach=False,
                workgroup=self.__workgroup,
                s3_output=self.__s3_output,
            )
        except QueryFailed as error:
            self._handle_query_error(error)
        except ClientError as error:
            self._handle_client_error(error)

    def query_async(self, dataset: DatasetMetadata, query: SQLQuery) -> Dict[str, str]:
        """
        :return: QueryExecutionId from Athena
        """
        table_name = dataset.glue_table_name()
        return self.query_sql_async(query.to_sql(table_name))

    def query_sql_async(self, query_string: str) -> Dict[str, str]:
        """
        :return: QueryExecutionId from Athena
        """
        try:
            return self.__athena_client.start_query_execution(
                QueryString=query_string,
                WorkGroup=self.__workgroup,
                QueryExecutionContext={"Database": self.__database},
                ResultConfiguration={"OutputLocation": self.__s3_output},
            )["QueryExecutionId"]
        except QueryFailed as error:
            self._handle_query_error(error)
        except ClientError as error:
            self._handle_client_error(error)

    def wait_for_query_to_complete(self, query_execution_id: str) -> None:
        retry_interval_seconds = 30
        num_retries = 8

        while num_retries > 0:
            try:
                response = self.__athena_client.get_query_execution(
                    QueryExecutionId=query_execution_id
                )
                state = (
                    response.get("QueryExecution", {})
                    .get("Status", {})
                    .get("State", None)
                )

                if state == "SUCCEEDED":
                    return
                elif state in ["FAILED", "CANCELLED"]:
                    reason = (
                        response.get("QueryExecution", {})
                        .get("Status", {})
                        .get("StateChangeReason", "Unknown error occurred")
                    )
                    AppLogger.error(f"Query {query_execution_id} failed to complete")
                    raise QueryExecutionError(f"Query did not complete: {reason}")
            except ClientError:
                pass
            num_retries -= 1
            sleep(retry_interval_seconds)
            retry_interval_seconds *= 2

        AppLogger.error(
            f"Retries exhausted when waiting for query with ID {query_execution_id} to complete"
        )
        raise AWSServiceError("Query took too long to execute")

    def _handle_client_error(self, error):
        if error.response["Error"]["Code"] == "InvalidRequestException":
            raise UserError(f'Failed to execute query: {error.response["Message"]}')
        raise AWSServiceError(f'Failed to execute query: {error.response["Message"]}')

    def _handle_query_error(self, error):
        if re.match(".+ Table .+ does not exist", error.args[0]):
            raise UserError(
                "Query failed to execute: The table does not exist. The data could be currently processing or you might need to upload it."
            )
        raise UserError(f"Query failed to execute: {error.args[0]}")
