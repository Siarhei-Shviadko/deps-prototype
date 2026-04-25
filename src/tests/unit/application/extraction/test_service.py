from random import randint

import pytest
from deps_extracted_data import ExtractedData

from deps_prototype.application import (
    DateExtractor,
    EnumExtractor,
    ExtractionService,
    ListDateExtractor,
    ListEnumExtractor,
    ListNumericExtractor,
    ListStringExtractor,
    NumericExtractor,
    StringExtractor,
)
from deps_prototype.domain.exceptions import PrototypeNotFound
from deps_prototype.domain.model import (
    DataTypeCode,
    DocumentLayout,
    Mapping,
    MappingType,
    Prototype,
    UniqueList,
)
from tests.factories import MappingFactory


@pytest.mark.extraction
def test_extract__no_prototype__not_found_error(extraction_service: ExtractionService, prototype):
    with pytest.raises(PrototypeNotFound):
        extraction_service.extract(
            document_id=randint(1, 40),
            prototype_id=prototype.id(),
            tenant_id=prototype.tenant_id(),
            language=prototype.language,
            engine=prototype.engine,
        )


@pytest.mark.extraction
def test_extract__prototype_no_mappings__no_error_extracted_data_not_saved(
    extraction_proxy_mock,
    saved_prototype: Prototype,
    extraction_service: ExtractionService,
):
    extraction_service.extract(
        document_id=randint(1, 40),
        prototype_id=saved_prototype.id(),
        tenant_id=saved_prototype.tenant_id(),
        language=saved_prototype.language,
        engine=saved_prototype.engine,
    )

    extraction_proxy_mock.save_extracted_data.assert_not_called()


@pytest.mark.extraction
def test_evaluate__prototype_fields__extracted_data_saved(
    extraction_proxy_mock,
    parsing_proxy_mock,
    saved_prototype: Prototype,
    saved_mappings: list[Mapping],
    document_layout: DocumentLayout,
    extraction_service: ExtractionService,
    extracted_data: ExtractedData,
):
    document_id = randint(1, 40)
    parsing_proxy_mock.get_document_layout.return_value = document_layout

    extraction_service.extract(
        document_id=document_id,
        prototype_id=saved_prototype.id(),
        tenant_id=saved_prototype.tenant_id(),
        language=saved_prototype.language,
        engine=saved_prototype.engine,
    )

    parsing_proxy_mock.get_document_layout.assert_called_once_with(
        document_id=str(document_id),
        language=saved_prototype.language,
        parsing_type=saved_prototype.engine,
        parsing_features=extraction_service.PARSING_FEATURES,
    )
    extraction_proxy_mock.save_extracted_data.assert_called_once()
    assert extraction_proxy_mock.save_extracted_data.call_args.kwargs["extracted_data"].fields


@pytest.mark.extraction
@pytest.mark.parametrize(
    "data_type,mapping_type,expected_extractor_type",
    [
        (DataTypeCode.STRING, MappingType.ONE_TO_ONE, StringExtractor),
        (DataTypeCode.NUMERIC, MappingType.ONE_TO_ONE, NumericExtractor),
        (DataTypeCode.ENUM, MappingType.ONE_TO_ONE, EnumExtractor),
        (DataTypeCode.DATE, MappingType.ONE_TO_ONE, DateExtractor),
        (DataTypeCode.STRING, MappingType.ONE_TO_MANY, ListStringExtractor),
        (DataTypeCode.NUMERIC, MappingType.ONE_TO_MANY, ListNumericExtractor),
        (DataTypeCode.ENUM, MappingType.ONE_TO_MANY, ListEnumExtractor),
        (DataTypeCode.DATE, MappingType.ONE_TO_MANY, ListDateExtractor),
    ],
)
def test_choose_extractor__ok(data_type, mapping_type, expected_extractor_type, extraction_service):
    field = MappingFactory(
        data_type=data_type,
        mapping_type=mapping_type,
    )
    actual_extractor = extraction_service._choose_extractor(field)

    assert isinstance(actual_extractor, expected_extractor_type)


@pytest.mark.extraction
def test_perform_extraction__no_extractor__ok(
    extraction_service,
    document_layout,
    extracted_data,
    mocker,
):
    mapping = mocker.Mock(Mapping)
    type(mapping).data_type = mocker.PropertyMock(return_value="unexpected field type")
    type(mapping).mapping_type = mocker.PropertyMock(return_value="unexpected field type")

    extraction_service._perform_extraction(mapping, document_layout, extracted_data)

    assert not extracted_data.fields


@pytest.mark.extraction
def test_perform_extraction__no_data__ok(extraction_service, document_layout, extracted_data):
    mapping: Mapping = MappingFactory(
        data_type=DataTypeCode.DATE,
        mapping_type=MappingType.ONE_TO_MANY,
        keys=UniqueList(["not existed keys"]),
    )

    extraction_service._perform_extraction(mapping, document_layout, extracted_data)

    assert not extracted_data.fields


@pytest.mark.extraction
def test_perform_extraction__kvp_value_is_none__one_to_many__ok(extraction_service, document_layout, extracted_data):
    mapping: Mapping = MappingFactory(
        data_type=DataTypeCode.DATE,
        mapping_type=MappingType.ONE_TO_MANY,
        keys=UniqueList(["Shipment Terms"]),
    )

    extraction_service._perform_extraction(mapping, document_layout, extracted_data)

    assert not extracted_data.fields


@pytest.mark.extraction
def test_perform_extraction__kvp_value_is_none__one_to_one__ok(extraction_service, document_layout, extracted_data):
    mapping: Mapping = MappingFactory(
        data_type=DataTypeCode.DATE,
        mapping_type=MappingType.ONE_TO_ONE,
        keys=UniqueList(["Shipment Terms"]),
    )

    extraction_service._perform_extraction(mapping, document_layout, extracted_data)

    assert not extracted_data.fields
