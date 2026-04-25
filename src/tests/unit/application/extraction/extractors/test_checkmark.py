import pytest
from deps_extracted_data.model import CheckboxValue

from deps_prototype.application import CheckmarkExtractor

FIRST_ELEMENT: int = 0


@pytest.mark.extraction
def test_extract__ok(key_value_pair_with_checkmark, checkmark_mapping, extracted_data):
    extractor = CheckmarkExtractor()
    extractor.extract([key_value_pair_with_checkmark], checkmark_mapping, extracted_data)

    assert len(extracted_data.fields) == 1
    for field in extracted_data.fields:
        data = field.data
        source_bbox_coordinate = data.source_bbox_coordinates[FIRST_ELEMENT]
        assert len(data.source_bbox_coordinates) == 1
        assert data.confidence == key_value_pair_with_checkmark.confidence

        assert isinstance(data.value, CheckboxValue)
        assert data.value.value == key_value_pair_with_checkmark.value_content
        assert source_bbox_coordinate.bboxes[FIRST_ELEMENT] == key_value_pair_with_checkmark.value.polygon.to_bbox()
        assert source_bbox_coordinate.source_id.value == key_value_pair_with_checkmark.page_id
