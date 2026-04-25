from abc import ABC, abstractmethod

from deps_extracted_data import ExtractedData
from requests import Response

__all__ = ["IExtractionProxy"]


class IExtractionProxy(ABC):
    @abstractmethod
    def save_extracted_data(self, extracted_data: ExtractedData) -> Response:
        pass

    @abstractmethod
    def create_document_type(
        self,
        name: str,
        language: str,
        engine: str,
        extractor_type: str,
        description: str | None = None,
    ) -> str:
        pass
