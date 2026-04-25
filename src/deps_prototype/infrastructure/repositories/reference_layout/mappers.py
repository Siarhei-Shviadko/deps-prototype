from typing import Mapping

from deps_prototype.domain.model import EntityId, LayoutState, ReferenceLayout

__all__ = ["ReferenceLayoutMapper"]


class ReferenceLayoutMapper:
    @staticmethod
    def from_dict(raw_reference_layout: Mapping[str, str]) -> ReferenceLayout:
        return ReferenceLayout(
            id_=EntityId(raw_reference_layout["id"]),
            prototype_id=EntityId(raw_reference_layout["prototype_id"]),
            state=LayoutState(raw_reference_layout["state"]),
            blob_name=raw_reference_layout["blob_name"],
            title=raw_reference_layout["title"],
        )

    @staticmethod
    def to_dict(reference_layout: ReferenceLayout) -> dict[str, str]:
        return {
            "id": reference_layout.id(),
            "prototype_id": reference_layout.prototype_id(),
            "state": reference_layout.state.value,
            "blob_name": reference_layout.blob_name,
            "title": reference_layout.title,
        }
