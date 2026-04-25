from enum import Enum

__all__ = ["DataTypeCode"]


class DataTypeCode(str, Enum):
    TABLE = "table"
    STRING = "string"
    CHECKMARK = "checkmark"
    ENUM = "enum"
    DATE = "date"
    NUMERIC = "numeric"
