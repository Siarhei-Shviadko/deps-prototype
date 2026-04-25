from abc import ABC, abstractmethod

__all__ = ["IDocumentTypeProxy"]


class IDocumentTypeProxy(ABC):
    @abstractmethod
    def delete_document_type(self, document_type_id: str) -> None:
        pass
