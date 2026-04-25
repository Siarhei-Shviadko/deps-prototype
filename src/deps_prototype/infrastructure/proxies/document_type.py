import logging

from deps_prototype.application import IDocumentTypeProxy
from deps_prototype.constants import V1_PREFIX
from deps_prototype.domain.exceptions import RestClientError

from .generic import GenericProxy

__all__ = ["DocumentTypeProxy"]


class DocumentTypeProxy(GenericProxy, IDocumentTypeProxy):  # noqa: WPS338
    TYPES_URL = f"/api/document-type{V1_PREFIX}/types"
    exception = RestClientError

    def __init__(self, base_url: str, timeout: int, ssl_verify: bool) -> None:
        super().__init__(base_url)
        self._timeout = timeout
        self._verify = ssl_verify

        self._logger = logging.getLogger(self.__class__.__name__)

    def delete_document_type(self, document_type_id: str) -> None:
        response = self._session.delete(
            url=f"{self._base_url}{self.TYPES_URL}/{document_type_id}",
        )
        self._check_response(response)
