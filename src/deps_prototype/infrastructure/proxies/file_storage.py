import logging
import os
from io import BytesIO
from uuid import uuid4

from deps_prototype.extras.exceptions import FileStorageRequestError

from .generic import GenericProxy

__all__ = ["FileStorageProxy"]


class FileStorageProxy(GenericProxy):
    exception: FileStorageRequestError  # type: ignore
    FILE_STORAGE_SERVICE_PREFIX = "/api/storage/v1/file"

    def __init__(self, base_url: str, timeout: int, ssl_verify: bool) -> None:
        super().__init__(base_url)
        self._timeout = timeout
        self._verify = ssl_verify

        self._logger = logging.getLogger(self.__class__.__name__)

    def upload_content(self, file_path: str, content: bytes) -> str:
        file_path = self._generate_unique_file_path(file_path)
        file_path, filename = os.path.split(file_path)
        file = {"file": (filename, BytesIO(content))}

        response = self._session.post(
            url=f"{self._base_url}{self.FILE_STORAGE_SERVICE_PREFIX}",
            files=file,
            data={"replaceIfExists": True},
            timeout=self._timeout,
            verify=self._verify,
        )

        self._check_response(response)
        return response.json()["path"]

    def delete_file(self, file_path: str) -> None:
        response = self._session.delete(
            url=f"{self._base_url}{self.FILE_STORAGE_SERVICE_PREFIX}/{file_path}",
            timeout=self._timeout,
            verify=self._verify,
        )
        self._check_response(response)

    @staticmethod
    def _generate_unique_file_path(file_path: str) -> str:
        root, file_name = os.path.split(file_path)
        _, ext = os.path.splitext(file_name)

        return os.path.join(root, str(uuid4().hex) + ext)
