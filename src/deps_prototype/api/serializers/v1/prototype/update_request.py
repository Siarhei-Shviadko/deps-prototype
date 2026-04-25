from ...configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["UpdatePrototypeRequest"]


class UpdatePrototypeRequest(ConfiguredBaseSerializer):
    engine: str | None = None
    language: str | None = None
    description: str | None = None
