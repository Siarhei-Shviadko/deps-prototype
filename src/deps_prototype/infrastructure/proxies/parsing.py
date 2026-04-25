import logging

from deps_prototype.application import IParsingProxy
from deps_prototype.domain.model import DocumentLayout, ParsingFeature

from .exeptions import ParsingProxyRequestError
from .generic import GenericProxy

__all__ = ["ParsingProxy"]


class ParsingProxy(IParsingProxy, GenericProxy):
    v1_url_suffix = "/api/parsing/v1"
    exception = ParsingProxyRequestError

    def __init__(self, base_url: str, timeout: int = 60, ssl_verify: bool = False) -> None:
        super().__init__(base_url)
        self._timeout = timeout
        self._ssl_verify = ssl_verify

        self._logger = logging.getLogger(self.__class__.__name__)

    def get_document_layout(
        self,
        document_id: str,
        parsing_type: str,
        language: str,
        parsing_features: tuple[ParsingFeature],
    ) -> DocumentLayout:
        url = f"{self._base_url}{self.v1_url_suffix}/document-layout/{document_id}"
        params = {
            "features": parsing_features,
            "parsingType": parsing_type,
            "language": language,
        }
        response = self._session.get(url=url, params=params, timeout=self._timeout, verify=self._ssl_verify)

        self._check_response(response)

        return DocumentLayout.from_dict(response.json())
