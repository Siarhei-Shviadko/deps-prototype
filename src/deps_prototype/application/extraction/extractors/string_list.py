from deps_extracted_data import ExtractedData, SourceBboxCoordinates

from deps_prototype.domain.model import DataTypeCode, KeyValuePair, Mapping

from .abstract import IKeyValuePairExtractor

__all__ = ["ListStringExtractor", "ListEnumExtractor", "ListDateExtractor", "ListNumericExtractor"]


class ListStringExtractor(IKeyValuePairExtractor):
    def extract(self, data: list[KeyValuePair], mapping: Mapping, extracted_data: ExtractedData) -> None:
        elements = [
            self.field_data_factory.create_string(
                value=kvp.value_content,
                confidence=kvp.confidence,
                coordinates=[SourceBboxCoordinates(value=kvp.page_id, bboxes=[kvp.value_polygon.to_bbox()])],
            )
            for kvp in data
            if kvp.value
        ]

        if elements:
            extracted_data.add_string_list(
                self.extracted_field_factory.create_string_list(field_code=mapping.code, elements=elements),
            )


class ListEnumExtractor(ListStringExtractor):
    field_type = DataTypeCode.ENUM


class ListDateExtractor(ListStringExtractor):
    field_type = DataTypeCode.DATE


class ListNumericExtractor(ListStringExtractor):
    field_type = DataTypeCode.NUMERIC
