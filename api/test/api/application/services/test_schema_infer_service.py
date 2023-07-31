from unittest.mock import patch

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
            columns=[
                Column(
                    name="colname1",
                    partition_index=None,
                    data_type="string",
                    allow_null=True,
                    format=None,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="integer",
                    allow_null=True,
                    format=None,
                ),
                Column(
                    name="col_name_3",
                    partition_index=None,
                    data_type="integer",
                    allow_null=True,
                    format=None,
                ),
                Column(
                    name="colname_4",
                    partition_index=None,
                    data_type="boolean",
                    allow_null=True,
                    format=None,
                ),
            ],
        ).dict(exclude={"metadata": {"version"}})
        file_content = b"colname1,colname2,Col name 3,Col/name 4! \nsomething,123,1,True\notherthing,123,3,False\n\n"

        actual_schema = self.infer_schema_service.infer_schema(
            "raw", "mydomain", "mydataset", "PUBLIC", file_content
        )
        assert actual_schema == expected_schema

    @patch("api.application.services.schema_infer_service.pd")
    def test_raises_error_when_parsing_provided_file_fails(self, mock_pd):
        file_content = b""

        mock_pd.read_csv.side_effect = ValueError("Some message")

        with pytest.raises(UserError):
            self.infer_schema_service.infer_schema(
                "raw", "mydomain", "mydataset", "PUBLIC", file_content
            )

    def test_raises_error_when_some_rows_contain_too_many_values(self):
        file_content = (
            b"colname1,colname2\n" b"value1,value2\n" b"value1,value2,EXTRA_VALUE\n"
        )

        with pytest.raises(UserError):
            self.infer_schema_service.infer_schema(
                "raw", "mydomain", "mydataset", "PUBLIC", file_content
            )
