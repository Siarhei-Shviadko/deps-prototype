from pydantic import Field

from deps_prototype.domain.model import LayoutState, ReferenceLayout

from ...configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["SerializedReferenceLayout"]


class SerializedReferenceLayout(ConfiguredBaseSerializer):
    id: str
    prototype_id: str = Field(..., alias="prototypeId")
    title: str | None = None
    state: LayoutState
    blob_name: str = Field(..., alias="blobName")

    @classmethod
    def from_model(cls, reference_layout: ReferenceLayout) -> "SerializedReferenceLayout":
        return cls(
            id=reference_layout.id(),
            prototype_id=reference_layout.prototype_id(),
            title=reference_layout.title,
            state=reference_layout.state,
            blob_name=reference_layout.blob_name,
        )
