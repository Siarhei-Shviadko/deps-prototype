from deps_extracted_data import ExtractedData, SourceBboxCoordinates

from deps_prototype.domain.model import DataTypeCode, KeyValuePair, Mapping

from .abstract import IKeyValuePairExtractor

__all__ = ["StringExtractor", "EnumExtractor", "DateExtractor", "NumericExtractor"]


class StringExtractor(IKeyValuePairExtractor):
    def extract(self, data: list[KeyValuePair], mapping: Mapping, extracted_data: ExtractedData) -> None:
        for kvp in data:
            if kvp.value is None:
                continue

            extracted_data.add_string(
                self.extracted_field_factory.create_string(
                    field_code=mapping.code,
                    value=kvp.value_content,
                    confidence=kvp.confidence,
                    coordinates=[SourceBboxCoordinates(value=kvp.page_id, bboxes=[kvp.value_polygon.to_bbox()])],
                ),
            )


class EnumExtractor(StringExtractor):
    field_type = DataTypeCode.ENUM


class DateExtractor(StringExtractor):
    field_type = DataTypeCode.DATE


class NumericExtractor(StringExtractor):
    field_type = DataTypeCode.NUMERIC
