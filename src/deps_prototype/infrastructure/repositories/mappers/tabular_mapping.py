from typing import Any, Mapping

from deps_prototype.domain.model import EntityId, Header, HeaderType, TabularMapping

from .parse_datetime_string import parse_datetime_string

__all__ = ["TabularMappingMapper"]


class TabularMappingMapper:
    @staticmethod
    def from_dict(raw_mapping: Mapping[str, Any]) -> TabularMapping:
        return TabularMapping(
            code=raw_mapping["code"],
            prototype_id=EntityId(raw_mapping["prototype_id"]),
            header_type=HeaderType(raw_mapping["header_type"]),
            headers=[
                Header(
                    name=header["name"],
                    aliases=set(header["aliases"]),
                )
                for header in raw_mapping["headers"]
            ],
            occurrence_index=raw_mapping["occurrence_index"],
            created_at=raw_mapping["created_at"],
        )

    @staticmethod
    def from_json_dict(raw_mapping: Mapping[str, Any]) -> TabularMapping:
        created_at = raw_mapping["created_at"]
        if isinstance(created_at, str):
            created_at = parse_datetime_string(created_at)

        return TabularMapping(
            code=raw_mapping["code"],
            prototype_id=EntityId(raw_mapping["prototype_id"]),
            header_type=HeaderType(raw_mapping["header_type"]),
            headers=[
                Header(
                    name=header["name"],
                    aliases=set(header["aliases"]),
                )
                for header in raw_mapping["headers"]
            ],
            occurrence_index=raw_mapping["occurrence_index"],
            created_at=created_at,
        )

    @staticmethod
    def to_dict(tabular_mapping: TabularMapping) -> dict[str, Any]:
        return {
            "code": tabular_mapping.code,
            "prototype_id": tabular_mapping.prototype_id(),
            "header_type": tabular_mapping.header_type.value,
            "headers": [{"name": header.name, "aliases": list(header.aliases)} for header in tabular_mapping.headers],
            "occurrence_index": tabular_mapping.occurrence_index,
            "created_at": tabular_mapping.created_at,
        }
