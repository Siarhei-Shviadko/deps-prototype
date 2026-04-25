from pydantic import Field

from deps_prototype.domain.model import DataTypeCode, Mapping, MappingType

from ...configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["SerializedMapping"]


class SerializedMapping(ConfiguredBaseSerializer):
    code: str
    prototype_id: str = Field(..., alias="prototypeId")
    keys: list[str]
    data_type: DataTypeCode = Field(..., alias="dataType")
    mapping_type: MappingType = Field(..., alias="mappingType")

    @classmethod
    def from_model(cls, mapping: Mapping) -> "SerializedMapping":
        return cls(
            code=mapping.code,
            prototype_id=mapping.prototype_id(),
            keys=mapping.keys,
            data_type=mapping.data_type,
            mapping_type=mapping.mapping_type,
        )
