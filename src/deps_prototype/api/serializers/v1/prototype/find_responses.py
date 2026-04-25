from deps_prototype.domain.model import Prototype

from ...configured_base_serializer import ConfiguredBaseSerializer
from .prototype import SerializedPrototype

__all__ = ["FindPrototypesResponse"]


class FindPrototypesResponse(ConfiguredBaseSerializer):
    prototypes: list[SerializedPrototype]
    meta: dict[str, int]

    @classmethod
    def from_model(cls, prototypes: list[Prototype], meta: dict[str, int]) -> "FindPrototypesResponse":
        return cls(
            prototypes=[SerializedPrototype.from_model(prototype) for prototype in prototypes],
            meta=meta,
        )
