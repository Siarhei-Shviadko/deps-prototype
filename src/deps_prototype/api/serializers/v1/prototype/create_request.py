from ...configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["CreatePrototypeRequest"]


class CreatePrototypeRequest(ConfiguredBaseSerializer):
    name: str
    engine: str
    language: str
    description: str | None = None
