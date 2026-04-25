from enum import Enum

__all__ = ["PrototypeSortingField"]


class PrototypeSortingField(str, Enum):
    ID = "id"
    NAME = "name"
    ENGINE = "engine"
    LANGUAGE = "language"
    CREATED_AT = "createdAt"
