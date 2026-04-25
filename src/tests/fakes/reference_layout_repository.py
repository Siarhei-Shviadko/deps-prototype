from copy import deepcopy

from deps_prototype.domain.model import IReferenceLayoutRepository, ReferenceLayout

__all__ = ["FakeReferenceLayoutRepository"]


class FakeReferenceLayoutRepository(IReferenceLayoutRepository):
    def __init__(self):
        self._db: dict[tuple[str, str], ReferenceLayout] = {}

    def save(self, reference_layout: ReferenceLayout) -> None:
        reference_layout = deepcopy(reference_layout)
        self._db[(reference_layout.id(), reference_layout.prototype_id())] = reference_layout

    def reference_layout_of_id(self, id_: str, prototype_id: str) -> ReferenceLayout | None:
        return self._db.get((id_, prototype_id))

    def reference_layouts_of_ids(self, ids: list[str], prototype_id: str) -> list[ReferenceLayout]:
        return [
            reference_layout
            for reference_layout in self._db.values()
            if reference_layout.id() in ids and reference_layout.prototype_id() == prototype_id
        ]

    def reference_layouts_of_prototype(self, prototype_id: str) -> list[ReferenceLayout]:
        return [
            reference_layout
            for reference_layout in self._db.values()
            if reference_layout.prototype_id() == prototype_id
        ]

    def delete(self, reference_layout: ReferenceLayout) -> None:
        if self.reference_layout_of_id(reference_layout.id(), reference_layout.prototype_id()):
            del self._db[(reference_layout.id(), reference_layout.prototype_id())]
            reference_layout.delete()

    def delete_all(self, reference_layouts: list[ReferenceLayout]) -> None:
        for reference_layout in reference_layouts:
            self.delete(reference_layout)
