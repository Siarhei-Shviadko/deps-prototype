from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from deps_extracted_data import ExtractedData, ExtractedFieldFactory, FieldDataFactory

from deps_prototype.domain.model import (
    AllocatedTable,
    KeyValuePair,
    Mapping,
    TabularMapping,
)

__all__ = ["IExtractor", "IKeyValuePairExtractor", "ITableExtractor"]

TData = TypeVar("TData", list[KeyValuePair], AllocatedTable)
TMapping = TypeVar("TMapping", Mapping, TabularMapping)


class IExtractor(ABC, Generic[TData, TMapping]):
    extracted_field_factory = ExtractedFieldFactory()
    field_data_factory = FieldDataFactory()

    @abstractmethod
    def extract(self, data: TData, mapping: TMapping, extracted_data: ExtractedData) -> None:
        pass


class IKeyValuePairExtractor(IExtractor[list[KeyValuePair], Mapping], ABC):
    @abstractmethod
    def extract(self, data: list[KeyValuePair], mapping: Mapping, extracted_data: ExtractedData) -> None:
        pass


class ITableExtractor(IExtractor[AllocatedTable, TabularMapping], ABC):
    @abstractmethod
    def extract(self, data: AllocatedTable, mapping: TabularMapping, extracted_data: ExtractedData) -> None:
        pass
