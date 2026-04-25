import pytest

from deps_prototype.application import (
    DateExtractor,
    EnumExtractor,
    NumericExtractor,
    StringExtractor,
)

FIRST_ELEMENT: int = 0


@pytest.mark.extraction
@pytest.mark.parametrize(
    "extractor",
    [StringExtractor(), DateExtractor(), EnumExtractor(), NumericExtractor()],
)
def test_extract__ok(extractor, key_value_pair, string_mapping, extracted_data):
    extractor.extract([key_value_pair], string_mapping, extracted_data)

    assert len(extracted_data.fields) == 1
    for field in extracted_data.fields:
        data = field.data
        source_bbox_coordinate = data.source_bbox_coordinates[FIRST_ELEMENT]
        assert len(data.source_bbox_coordinates) == 1
        assert data.confidence == key_value_pair.confidence
        assert data.value == key_value_pair.value_content
        assert source_bbox_coordinate.bboxes[FIRST_ELEMENT] == key_value_pair.value.polygon.to_bbox()
        assert source_bbox_coordinate.source_id.value == key_value_pair.page_id
