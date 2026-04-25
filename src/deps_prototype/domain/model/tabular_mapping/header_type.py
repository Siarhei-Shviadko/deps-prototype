from enum import Enum

__all__ = ["HeaderType"]


class HeaderType(str, Enum):
    ROWS = "rows"
    COLUMNS = "columns"
