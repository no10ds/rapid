from strenum import StrEnum
from enum import Enum

from pandas import DataFrame
from pandas.api.types import infer_dtype

import pandera

from api.common.custom_exceptions import UnsupportedTypeError


class NumericType(StrEnum):
    INTEGER = "integer"
    INT = "int"
    MIXED_INTEGER_FLOAT = "mixed-integer-float"
    FLOATING = "floating"
    TINYINT = "tinyint"
    SMALLINT = "smallint"
    BIGINT = "bigint"
    DOUBLE = "double"
    FLOAT = "float"
    DECIMAL = "decimal"


class BooleanType(StrEnum):
    BOOLEAN = "boolean"


class StringType(StrEnum):
    STRING = "string"
    OBJECT = "object"
    CHAR = "char"
    VARCHAR = "varchar"
    MIXED_INTEGER = "mixed-integer"
    MIXED = "mixed"


class DateType(StrEnum):
    DATE = "date"
    DATETIME = "datetime"
    DATETIME64 = "datetime64"


class TimestampType(StrEnum):
    TIMESTAMP = "timestamp"


class PandasDataType(StrEnum):
    BOOLEAN = BooleanType.BOOLEAN
    DATE = DateType.DATE
    DATETIME = DateType.DATETIME
    DATETIME64 = DateType.DATETIME64
    DECIMAL = NumericType.DECIMAL
    INTEGER = NumericType.INTEGER
    FLOATING = NumericType.FLOATING
    MIXED = StringType.MIXED
    MIXED_INTEGER = StringType.MIXED_INTEGER
    MIXED_INTEGER_FLOAT = NumericType.MIXED_INTEGER_FLOAT
    OBJECT = StringType.OBJECT
    STRING = StringType.STRING


class AthenaDataType(StrEnum):
    BIGINT = NumericType.BIGINT
    BOOLEAN = BooleanType.BOOLEAN
    CHAR = StringType.CHAR
    DATE = DateType.DATE
    DECIMAL = NumericType.DECIMAL
    DOUBLE = NumericType.DOUBLE
    FLOAT = NumericType.FLOAT
    INT = NumericType.INT
    SMALLINT = NumericType.SMALLINT
    STRING = StringType.STRING
    TIMESTAMP = TimestampType.TIMESTAMP
    TINYINT = NumericType.TINYINT
    VARCHAR = StringType.VARCHAR


PANDAS_TO_ATHENA_CONVERTER = {
    PandasDataType.BOOLEAN: AthenaDataType.BOOLEAN,
    PandasDataType.DATE: AthenaDataType.DATE,
    PandasDataType.DATETIME: AthenaDataType.DATE,
    PandasDataType.DATETIME64: AthenaDataType.DATE,
    PandasDataType.DECIMAL: AthenaDataType.DECIMAL,
    PandasDataType.INTEGER: AthenaDataType.INT,
    PandasDataType.FLOATING: AthenaDataType.DOUBLE,
    PandasDataType.MIXED: AthenaDataType.STRING,
    PandasDataType.MIXED_INTEGER: AthenaDataType.STRING,
    PandasDataType.MIXED_INTEGER_FLOAT: AthenaDataType.DOUBLE,
    PandasDataType.STRING: AthenaDataType.STRING,
    PandasDataType.OBJECT: AthenaDataType.STRING,
}


ATHENA_TO_PANDERA_CONVERTER = {
    AthenaDataType.STRING: pandera.dtypes.String,
    AthenaDataType.VARCHAR: pandera.dtypes.String,
    AthenaDataType.CHAR: pandera.dtypes.String,
    AthenaDataType.INT: pandera.dtypes.Int,
    AthenaDataType.BIGINT: pandera.dtypes.Int64,
    AthenaDataType.SMALLINT: pandera.dtypes.Int16,
    AthenaDataType.TINYINT: pandera.dtypes.Int8,
    AthenaDataType.DOUBLE: pandera.dtypes.Float64,
    AthenaDataType.FLOAT: pandera.dtypes.Float32,
    AthenaDataType.DECIMAL: pandera.dtypes.Float64, 
    AthenaDataType.BOOLEAN: pandera.dtypes.Bool,
    AthenaDataType.DATE: pandera.dtypes.Timestamp,
    AthenaDataType.TIMESTAMP: pandera.dtypes.Timestamp,
}



def convert_athena_to_pandera_type(athena_type: str) -> str:
    try:
        pandas_type = ATHENA_TO_PANDERA_CONVERTER[athena_type]
    except KeyError:
        raise UnsupportedTypeError(
            f"Unable to convert data type: {athena_type} to the Pandera Schema. This type is currently unsupported."
        )
    return pandas_type

# TODO: Replace with pandera's equivalent
def is_date_type(type: str) -> bool:
    return type in [AthenaDataType.DATE.value]


def extract_athena_types(df: DataFrame) -> dict:
    types = {}
    for column in df.columns:
        if df[column].dropna().size == 0:
            continue
        dtype = str(infer_dtype(df[column], skipna=True))
        try:
            types[column] = PANDAS_TO_ATHENA_CONVERTER[dtype].value
        except KeyError:
            raise UnsupportedTypeError(
                f"Unable to convert the column [{column}] of type [{dtype}] to Athena Schema. This type is currently unsupported."
            )

    return types
