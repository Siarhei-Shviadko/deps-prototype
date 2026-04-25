from deps_extracted_data import ExtractedData, SourceBboxCoordinates
from deps_extracted_data.model import CheckboxValue

from deps_prototype.domain.model import DataTypeCode, KeyValuePair, Mapping

from .abstract import IKeyValuePairExtractor

__all__ = ["CheckmarkExtractor"]


class CheckmarkExtractor(IKeyValuePairExtractor):
    field_type = DataTypeCode.CHECKMARK

    def extract(self, data: list[KeyValuePair], mapping: Mapping, extracted_data: ExtractedData) -> None:
        for kvp in data:
            if kvp.value is None:
                continue

            try:
                checkbox_value = CheckboxValue(kvp.value.content)
            except ValueError:
                checkbox_value = CheckboxValue.CHECKED if kvp.value.content else CheckboxValue.UNCHECKED

            extracted_data.add_checkbox(
                self.extracted_field_factory.create_checkbox(
                    field_code=mapping.code,
                    value=checkbox_value,
                    confidence=kvp.confidence,
                    coordinates=[SourceBboxCoordinates(value=kvp.page_id, bboxes=[kvp.value_polygon.to_bbox()])],
                ),
            )
