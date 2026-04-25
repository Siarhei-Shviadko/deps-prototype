from enum import Enum

__all__ = ["MappingType"]


class MappingType(str, Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
