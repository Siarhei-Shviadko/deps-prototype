from dataclasses import dataclass

from ...shared import SortingDirection
from .sorting_field import PrototypeSortingField

__all__ = ["PrototypeSorting"]


@dataclass
class PrototypeSorting:
    field: PrototypeSortingField = PrototypeSortingField.CREATED_AT
    direction: SortingDirection = SortingDirection.DESC
