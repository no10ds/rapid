from strenum import StrEnum

import pandera.dtypes
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


class PanderaDataType(StrEnum):
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

PANDERA_TO_ATHENA_CONVERTER = {
    pandera.dtypes.Int: AthenaDataType.INT,
    pandera.dtypes.Int8: AthenaDataType.TINYINT,
    pandera.dtypes.Int16: AthenaDataType.SMALLINT,
    pandera.dtypes.Int32: AthenaDataType.INT,
    pandera.dtypes.Int64: AthenaDataType.BIGINT,
    pandera.dtypes.Float: AthenaDataType.FLOAT,
    pandera.dtypes.Float32: AthenaDataType.FLOAT,
    pandera.dtypes.Float64: AthenaDataType.DOUBLE,
    pandera.dtypes.Bool: AthenaDataType.BOOLEAN,
    pandera.dtypes.String: AthenaDataType.STRING,
    pandera.dtypes.Timestamp: AthenaDataType.TIMESTAMP,
    pandera.dtypes.DateTime: AthenaDataType.TIMESTAMP,
    pandera.dtypes.Date: AthenaDataType.DATE,
}

# TODO Pandera: tidy up
PANDERA_ENGINE_TO_ATHENA_CONVERTER = {
    # Numpy engine types
    "object": AthenaDataType.STRING,
    "str": AthenaDataType.STRING,
    "bool": AthenaDataType.BOOLEAN,
    "int8": AthenaDataType.TINYINT,
    "int16": AthenaDataType.SMALLINT,
    "int32": AthenaDataType.INT,
    "int64": AthenaDataType.BIGINT,
    "float16": AthenaDataType.FLOAT,
    "float32": AthenaDataType.FLOAT,
    "float64": AthenaDataType.DOUBLE,
    "datetime64": AthenaDataType.TIMESTAMP,
    "timedelta64[ns]": AthenaDataType.TIMESTAMP,
    
    # Pandas engine types  
    "string": AthenaDataType.STRING,
    "string[python]": AthenaDataType.STRING,
    "boolean": AthenaDataType.BOOLEAN,
    "Int8": AthenaDataType.TINYINT,
    "Int16": AthenaDataType.SMALLINT,
    "Int32": AthenaDataType.INT,
    "Int64": AthenaDataType.BIGINT,
    "Float32": AthenaDataType.FLOAT,
    "Float64": AthenaDataType.DOUBLE,
    "datetime64[ns]": AthenaDataType.TIMESTAMP,
    "date": AthenaDataType.DATE,
}


def is_date_type(type: str) -> bool:
    return type in [AthenaDataType.DATE.value]


# def convert_pandera_column_to_athena(pandera_dtype: pandera.dtypes) -> str:

#     try:
#         dtype = type(pandera_dtype)
#         return PANDERA_TO_ATHENA_CONVERTER[dtype].value
#     except KeyError:
#         pass
    
#     # If that fails, try to convert using the string representation
#     # This handles engine-specific types like pandera.engines.numpy_engine.Object
#     try:
#         dtype_str = str(pandera_dtype)
#         return PANDERA_ENGINE_TO_ATHENA_CONVERTER[dtype_str].value
#     except KeyError:
#         pass
    
#     # If both approaches fail, raise the original error with more context
#     dtype = type(pandera_dtype)
#     dtype_str = str(pandera_dtype)
#     raise UnsupportedTypeError(
#         f"Unable to convert the pandera type [{dtype}] with string representation '{dtype_str}' to Athena Schema. "
#         f"This type is currently unsupported. Supported type classes: {list(PANDERA_TO_ATHENA_CONVERTER.keys())}. "
#         f"Supported string representations: {list(PANDERA_ENGINE_TO_ATHENA_CONVERTER.keys())}"
#     )

def convert_pandera_column_to_athena(pandera_dtype: pandera.dtypes) -> str:

    try:
        dtype_str = str(pandera_dtype)
        return PANDERA_ENGINE_TO_ATHENA_CONVERTER[dtype_str].value
    except KeyError:
        pass
    
    dtype = type(pandera_dtype)
    dtype_str = str(pandera_dtype)
    raise UnsupportedTypeError(
        f"Unable to convert the pandera type [{dtype}] with string representation '{dtype_str}' to Athena Schema. "
        f"This type is currently unsupported. Supported type classes: {list(PANDERA_TO_ATHENA_CONVERTER.keys())}. "
        f"Supported string representations: {list(PANDERA_ENGINE_TO_ATHENA_CONVERTER.keys())}"
    )
