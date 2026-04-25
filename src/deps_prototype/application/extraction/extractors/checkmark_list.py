from deps_extracted_data import ExtractedData, SourceBboxCoordinates
from deps_extracted_data.model import CheckboxValue

from deps_prototype.domain.model import DataTypeCode, KeyValuePair, Mapping

from .abstract import IKeyValuePairExtractor

__all__ = ["ListCheckmarkExtractor"]


class ListCheckmarkExtractor(IKeyValuePairExtractor):
    field_type = DataTypeCode.CHECKMARK

    def extract(self, data: list[KeyValuePair], mapping: Mapping, extracted_data: ExtractedData) -> None:
        elements = []
        for kvp in data:
            if kvp.value:
                bboxes = [kvp.value_polygon.to_bbox()]
                try:
                    checkbox_value = CheckboxValue(kvp.value.content)
                except ValueError:
                    checkbox_value = CheckboxValue.CHECKED if kvp.value.content else CheckboxValue.UNCHECKED
            else:
                bboxes = []
                checkbox_value = CheckboxValue.UNRECOGNIZED

            elements.append(
                self.field_data_factory.create_checkbox(
                    value=checkbox_value,
                    confidence=kvp.confidence,
                    coordinates=[SourceBboxCoordinates(value=kvp.page_id, bboxes=bboxes)],
                ),
            )

        if elements:
            extracted_data.add_checkbox_list(
                self.extracted_field_factory.create_checkbox_list(field_code=mapping.code, elements=elements),
            )
