from pydantic import Field

from deps_prototype.domain.model import HeaderType, TabularMapping

from ...configured_base_serializer import ConfiguredBaseSerializer
from .header import SerializedHeader

__all__ = ["SerializedTabularMapping"]


class SerializedTabularMapping(ConfiguredBaseSerializer):
    code: str
    prototype_id: str = Field(..., alias="prototypeId")
    headers: list[SerializedHeader]
    header_type: HeaderType = Field(..., alias="headerType")
    occurrence_index: int = Field(..., alias="occurrenceIndex")

    @classmethod
    def from_model(cls, tabular_mapping: TabularMapping) -> "SerializedTabularMapping":
        return cls(
            code=tabular_mapping.code,
            prototype_id=tabular_mapping.prototype_id(),
            headers=[SerializedHeader.from_model(header) for header in tabular_mapping.headers],
            header_type=tabular_mapping.header_type,
            occurrence_index=tabular_mapping.occurrence_index,
        )
