from datetime import datetime

from pydantic import Field

from deps_prototype.domain.model import Prototype

from ...configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["SerializedPrototype"]


class SerializedPrototype(ConfiguredBaseSerializer):
    id: str
    name: str
    engine: str
    language: str
    created_at: datetime = Field(..., alias="createdAt")
    description: str | None = None

    @classmethod
    def from_model(cls, prototype: Prototype) -> "SerializedPrototype":
        return cls(
            id=prototype.id(),
            name=prototype.name,
            engine=prototype.engine,
            language=prototype.language,
            created_at=prototype.created_at,
            description=prototype.description,
        )
