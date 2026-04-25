from typing import TypedDict

from .mapping import Mapping
from .prototype import Prototype
from .tabular_mapping import TabularMapping

__all__ = ["PrototypeWithMappings"]


class PrototypeWithMappings(TypedDict):
    prototype: Prototype
    mappings: list[Mapping]
    tabular_mappings: list[TabularMapping]
