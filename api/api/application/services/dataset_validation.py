from typing import Tuple

import pandas as pd
from pandas import Timestamp

from api.common.custom_exceptions import (
    DatasetValidationError,
    UnprocessableDatasetError,
)
from api.common.value_transformers import clean_column_name
from api.domain.data_types import DataTypes
from api.domain.schema import Schema
from api.domain.validation_context import ValidationContext


def build_validated_dataframe(schema: Schema, dataframe: pd.DataFrame) -> pd.DataFrame:
    return transform_and_validate(schema, dataframe)


def transform_and_validate(schema: Schema, data: pd.DataFrame) -> pd.DataFrame:
    validation_context = (
        ValidationContext(data)
        .pipe(remove_empty_rows)
        .pipe(clean_column_headers)
        .pipe(dataset_has_correct_columns, schema)
        .pipe(set_data_types, schema)
        .pipe(convert_dates_to_ymd, schema)
        .pipe(dataset_has_acceptable_null_values, schema)
        .pipe(dataset_has_correct_data_types, schema)
        .pipe(dataset_has_no_illegal_characters_in_partition_columns, schema)
    )

    if validation_context.has_errors():
        raise DatasetValidationError(validation_context.errors())

    return validation_context.get_dataframe()


def set_data_types(df: pd.DataFrame, schema: Schema) -> Tuple[pd.DataFrame, list[str]]:
    error_list = []
    columns_to_cast = schema.get_column_dtypes_to_cast()
    if columns_to_cast:
        for column, column_type in columns_to_cast.items():
            try:
                df = df.astype({column: column_type})
            except (TypeError, ValueError):
                error_list.append(
                    f"Failed to convert column [{column}] to type [{column_type}]"
                )
    return df, error_list


def dataset_has_correct_columns(
    df: pd.DataFrame, schema: Schema
) -> Tuple[pd.DataFrame, list[str]]:
    expected_columns = schema.get_column_names()
    actual_columns = list(df.columns)
    error_list = []

    has_expected_columns = all(
        [expected_column in actual_columns for expected_column in expected_columns]
    )

    if not has_expected_columns or len(actual_columns) != len(expected_columns):
        # Cannot reasonably proceed with further validation if we don't even have the correct columns
        raise UnprocessableDatasetError(
            [f"Expected columns: {expected_columns}, received: {actual_columns}"]
        )

    return df, error_list


def dataset_has_acceptable_null_values(
    data_frame: pd.DataFrame, schema: Schema
) -> Tuple[pd.DataFrame, list[str]]:
    error_list = []
    for column in schema.columns:
        if not column.allow_null and data_frame[column.name].isnull().values.any():
            error_list.append(f"Column [{column.name}] does not allow null values")

    return data_frame, error_list


def dataset_has_correct_data_types(
    data_frame: pd.DataFrame, schema: Schema
) -> Tuple[pd.DataFrame, list[str]]:
    error_list = []
    for column in schema.columns:
        actual_type = data_frame[column.name].dtype
        expected_type = column.data_type

        types_match = actual_type == expected_type

        if not types_match and not is_valid_custom_dtype(actual_type, expected_type):
            error_list.append(
                f"Column [{column.name}] has an incorrect data type. Expected {expected_type}, received {actual_type}"
                # noqa: E501
            )

    return data_frame, error_list


def dataset_has_no_illegal_characters_in_partition_columns(
    data_frame: pd.DataFrame, schema: Schema
) -> Tuple[pd.DataFrame, list[str]]:
    error_list = []
    for column in schema.get_partition_columns():
        series = data_frame[column.name]
        if not column.data_type == DataTypes.DATE and series.dtype == object:
            any_illegal_characters = any(
                [value is True for value in series.str.contains("/")]
            )
            if any_illegal_characters:
                error_list.append(
                    f"Partition column [{column.name}] has values with illegal characters '/'"
                )

    return data_frame, error_list


def convert_dates_to_ymd(
    df: pd.DataFrame, schema: Schema
) -> Tuple[pd.DataFrame, list[str]]:
    error_list = []
    for column in schema.get_columns_by_type(DataTypes.DATE):
        df[column.name], error = convert_date_column_to_ymd(
            column.name, df[column.name], column.format
        )
        if error is not None:
            error_list.append(error)

    return df, error_list


def remove_empty_rows(df: pd.DataFrame) -> Tuple[pd.DataFrame, list[str]]:
    error_list = []
    try:
        df.dropna(how="all", inplace=True)
    except (TypeError, ValueError, KeyError) as error:
        error_list.append(f"Could not drop null values: {error}")
    return df, error_list


def clean_column_headers(df: pd.DataFrame) -> Tuple[pd.DataFrame, list[str]]:
    error_list = []
    try:
        df.columns = df.columns.map(clean_column_name)
    except (TypeError, ValueError, KeyError) as error:
        error_list.append(f"Could not clean column names: {error}")
    return df, error_list


def convert_date_column_to_ymd(
    column_name: str, series: pd.Series, date_format: str
) -> Tuple[pd.Series, str]:
    error_result = None
    try:
        series = pd.to_datetime(series, format=date_format)
        series = series.apply(format_timestamp_as_ymd)
    except ValueError:
        error_result = f"Column [{column_name}] does not match specified date format in at least one row"
    return series, error_result


def format_timestamp_as_ymd(timestamp: Timestamp) -> str:
    return f"{timestamp.year}-{str(timestamp.month).zfill(2)}-{str(timestamp.day).zfill(2)}"


def is_valid_custom_dtype(actual_type: str, expected_type: str) -> bool:
    is_custom_dtype = expected_type in DataTypes.custom_data_types()
    return is_custom_dtype and actual_type == DataTypes.OBJECT
