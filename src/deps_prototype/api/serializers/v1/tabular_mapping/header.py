from deps_prototype.domain.model import Header

from ...configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["SerializedHeader"]


class SerializedHeader(ConfiguredBaseSerializer):
    name: str
    aliases: set[str]

    @classmethod
    def from_model(cls, header: Header) -> "SerializedHeader":
        return cls(
            name=header.name,
            aliases=header.aliases,
        )
