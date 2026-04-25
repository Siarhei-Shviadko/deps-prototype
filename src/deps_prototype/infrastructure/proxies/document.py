import json
import logging

from deps_prototype.application import IDocumentProxy
from deps_prototype.constants import V1_PREFIX

from .exeptions import DocumentProxyRequestError
from .generic import GenericProxy

__all__ = ["DocumentProxy"]


class DocumentProxy(IDocumentProxy, GenericProxy):
    v1_url_suffix = f"/api/document{V1_PREFIX}"
    exception = DocumentProxyRequestError

    def __init__(self, base_url: str, timeout: int = 60, ssl_verify: bool = False) -> None:
        super().__init__(base_url)
        self._timeout = timeout
        self._ssl_verify = ssl_verify

        self._logger = logging.getLogger(self.__class__.__name__)

    def get_prototype_ids_with_documents(self, prototype_ids: list[str]) -> list[str]:
        url = f"{self._base_url}{self.v1_url_suffix}/documents"
        params = {"types": json.dumps(prototype_ids)}

        response = self._session.get(url, timeout=self._timeout, verify=self._ssl_verify, params=params)

        self._check_response(response)

        return [d["documentType"] for d in response.json()["result"]]
