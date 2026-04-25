from pydantic import field_validator

from deps_prototype.domain.model import UniqueList

from ...configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["ModifyMappingRequest"]


class ModifyMappingRequest(ConfiguredBaseSerializer):
    keys: UniqueList[str]

    @field_validator("keys", mode="before")
    @classmethod
    def validate_keys(cls, v):  # noqa: N805
        if isinstance(v, list):
            return UniqueList(v)
        return v
