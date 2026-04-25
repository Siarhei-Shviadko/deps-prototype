import logging
from typing import Union

from deps_extracted_data import ExtractedData, ExtractedDataFactory

from deps_prototype.domain.exceptions import PrototypeNotFound
from deps_prototype.domain.model import (
    DataTypeCode,
    DocumentLayout,
    IMappingRepository,
    IPrototypeRepository,
    ITabularMappingRepository,
    Mapping,
    MappingType,
    ParsingFeature,
    Prototype,
    TabularMapping,
)

from ..interfaces import IExtractionProxy, IParsingProxy
from .extractors import (
    CheckmarkExtractor,
    DateExtractor,
    EnumExtractor,
    IExtractor,
    IKeyValuePairExtractor,
    ListCheckmarkExtractor,
    ListDateExtractor,
    ListEnumExtractor,
    ListNumericExtractor,
    ListStringExtractor,
    NumericExtractor,
    StringExtractor,
    TableExtractor,
)

__all__ = ["ExtractionService"]

AnyMappingType = Union[Mapping, TabularMapping]


class ExtractionService:
    PARSING_FEATURES = (ParsingFeature.TABLES.value, ParsingFeature.KEY_VALUE_PAIRS.value)

    def __init__(
        self,
        parsing_proxy: IParsingProxy,
        extraction_proxy: IExtractionProxy,
        prototype_repository: IPrototypeRepository,
        mapping_repository: IMappingRepository,
        tabular_mapping_repository: ITabularMappingRepository,
    ) -> None:
        self._parsing_proxy = parsing_proxy
        self._extraction_proxy = extraction_proxy
        self._prototype_repository = prototype_repository
        self._mapping_repository = mapping_repository
        self._tabular_mapping_repository = tabular_mapping_repository

        self._kvp_extractors: dict[tuple[DataTypeCode, MappingType], IKeyValuePairExtractor] = {
            (DataTypeCode.STRING, MappingType.ONE_TO_ONE): StringExtractor(),
            (DataTypeCode.ENUM, MappingType.ONE_TO_ONE): EnumExtractor(),
            (DataTypeCode.DATE, MappingType.ONE_TO_ONE): DateExtractor(),
            (DataTypeCode.NUMERIC, MappingType.ONE_TO_ONE): NumericExtractor(),
            (DataTypeCode.CHECKMARK, MappingType.ONE_TO_ONE): CheckmarkExtractor(),
            (DataTypeCode.STRING, MappingType.ONE_TO_MANY): ListStringExtractor(),
            (DataTypeCode.ENUM, MappingType.ONE_TO_MANY): ListEnumExtractor(),
            (DataTypeCode.DATE, MappingType.ONE_TO_MANY): ListDateExtractor(),
            (DataTypeCode.NUMERIC, MappingType.ONE_TO_MANY): ListNumericExtractor(),
            (DataTypeCode.CHECKMARK, MappingType.ONE_TO_MANY): ListCheckmarkExtractor(),
        }

        self._logger = logging.getLogger(self.__class__.__name__)

    def extract(
        self,
        document_id: int,
        prototype_id: str,
        tenant_id: str,
        language: str | None = None,
        engine: str | None = None,
    ) -> None:
        self._logger.info(f"Starting extraction for document `{document_id}`, using prototype `{prototype_id}`...")

        prototype = self._find_prototype(prototype_id=prototype_id, tenant_id=tenant_id)

        mappings: list[AnyMappingType] = []
        mappings.extend(self._find_mappings(prototype_id=prototype_id))
        mappings.extend(self._find_tabular_mappings(prototype_id=prototype_id))

        if not mappings:
            self._logger.warning(
                f"Can't perform extraction of doc={document_id}, "
                f"because prototype {prototype_id} doesn't have mappings",
            )
            return

        document_layout = self._get_document_layout(
            document_id=str(document_id),
            engine=engine or prototype.engine,
            language=language or prototype.language,
        )

        extracted_data = ExtractedDataFactory.make_extracted_data(document_id=document_id)

        for mapping in mappings:
            self._perform_extraction(mapping, document_layout, extracted_data)

        self._save_extracted_data(extracted_data)

    def _find_mappings(self, prototype_id: str) -> list[Mapping]:
        return self._mapping_repository.mappings_of_prototype(prototype_id=prototype_id)

    def _find_tabular_mappings(self, prototype_id: str) -> list[TabularMapping]:
        return self._tabular_mapping_repository.mappings_of_prototype(prototype_id=prototype_id)

    def _find_prototype(self, prototype_id: str, tenant_id: str) -> Prototype:
        if prototype := self._prototype_repository.prototype_of_id(id_=prototype_id, tenant_id=tenant_id):
            return prototype

        raise PrototypeNotFound(prototype_id)

    def _get_document_layout(self, document_id: str, engine: str, language: str) -> DocumentLayout:
        return self._parsing_proxy.get_document_layout(
            document_id=document_id,
            parsing_type=engine,
            language=language,
            parsing_features=self.PARSING_FEATURES,  # type: ignore
        )

    def _perform_extraction(
        self,
        mapping: AnyMappingType,
        document_layout: DocumentLayout,
        extracted_data: ExtractedData,
    ) -> None:
        extractor = self._choose_extractor(mapping)

        if not extractor:
            self._logger.warning(
                "Extractor for data type `%s` and mapping type `%s` is not implemented",
                mapping.data_type,
                mapping.mapping_type,
            )
            return

        if data := mapping.search_data(document_layout):
            extractor.extract(data, mapping, extracted_data)

    def _choose_extractor(self, mapping: AnyMappingType) -> IExtractor | None:
        if isinstance(mapping, TabularMapping):
            return TableExtractor()

        return self._kvp_extractors.get((mapping.data_type, mapping.mapping_type))

    def _save_extracted_data(self, extracted_data: ExtractedData) -> None:
        self._extraction_proxy.save_extracted_data(extracted_data=extracted_data)
