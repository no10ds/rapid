import tempfile
import os
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from api.application.services.schema_infer_service import SchemaInferService
from api.common.custom_exceptions import UserError
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata


class TestSchemaInfer:
    def setup_method(self):
        self.infer_schema_service = SchemaInferService()

    def test_infer_schema(self):
        expected_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="mydomain",
                dataset="mydataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="change_me", email="change_me@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                    format=None,
                ),
                "colname2": Column(
                    partition_index=None,
                    dtype="int",
                    nullable=True,
                    format=None,
                ),
                "col_name_3": Column(
                    partition_index=None,
                    dtype="int",
                    nullable=True,
                    format=None,
                ),
                "colname_4": Column(
                    partition_index=None,
                    dtype="boolean",
                    nullable=True,
                    format=None,
                ),
            },
        ).dict(exclude={"metadata": {"version"}})
        file_content = b"colname1,colname2,Col name 3,Col/name 4! \nsomething,123,1,True\notherthing,123,3,False\n\n"
        temp_out_path = tempfile.mkstemp(suffix=".csv")[1]
        path = Path(temp_out_path)
        with open(path, "wb") as file:
            file.write(file_content)

        actual_schema = self.infer_schema_service.infer_schema(
            "raw", "mydomain", "mydataset", "PUBLIC", path
        )
        assert actual_schema == expected_schema
        os.remove(temp_out_path)

    def test_infer_schema_with_date(self):
        expected_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="mydomain",
                dataset="mydataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="change_me", email="change_me@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=None,
                    dtype="object",
                    nullable=True,
                    format=None,
                ),
                "colname2": Column(
                    partition_index=None,
                    dtype="datetime64[ns]",
                    nullable=True,
                    format="%Y-%m-%d",
                ),
            },
        ).dict(exclude={"metadata": {"version"}})

        df = pd.DataFrame(data={"colname1": ["something"], "colname2": ["2021-01-01"]})
        df["colname2"] = pd.to_datetime(df["colname2"])
        temp_out_path = tempfile.mkstemp(suffix=".parquet")[1]
        path = Path(temp_out_path)
        pq.write_table(pa.Table.from_pandas(df), path)

        actual_schema = self.infer_schema_service.infer_schema(
            "raw", "mydomain", "mydataset", "PUBLIC", path
        )
        assert actual_schema == expected_schema
        os.remove(temp_out_path)

    @patch("api.application.services.schema_infer_service.construct_chunked_dataframe")
    def test_raises_error_when_parsing_provided_file_fails(
        self, mock_construct_chunked_dataframe
    ):
        mock_construct_chunked_dataframe.side_effect = ValueError("Some message")

        with pytest.raises(UserError):
            self.infer_schema_service.infer_schema(
                "raw", "mydomain", "mydataset", "PUBLIC", Path("xxx-yyy.csv")
            )

    def test_raises_error_when_some_rows_contain_too_many_values(self):
        file_content = (
            b"colname1,colname2\n" b"value1,value2\n" b"value1,value2,EXTRA_VALUE\n"
        )
        temp_out_path = tempfile.mkstemp(suffix=".csv")[1]
        path = Path(temp_out_path)
        with open(path, "wb") as file:
            file.write(file_content)

        with pytest.raises(UserError):
            self.infer_schema_service.infer_schema(
                "raw", "mydomain", "mydataset", "PUBLIC", path
            )
        os.remove(temp_out_path)
