import re
from typing import List

import numpy as np
import pandas as pd
import pytest

from api.application.services.dataset_validation import (
    build_validated_dataframe,
    convert_date_columns,
    remove_empty_rows,
    clean_column_headers,
    dataset_has_correct_columns,
    dataset_has_no_illegal_characters_in_partition_columns,
    dataset_has_rows,
    validate_with_pandera,
)
from api.common.custom_exceptions import (
    DatasetValidationError,
    UserError,
    UnprocessableDatasetError,
)
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, SchemaMetadata


class TestDatasetValidation:
    def setup_method(self):
        self.schema_metadata = SchemaMetadata(
            layer="raw",
            domain="test_domain",
            dataset="test_dataset",
            sensitivity="PUBLIC",
            owners=[Owner(name="owner", email="owner@email.com")],
        )

        self.valid_schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "colname1": Column(
                    name="colname1",
                    partition_index=0,
                    dtype="int",
                    nullable=True,
                ),
                "colname2": Column(
                    name="colname2",
                    partition_index=None,
                    dtype="string",
                    nullable=False,
                ),
                "colname3": Column(
                    name="colname3",
                    partition_index=None,
                    dtype="boolean",
                    nullable=True,
                ),
            },
        )

    def test_fully_valid_dataset(self):
        full_valid_schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "colname1": Column(
                    name="colname1",
                    partition_index=0,
                    dtype="int64",
                    nullable=True,
                ),
                "colname2": Column(
                    name="colname2",
                    partition_index=None,
                    dtype="string[python]",
                    nullable=False,
                ),
                "colname3": Column(
                    name="colname3",
                    partition_index=None,
                    dtype="boolean",
                    nullable=True,
                ),
                "colname4": Column(
                    name="colname4",
                    partition_index=None,
                    dtype="date",
                    format="%d/%m/%Y",
                    nullable=True,
                ),
            },
        )

        dataframe = pd.DataFrame(
            {
                "colname1": [1234, 4567],
                "colname2": ["Carlos", "Ada"],
                "colname3": [True, pd.NA],
                "Col-Name!4": ["12/05/2022", "15/11/2022"],
            }
        )

        expected = pd.DataFrame(
            {
                "colname1": [1234, 4567],
                "colname2": ["Carlos", "Ada"],
                "colname3": [True, pd.NA],
                "colname4": ["2022-05-12", "2022-11-15"],
            }
        )
        expected["colname1"] = expected["colname1"].astype(dtype=pd.Int32Dtype())
        expected["colname3"] = expected["colname3"].astype(dtype=pd.BooleanDtype())
        expected["colname4"] = expected["colname4"].astype(dtype="datetime64[ns]")

        validated_dataframe = build_validated_dataframe(full_valid_schema, dataframe)

        assert validated_dataframe.to_dict() == expected.to_dict()

    def test_invalid_column_names(self):
        dataframe = pd.DataFrame(
            {
                "wrongcolumn": [1234, 4567],
                "colname2": ["Carlos", "Ada"],
                "colname3": [pd.NA, pd.NA],
            }
        )

        try:
            build_validated_dataframe(self.valid_schema, dataframe)
        except UnprocessableDatasetError as error:
            assert error.message == [
                "Expected columns: ['colname1', 'colname2', 'colname3'], received: ['wrongcolumn', 'colname2', 'colname3']",
            ]

    def test_no_rows(self):
        dataframe = pd.DataFrame(
            {
                "wrongcolumn": [],
                "colname2": [],
                "colname3": [],
            }
        )

        try:
            build_validated_dataframe(self.valid_schema, dataframe)
        except UnprocessableDatasetError as error:
            assert error.message == [
                "Dataset has no rows, it cannot be processed",
            ]

    def test_invalid_when_partition_column_with_illegal_characters(self):
        valid_schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "colname1": Column(
                    name="colname1",
                    partition_index=0,
                    dtype="string",
                    nullable=True,
                ),
                "colname2": Column(
                    name="colname2",
                    partition_index=1,
                    dtype="string",
                    nullable=False,
                ),
            },
        )

        dataframe = pd.DataFrame(
            {"colname1": [2021, 2020], "colname2": ["01/02/2021", "01/02/2021"]}
        )

        with pytest.raises(DatasetValidationError):
            build_validated_dataframe(valid_schema, dataframe)

    def test_valid_when_date_partition_column_with_illegal_slash_character(self):
        valid_schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "colname1": Column(
                    name="colname1",
                    partition_index=0,
                    dtype="date",
                    format="%d/%m/%Y",
                    nullable=True,
                ),
            },
        )

        dataframe = pd.DataFrame({"colname1": ["01/02/2021", "01/02/2021"]})

        try:
            build_validated_dataframe(valid_schema, dataframe)
        except DatasetValidationError:
            pytest.fail("An unexpected InvalidDatasetError was thrown")

    def test_invalid_when_strings_in_numeric_column(self):
        dataframe = pd.DataFrame(
            {
                "colname1": [23, 34],
                "colname2": ["name1", "name2"],
                "colname3": ["name3", "name4"],
            }
        )

        with pytest.raises(DatasetValidationError):
            build_validated_dataframe(self.valid_schema, dataframe)

    def test_invalid_when_entire_column_is_different_to_expected_type(self):
        dataframe = pd.DataFrame(
            {"colname1": [1, 2], "colname2": [67.8, 98.2], "colname3": [True, False]}
        )

        with pytest.raises(
            DatasetValidationError,
            match=r"Column \[colname2\] has an incorrect data type. Expected string, received double",
            # noqa: E501, W605
        ):
            build_validated_dataframe(self.valid_schema, dataframe)

    @pytest.mark.parametrize(
        "dataframe",
        [
            pd.DataFrame(
                {"col1": [45, pd.NA], "col2": [56.2, 23.1], "col3": ["hello", "there"]}
            ),
            pd.DataFrame(
                {"col1": [45, 56], "col2": [56.2, pd.NA], "col3": ["hello", "there"]}
            ),
            pd.DataFrame(
                {"col1": [45, 56], "col2": [56.2, 23.1], "col3": ["hello", pd.NA]}
            ),
        ],
    )
    def test_checks_for_unacceptable_null_values(self, dataframe: pd.DataFrame):
        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "col1": Column(
                    name="col1",
                    partition_index=None,
                    dtype="int",
                    nullable=False,
                ),
                "col2": Column(
                    name="col2",
                    partition_index=None,
                    dtype="double",
                    nullable=False,
                ),
                "col3": Column(
                    name="col3",
                    partition_index=None,
                    dtype="string",
                    nullable=False,
                ),
            },
        )

        with pytest.raises(DatasetValidationError):
            build_validated_dataframe(schema, dataframe)

    def test_validates_correct_data_types(self):
        dataframe = pd.DataFrame(
            {"col1": [1234, 4567], "col2": [4.53, 9.33], "col3": ["Carlos", "Ada"]}
        )

        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "col1": Column(
                    name="col1",
                    partition_index=None,
                    dtype="int",
                    nullable=True,
                ),
                "col2": Column(
                    name="col2",
                    partition_index=None,
                    dtype="double",
                    nullable=True,
                ),
                "col3": Column(
                    name="col3",
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        try:
            build_validated_dataframe(schema, dataframe)
        except DatasetValidationError:
            pytest.fail("Unexpected InvalidDatasetError was thrown")

    def test_validates_custom_data_types_as_object_type(self):
        dataframe = pd.DataFrame(
            {
                "col1": ["12/04/2016", "13/04/2016"],
                "col2": [4.53, 9.33],
                "col3": ["Carlos", "Ada"],
            }
        )

        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "col1": Column(
                    name="col1",
                    partition_index=None,
                    dtype="date",
                    format="%d/%m/%Y",
                    nullable=True,
                ),
                "col2": Column(
                    name="col2",
                    partition_index=None,
                    dtype="double",
                    nullable=True,
                ),
                "col3": Column(
                    name="col3",
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        try:
            build_validated_dataframe(schema, dataframe)
        except DatasetValidationError:
            pytest.fail("Unexpected InvalidDatasetError was thrown")

    def test_validates_dataset_with_empty_rows(self):
        dataframe = pd.DataFrame(
            {
                "col1": ["12/04/2016", "13/04/2016", pd.NA, pd.NA],
                "col2": [4.53, 9.33, pd.NA, pd.NA],
                "col3": ["Carlos", "Ada", pd.NA, pd.NA],
            }
        )

        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "col1": Column(
                    name="col1",
                    partition_index=None,
                    dtype="date",
                    format="%d/%m/%Y",
                    nullable=True,
                ),
                "col2": Column(
                    name="col2",
                    partition_index=None,
                    dtype="double",
                    nullable=True,
                ),
                "col3": Column(
                    name="col3",
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        try:
            build_validated_dataframe(schema, dataframe)
        except DatasetValidationError:
            pytest.fail("Unexpected InvalidDatasetError was thrown")

    @pytest.mark.parametrize(
        "dataframe_columns,schema_columns",
        [
            (["colname1", "colname2", "colname3"], ["colname1", "colname2"]),
            (["colname1", "colname2"], ["colname1", "colname2", "colname3"]),
            (
                ["colname1", "colname2", "anothercolname"],
                ["colname1", "colname2", "colname3"],
            ),
            (
                ["colname1", "colname2", "colname3"],
                ["colname1", "colname2", "anothercolname"],
            ),
        ],
    )
    def test_return_error_message_when_columns_do_not_match(
        self, dataframe_columns: list[str], schema_columns: list[str]
    ):
        df = pd.DataFrame(columns=dataframe_columns)

        columns = {
            schema_column: Column(
                name=schema_column,
                partition_index=None,
                dtype="string",
                nullable=True,
            )
            for schema_column in schema_columns
        }

        schema = Schema(
            metadata=self.schema_metadata,
            columns=columns,
        )

        with pytest.raises(
            UnprocessableDatasetError,
            match=re.escape(
                f"Expected columns: {schema_columns}, received: {dataframe_columns}"
            ),
        ):
            dataset_has_correct_columns(df, schema)

    def test_return_error_message_when_dataset_has_no_rows(self):
        df = pd.DataFrame(columns=["a", "b"])

        with pytest.raises(
            UnprocessableDatasetError,
            match=re.escape("Dataset has no rows, it cannot be processed"),
        ):
            dataset_has_rows(df)

    def test_return_error_message_when_not_accepted_null_values(self):
        df = pd.DataFrame(
            {"col1": ["a", "b", None], "col2": ["d", "e", None], "col3": [1, 5, None]}
        )
        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "col1": Column(
                    name="col1",
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
                "col2": Column(
                    name="col2",
                    partition_index=None,
                    dtype="string",
                    nullable=False,
                ),
                "col3": Column(
                    name="col3",
                    partition_index=None,
                    dtype="int",
                    nullable=False,
                ),
            },
        )

        try:
            validate_with_pandera(df, schema)
        except DatasetValidationError as error:
            assert error.message == [
                "Column [col2] does not allow null values",
                "Column [col3] does not allow null values",
            ]

    def test_return_error_message_when_not_accepted_unique_values(self):
        df = pd.DataFrame(
            {
                "col1": [None, "a", None, "a"],
                "col2": [None, "b", None, "a"],
                "col3": ["c", "b", None, "b"],
            }
        )
        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "col1": Column(
                    name="col1",
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                    unique=True,
                ),
                "col2": Column(
                    name="col2",
                    partition_index=None,
                    dtype="string",
                    nullable=False,
                    unique=True,
                ),
                "col3": Column(
                    name="col3",
                    partition_index=None,
                    dtype="string",
                    nullable=False,
                    unique=True,
                ),
            },
        )

        data_frame, error_list = validate_with_pandera(df, schema)
        assert error_list == [
            "Column [col1] must have unique values",
            "Column [col3] must have unique values",
        ]

    def test_return_error_message_when_not_correct_datatypes(self):
        df = pd.DataFrame(
            {
                "col1": ["a", "b", 123],
                "col2": [True, False, 12],
                "col3": [1, 5, True],
                "col4": [1.5, 2.5, "A"],
                "col5": ["2021-01-01", "2021-05-01", 1000],
                "col6": [None, None, None],
                "col7": [np.nan, np.nan, np.nan],
            }
        )
        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "col1": Column(
                    name="col1",
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
                "col2": Column(
                    name="col2",
                    partition_index=None,
                    dtype="boolean",
                    nullable=False,
                ),
                "col3": Column(
                    name="col3",
                    partition_index=None,
                    dtype="int",
                    nullable=False,
                ),
                "col4": Column(
                    name="col4",
                    partition_index=None,
                    dtype="int64",
                    nullable=False,
                ),
                "col5": Column(
                    name="col5",
                    partition_index=None,
                    dtype="date",
                    nullable=False,
                ),
                "col6": Column(
                    name="col6",
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
                "col7": Column(
                    name="col7",
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        data_frame, error_list = validate_with_pandera(df, schema)
        assert error_list == [
            "Column [col2] has an incorrect data type. Expected boolean, received string",
            "Column [col3] has an incorrect data type. Expected int, received string",
            "Column [col4] has an incorrect data type. Expected int64, received string",
        ]

    def test_return_error_message_when_dataset_has_illegal_chars_in_partition_columns(
        self,
    ):
        df = pd.DataFrame(
            {
                "col1": ["a", "b", "c/d"],
                "col2": ["1", "2", "4/5"],
                "col3": ["d", "e", "f"],
                "col4": ["2021-01-01", "2021-05-01", "20/05/2020"],
                "col5": [1, 2, 3],
            }
        )
        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "col1": Column(
                    name="col1",
                    partition_index=0,
                    dtype="string",
                    nullable=True,
                ),
                "col2": Column(
                    name="col2",
                    partition_index=1,
                    dtype="string",
                    nullable=False,
                ),
                "col3": Column(
                    name="col3",
                    partition_index=2,
                    dtype="string",
                    nullable=False,
                ),
                "col4": Column(
                    name="col4",
                    partition_index=3,
                    dtype="date",
                    nullable=False,
                ),
                "col5": Column(
                    name="col5",
                    partition_index=4,
                    dtype="int",
                    nullable=False,
                ),
            },
        )

        try:
            dataset_has_no_illegal_characters_in_partition_columns(df, schema)
        except DatasetValidationError as error:
            assert error.message == [
                "Partition column [col1] has values with illegal characters '/'",
                "Partition column [col2] has values with illegal characters '/'",
            ]

    def test_return_list_of_validation_error_messages_when_multiple_validation_steps_fail(
        self,
    ):
        df = pd.DataFrame(
            {
                "col1": ["a", "b", "c/d"],  # Illegal character in partition column
                "col2": ["1", "2/3", "3"],  # Illegal character in partition column
                "col3": ["d", "e", None],  # Contains null values
                "col4": ["2021-05-02", "2021-05-01", "20/05"],  # Incorrect date format
                "col5": ["data", "is", "strings"],  # Incorrect data type
            }
        )
        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "col1": Column(
                    name="col1",
                    partition_index=0,
                    dtype="string",
                    nullable=True,
                ),
                "col2": Column(
                    name="col2",
                    partition_index=1,
                    dtype="string",
                    nullable=False,
                ),
                "col3": Column(
                    name="col3",
                    partition_index=None,
                    dtype="string",
                    nullable=False,
                ),
                "col4": Column(
                    name="col4",
                    partition_index=None,
                    dtype="date",
                    nullable=False,
                ),
                "col5": Column(
                    name="col5",
                    partition_index=None,
                    dtype="int",
                    nullable=False,
                ),
            },
        )

        try:
            build_validated_dataframe(schema, df)
        except DatasetValidationError as error:
            assert error.message == [
                "Column [col4] does not match specified date format in at least one row",
                "Column [col3] does not allow null values",
                "Column [col5] has an incorrect data type. Expected int, received string",
                "Partition column [col1] has values with illegal characters '/'",
                "Partition column [col2] has values with illegal characters '/'",
            ]


class TestDatasetTransformation:
    def setup_method(self):
        self.schema_metadata = SchemaMetadata(
            layer="raw",
            domain="test_domain",
            dataset="test_dataset",
            sensitivity="PUBLIC",
            owners=[Owner(name="owner", email="owner@email.com")],
        )

    @pytest.mark.parametrize(
        "date_format,date_column_data,expected_date_column_data",
        [
            (
                "%Y-%m-%d",  # noqa: E126
                ["2008-01-30", "2008-01-31", "2008-02-01", "2008-02-02"],
                ["2008-01-30", "2008-01-31", "2008-02-01", "2008-02-02"],
            ),
            (
                "%d/%m/%Y",  # noqa: E126
                ["30/01/2008", "31/01/2008", "01/02/2008", "02/02/2008"],
                ["2008-01-30", "2008-01-31", "2008-02-01", "2008-02-02"],
            ),
            (
                "%m-%d-%Y",  # noqa: E126
                ["05-15-2008", "12-13-2008", "07-09-2008", "03-17-2008"],
                ["2008-05-15", "2008-12-13", "2008-07-09", "2008-03-17"],
            ),
            (
                "%Y/%d/%m",  # noqa: E126
                ["2008/15/05", "2008/13/12", "2008/09/07", "2008/17/03"],
                ["2008-05-15", "2008-12-13", "2008-07-09", "2008-03-17"],
            ),
            (
                "%m-%Y",  # noqa: E126
                ["05-2008", "12-2008", "07-2008", "03-2008"],
                ["2008-05-01", "2008-12-01", "2008-07-01", "2008-03-01"],
            ),
        ],
    )
    def test_convert_date_columns(
        self,
        date_format: str,
        date_column_data: List[str],
        expected_date_column_data: List[str],
    ):
        data = pd.DataFrame({"date": date_column_data, "value": [1, 5, 4, 8]})

        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "date": Column(
                    name="date",
                    partition_index=None,
                    dtype="date",
                    format=date_format,
                    nullable=False,
                )
            },
        )

        transformed_df, _ = convert_date_columns(data, schema)

        expected_date_column = pd.Series(
            expected_date_column_data,
            dtype="datetime64[ns]",
        )

        assert transformed_df["date"].equals(expected_date_column)

    def test_converts_multiple_date_columns(self):
        data = pd.DataFrame(
            {
                "date1": ["30/01/2008", "31/01/2008", "01/02/2008", "02/02/2008"],
                "date2": ["05-15-2008", "12-13-2008", "07-09-2008", "03-17-2008"],
                "value": [1, 5, 4, 8],
            }
        )
        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "date1": Column(
                    name="date1",
                    partition_index=None,
                    dtype="date",
                    format="%d/%m/%Y",
                    nullable=False,
                ),
                "date2": Column(
                    name="date2",
                    partition_index=None,
                    dtype="date",
                    format="%m-%d-%Y",
                    nullable=False,
                ),
            },
        )
        transformed_df, _ = convert_date_columns(data, schema)

        expected_date_column_1 = pd.Series(
            ["2008-01-30", "2008-01-31", "2008-02-01", "2008-02-02"],
            dtype="datetime64[ns]",
        )
        expected_date_column_2 = pd.Series(
            ["2008-05-15", "2008-12-13", "2008-07-09", "2008-03-17"],
            dtype="datetime64[ns]",
        )

        assert transformed_df["date1"].equals(expected_date_column_1)
        assert transformed_df["date2"].equals(expected_date_column_2)

    def test_raises_error_if_provided_date_is_not_valid(self):
        data = pd.DataFrame(
            {
                "date1": ["1545-73-98", "1545-73-99"],
                "date2": ["16-05-1950", "bbbb"],
                "value": [1, 5],
            }
        )
        schema = Schema(
            metadata=self.schema_metadata,
            columns={
                "date1": Column(
                    name="date1",
                    partition_index=None,
                    dtype="date",
                    format="%Y-%m-%d",
                    nullable=False,
                ),
                "date2": Column(
                    name="date2",
                    partition_index=None,
                    dtype="date",
                    format="%d-%m-%Y",
                    nullable=False,
                ),
                "value": Column(
                    name="value",
                    partition_index=None,
                    dtype="int",
                    nullable=False,
                ),
            },
        )

        try:
            convert_date_columns(data, schema)
        except UserError as error:
            assert error.message == [
                "Column [date1] does not match specified date format in at least one row",
                "Column [date2] does not match specified date format in at least one row",
            ]

    def test_removes_null_rows(self):
        data = pd.DataFrame(
            {"col1": [1, 2, 3, pd.NA, pd.NA], "col2": ["a", "b", "c", pd.NA, pd.NA]}
        )

        data["col1"] = data["col1"].astype(dtype=pd.Int32Dtype())

        transformed_df, _ = remove_empty_rows(data)

        expected_column_1 = pd.Series([1, 2, 3])
        expected_column_2 = pd.Series(["a", "b", "c"])

        expected_column_1 = expected_column_1.astype(dtype=pd.Int32Dtype())

        assert transformed_df["col1"].equals(expected_column_1)
        assert transformed_df["col2"].equals(expected_column_2)

    def test_cleans_up_column_headings(self):
        incorrect_given_column_name = " col 2"
        expected_column_name = "col_2"

        data = pd.DataFrame(
            {
                incorrect_given_column_name: [1],
            }
        )

        transformed_df, _ = clean_column_headers(data)

        assert transformed_df.columns[0] == expected_column_name