from abc import ABC, abstractmethod

from .mapping import Mapping

__all__ = ["IMappingRepository"]


class IMappingRepository(ABC):
    @abstractmethod
    def mapping_by_code(self, code: str, prototype_id: str) -> Mapping | None:
        pass

    @abstractmethod
    def save(self, mapping: Mapping) -> None:
        pass

    @abstractmethod
    def delete(self, mapping_code: str, prototype_id: str) -> None:
        pass

    @abstractmethod
    def mappings_of_prototype(self, prototype_id: str) -> list[Mapping]:
        pass
