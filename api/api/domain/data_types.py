from strenum import StrEnum
from pandera.pandas import dtypes as pandera_dtypes
from api.common.custom_exceptions import UnsupportedTypeError


class NumericType(StrEnum):
    INTEGER = "integer"
    INT = "int"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT16 = "float16"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
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
    STRING_PYTHON = "string[python]"


class DateType(StrEnum):
    DATE = "date"
    DATETIME = "datetime"
    DATETIME64 = "datetime64"
    DATETIME64_NS = "datetime64[ns]"


class TimestampType(StrEnum):
    TIMESTAMP = "timestamp"


class PanderaDataType(StrEnum):
    BOOLEAN = BooleanType.BOOLEAN
    DATE = DateType.DATE
    DATETIME = DateType.DATETIME
    DATETIME64 = DateType.DATETIME64
    DATETIME64_NS = DateType.DATETIME64_NS
    MIXED = StringType.MIXED
    MIXED_INTEGER = StringType.MIXED_INTEGER
    STRING = StringType.STRING
    STRING_PYTHON = StringType.STRING_PYTHON
    INT = NumericType.INT
    INT8 = NumericType.INT8
    INT16 = NumericType.INT16
    INT32 = NumericType.INT32
    INT64 = NumericType.INT64
    FLOAT = NumericType.FLOAT
    FLOAT16 = NumericType.FLOAT16
    FLOAT32 = NumericType.FLOAT32
    FLOAT64 = NumericType.FLOAT64


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
    

PANDERA_ENGINE_TO_ATHENA_CONVERTER = {
    PanderaDataType.INT: AthenaDataType.INT,
    PanderaDataType.INT8: AthenaDataType.TINYINT,
    PanderaDataType.INT16: AthenaDataType.SMALLINT,
    PanderaDataType.INT32: AthenaDataType.INT,
    PanderaDataType.INT64: AthenaDataType.BIGINT,
    PanderaDataType.FLOAT: AthenaDataType.FLOAT,
    PanderaDataType.FLOAT16: AthenaDataType.FLOAT,
    PanderaDataType.FLOAT32: AthenaDataType.FLOAT,
    PanderaDataType.FLOAT64: AthenaDataType.DOUBLE,
    PanderaDataType.DATETIME64: AthenaDataType.TIMESTAMP,
    StringType.STRING: AthenaDataType.STRING,
    PanderaDataType.STRING_PYTHON: AthenaDataType.STRING,
    PanderaDataType.BOOLEAN: AthenaDataType.BOOLEAN,
    PanderaDataType.DATETIME64_NS: AthenaDataType.TIMESTAMP,
    PanderaDataType.DATE: AthenaDataType.DATE,
}


def is_date_type(type) -> bool:
    type_str = str(type)
    date_type_values = [date_type.value for date_type in DateType]
    return type_str in date_type_values


def convert_pandera_column_to_athena(pandera_dtype: pandera_dtypes) -> str:

    try:
        dtype_str = str(pandera_dtype)
        return PANDERA_ENGINE_TO_ATHENA_CONVERTER[dtype_str].value
    except KeyError:
        pass
    
    dtype = type(pandera_dtype)
    dtype_str = str(pandera_dtype)
    raise UnsupportedTypeError(
        f"Unable to convert the pandera type [{dtype}] with string representation '{dtype_str}' to Athena Schema. "
        f"Supported: {list(PANDERA_ENGINE_TO_ATHENA_CONVERTER.keys())}"
    )
