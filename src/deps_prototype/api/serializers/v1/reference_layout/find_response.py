from deps_prototype.domain.model import ReferenceLayout

from ...configured_base_serializer import ConfiguredBaseSerializer
from .reference_layout import SerializedReferenceLayout

__all__ = ["FindReferenceLayoutsResponse"]


class FindReferenceLayoutsResponse(ConfiguredBaseSerializer):
    reference_layouts: list[SerializedReferenceLayout]

    @classmethod
    def from_model(cls, reference_layouts: list[ReferenceLayout]) -> "FindReferenceLayoutsResponse":
        return cls(
            reference_layouts=[SerializedReferenceLayout.from_model(layout) for layout in reference_layouts],
        )
