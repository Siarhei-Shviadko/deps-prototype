from pydantic import Field

from deps_prototype.domain.model import DataTypeCode, MappingType

from ...configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["CreateMappingRequest"]


class CreateMappingRequest(ConfiguredBaseSerializer):
    code: str = Field(..., description="Mapping code equal to the Field Code this Mapping belongs to.")
    data_type: DataTypeCode = Field(..., alias="typeCode")
    keys: list[str]
    mapping_type: MappingType = Field(..., alias="mappingType")
