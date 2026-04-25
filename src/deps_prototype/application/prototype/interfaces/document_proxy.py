from abc import ABC, abstractmethod

__all__ = ["IDocumentProxy"]


class IDocumentProxy(ABC):
    @abstractmethod
    def get_prototype_ids_with_documents(self, prototype_ids: list[str]) -> list[str]:
        pass
