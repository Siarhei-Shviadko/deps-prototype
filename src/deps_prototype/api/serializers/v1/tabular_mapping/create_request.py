from typing import Any

from pydantic import Field, model_validator

from deps_prototype.domain.model import HeaderType, RawHeader

from ...configured_base_serializer import ConfiguredBaseSerializer
from .header import SerializedHeader

__all__ = ["CreateTabularMappingRequest"]


class CreateTabularMappingRequest(ConfiguredBaseSerializer):
    code: str
    header_type: HeaderType = Field(..., alias="headerType")
    headers: list[SerializedHeader]
    occurrence_index: int = Field(0, alias="occurrenceIndex")

    @model_validator(mode="after")
    def check_headers_not_empty(self) -> "CreateTabularMappingRequest":  # noqa: N805
        if not self.headers:
            raise ValueError("Headers must contain at least one item")

        return self

    @property
    def raw_headers(self) -> list[RawHeader]:
        return [RawHeader(name=header.name, aliases=header.aliases) for header in self.headers]
