import logging

from deps_extracted_data import ExtractedData
from deps_extracted_data.serializers.v2 import SerializedExtractedData
from requests import Response

from deps_prototype.application import IExtractionProxy

from ..exeptions import ExtractionProxyRequestError
from ..generic import GenericProxy
from .document_type_data import DocumentTypeData

__all__ = ["ExtractionProxy"]


class ExtractionProxy(IExtractionProxy, GenericProxy):
    v2_url_suffix = "/api/extraction/v2"
    exception = ExtractionProxyRequestError

    def __init__(self, base_url: str, timeout: int = 60, ssl_verify: bool = False) -> None:
        super().__init__(base_url)
        self._timeout = timeout
        self._ssl_verify = ssl_verify

        self._logger = logging.getLogger(self.__class__.__name__)

    def save_extracted_data(self, extracted_data: ExtractedData) -> Response:
        url = f"{self._base_url}{self.v2_url_suffix}/extracted-data/{extracted_data.document_id}"
        json = SerializedExtractedData.from_model(extracted_data).model_dump(by_alias=True)

        response = self._session.put(url, timeout=self._timeout, verify=self._ssl_verify, json=json)

        self._check_response(response)

        return response

    def create_document_type(
        self,
        name: str,
        language: str,
        engine: str,
        extractor_type: str,
        description: str | None = None,
    ) -> str:
        data = {
            "name": name,
            "extractorType": extractor_type,
            "engine": engine,
            "language": language,
            "description": description,
        }
        response = self._session.post(
            url=f"{self._base_url}{self.v2_url_suffix}/document-types/attach-extractor",
            json=data,
            timeout=self._timeout,
            verify=self._ssl_verify,
        )

        self._check_response(response)

        return DocumentTypeData.from_dict(response.json()).id
