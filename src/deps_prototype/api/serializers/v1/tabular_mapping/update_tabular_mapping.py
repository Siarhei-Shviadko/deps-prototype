from pydantic import Field

from deps_prototype.domain.model import HeaderType, RawHeader

from ...configured_base_serializer import ConfiguredBaseSerializer
from .header import SerializedHeader

__all__ = ["UpdateTabularMappingRequest"]


class UpdateTabularMappingRequest(ConfiguredBaseSerializer):
    header_type: HeaderType | None = Field(None, alias="headerType")
    headers: list[SerializedHeader] | None = Field(None, min_length=1)
    occurrence_index: int | None = Field(None, alias="occurrenceIndex")

    @property
    def raw_headers(self) -> list[RawHeader] | None:
        if self.headers is None:
            return None
        return [RawHeader(name=header.name, aliases=set(header.aliases)) for header in self.headers]
