import os

from deps_prototype.extras.exceptions import FileStorageRequestError

__all__ = ["FakeStorageService"]


class FakeStorageService:
    def __init__(self):
        self.storage_dict = {}

    def delete_file(self, file_path):
        if file_path in self.storage_dict:
            del self.storage_dict[file_path]
        else:
            raise FileStorageRequestError("File storage service returned 404 code: msg")

    def upload_content(self, file_path: str, content: bytes):
        file_path, filename = os.path.split(file_path)
        self.storage_dict[file_path] = content
        return file_path
