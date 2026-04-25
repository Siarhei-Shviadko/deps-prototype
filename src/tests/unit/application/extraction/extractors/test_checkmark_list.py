import pytest
from deps_extracted_data.model import CheckboxValue

from deps_prototype.application import ListCheckmarkExtractor

FIRST_ELEMENT: int = 0


@pytest.mark.extraction
def test_extract__ok(key_value_pair_with_checkmark, checkmark_mapping, extracted_data):
    extractor = ListCheckmarkExtractor()
    extractor.extract([key_value_pair_with_checkmark, key_value_pair_with_checkmark], checkmark_mapping, extracted_data)

    assert len(extracted_data.fields) == 1
    for field in extracted_data.fields:
        elements = field.data.elements
        assert len(elements) == 2
        for element in elements:
            source_bbox_coordinate = element.source_bbox_coordinates[FIRST_ELEMENT]
            assert len(element.source_bbox_coordinates) == 1
            assert element.confidence == key_value_pair_with_checkmark.confidence

            assert isinstance(element.value, CheckboxValue)
            assert element.value.value == key_value_pair_with_checkmark.value_content
            assert source_bbox_coordinate.bboxes[FIRST_ELEMENT] == key_value_pair_with_checkmark.value.polygon.to_bbox()
            assert source_bbox_coordinate.source_id.value == key_value_pair_with_checkmark.page_id
