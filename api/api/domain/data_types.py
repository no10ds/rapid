from typing import List


class DataTypes:
    DATE = "date"
    INT64 = "Int64"
    INT32 = "Int32"
    INT16 = "Int16"
    FLOAT = "Float64"
    STRING = "object"
    OBJECT = "object"
    BOOLEAN = "boolean"

    @classmethod
    def accepted_data_types(cls) -> List[str]:
        return [
            cls.DATE,
            cls.INT16,
            cls.INT32,
            cls.INT64,
            cls.FLOAT,
            cls.STRING,
            cls.OBJECT,
            cls.BOOLEAN,
        ]

    @classmethod
    def numeric_data_types(cls) -> List[str]:
        return [cls.INT16, cls.INT32, cls.INT64, cls.FLOAT]

    @classmethod
    def data_types_to_cast(cls) -> List[str]:
        return [cls.INT16, cls.INT32, cls.INT64, cls.FLOAT, cls.BOOLEAN]

    @classmethod
    def custom_data_types(cls) -> List[str]:
        return [cls.DATE]
