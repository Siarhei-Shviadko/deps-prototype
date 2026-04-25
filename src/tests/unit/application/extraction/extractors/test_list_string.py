import pytest

from deps_prototype.application import (
    ListDateExtractor,
    ListEnumExtractor,
    ListNumericExtractor,
    ListStringExtractor,
)

FIRST_ELEMENT: int = 0


@pytest.mark.extraction
@pytest.mark.parametrize(
    "extractor", [ListDateExtractor(), ListEnumExtractor(), ListNumericExtractor(), ListStringExtractor()]
)
def test_extract__ok(extractor, key_value_pair, string_mapping, extracted_data):
    extractor.extract([key_value_pair, key_value_pair], string_mapping, extracted_data)

    assert len(extracted_data.fields) == 1
    for field in extracted_data.fields:
        elements = field.data.elements
        assert len(elements) == 2
        for element in elements:
            source_bbox_coordinate = element.source_bbox_coordinates[FIRST_ELEMENT]
            assert len(element.source_bbox_coordinates) == 1
            assert element.confidence == key_value_pair.confidence
            assert element.value == key_value_pair.value_content
            assert source_bbox_coordinate.bboxes[FIRST_ELEMENT] == key_value_pair.value.polygon.to_bbox()
            assert source_bbox_coordinate.source_id.value == key_value_pair.page_id
