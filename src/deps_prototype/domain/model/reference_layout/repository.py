from abc import ABC, abstractmethod

from .reference_layout import ReferenceLayout

__all__ = ["IReferenceLayoutRepository"]


class IReferenceLayoutRepository(ABC):
    @abstractmethod
    def save(self, reference_layout: ReferenceLayout) -> None:
        pass

    @abstractmethod
    def reference_layout_of_id(self, id_: str, prototype_id: str) -> ReferenceLayout | None:
        pass

    @abstractmethod
    def reference_layouts_of_ids(self, ids: list[str], prototype_id: str) -> list[ReferenceLayout]:
        pass

    @abstractmethod
    def reference_layouts_of_prototype(self, prototype_id: str) -> list[ReferenceLayout]:
        pass

    @abstractmethod
    def delete(self, reference_layout: ReferenceLayout) -> None:
        pass

    @abstractmethod
    def delete_all(self, reference_layouts: list[ReferenceLayout]) -> None:
        pass
