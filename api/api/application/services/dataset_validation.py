from typing import Tuple

import pandas as pd
from pandas import Timestamp

from api.common.custom_exceptions import (
    DatasetValidationError,
    UnprocessableDatasetError,
)
from api.common.value_transformers import clean_column_name
from api.domain.data_types import (
    StringType,
    DateType,
)
from api.domain.schema import Schema
from api.domain.validation_context import ValidationContext


def build_validated_dataframe(schema: Schema, dataframe: pd.DataFrame) -> pd.DataFrame:
    return transform_and_validate(schema, dataframe)


def transform_and_validate(schema: Schema, data: pd.DataFrame) -> pd.DataFrame:
    validation_context = (
        ValidationContext(data)
        .pipe(dataset_has_rows)
        .pipe(remove_empty_rows)
        .pipe(clean_column_headers)
        .pipe(convert_date_columns, schema)
        .pipe(dataset_has_no_illegal_characters_in_partition_columns, schema)
    )

    if validation_context.has_errors():
        raise DatasetValidationError(validation_context.errors())

    return validation_context.get_dataframe()


def dataset_has_rows(df: pd.DataFrame) -> Tuple[pd.DataFrame, list[str]]:
    if df.shape[0] == 0:
        # Cannot proceed if there are no rows
        raise UnprocessableDatasetError(["Dataset has no rows, it cannot be processed"])

    return df, []


def convert_date_columns(
    data_frame: pd.DataFrame, schema: Schema
) -> Tuple[pd.DataFrame, list[str]]:
    error_list = []

    for column in schema.get_columns_by_type(DateType):
        try:
            data_frame[column.name] = pd.to_datetime(
                data_frame[column.name], format=column.format
            )
        except ValueError:
            error_list.append(
                f"Column [{column.name}] does not match specified date format in at least one row"
            )

    return data_frame, error_list


def dataset_has_no_illegal_characters_in_partition_columns(
    data_frame: pd.DataFrame, schema: Schema
) -> Tuple[pd.DataFrame, list[str]]:
    error_list = []
    for column in schema.get_partition_columns():
        series = data_frame[column.name]
        if not column.is_of_data_type(DateType) and series.dtype == object:
            any_illegal_characters = any(
                [value is True for value in series.str.contains("/")]
            )
            if any_illegal_characters:
                error_list.append(
                    f"Partition column [{column.name}] has values with illegal characters '/'"
                )

    return data_frame, error_list


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
    """
    Custom data types should be validated separately, rather than by column type comparisons
    """
    is_custom_dtype = expected_type in list(DateType)
    return is_custom_dtype and actual_type in list(StringType)
