from uuid import uuid4

from deps_extracted_data import ExtractedData
from requests import Response

from deps_prototype.application import IExtractionProxy

__all__ = ["FakeExtractionProxy"]


class FakeExtractionProxy(IExtractionProxy):
    def create_document_type(
        self,
        name: str,
        language: str,
        engine: str,
        extractor_type: str,
        description: str | None = None,
    ) -> str:
        return uuid4().hex

    def save_extracted_data(self, extracted_data: ExtractedData) -> Response:
        pass
