from abc import ABC, abstractmethod

from ...shared import DocumentLayout, KeyValuePair
from .comparer import Comparer

__all__ = ["Allocator"]


class Allocator(ABC):
    comparer = Comparer

    def __init__(self, document_layout: DocumentLayout, keys: set[str]):
        self._document_layout = document_layout
        self._keys = keys

    @abstractmethod
    def allocate(self) -> list[KeyValuePair]:
        pass
