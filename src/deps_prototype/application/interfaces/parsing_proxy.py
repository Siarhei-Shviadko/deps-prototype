from abc import ABC, abstractmethod

from deps_prototype.domain.model import DocumentLayout, ParsingFeature

__all__ = ["IParsingProxy"]


class IParsingProxy(ABC):
    @abstractmethod
    def get_document_layout(
        self,
        document_id: str,
        parsing_type: str,
        language: str,
        parsing_features: tuple[ParsingFeature],
    ) -> DocumentLayout:
        pass
