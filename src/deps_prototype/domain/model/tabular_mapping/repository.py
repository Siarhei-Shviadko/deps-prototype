from abc import ABC, abstractmethod

from .tabular_mapping import TabularMapping

__all__ = ["ITabularMappingRepository"]


class ITabularMappingRepository(ABC):
    @abstractmethod
    def get_by_code(self, code: str, prototype_id: str) -> TabularMapping | None:
        pass

    @abstractmethod
    def mappings_of_prototype(self, prototype_id: str) -> list[TabularMapping]:
        pass

    @abstractmethod
    def save(self, tabular_mapping: TabularMapping) -> None:
        pass

    @abstractmethod
    def delete(self, code: str, prototype_id: str) -> None:
        pass
