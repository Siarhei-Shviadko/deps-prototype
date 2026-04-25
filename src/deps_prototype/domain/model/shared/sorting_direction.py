from enum import Enum

__all__ = ["SortingDirection"]


class SortingDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"
