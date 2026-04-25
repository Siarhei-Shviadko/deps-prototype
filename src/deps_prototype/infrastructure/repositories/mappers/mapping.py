from typing import Any, Mapping

from deps_prototype.domain.model import DataTypeCode, EntityId
from deps_prototype.domain.model import Mapping as FieldMapping
from deps_prototype.domain.model import MappingType, UniqueList

from .parse_datetime_string import parse_datetime_string

__all__ = ["MappingMapper"]


class MappingMapper:
    @staticmethod
    def from_dict(raw_mapping: Mapping[str, Any]) -> FieldMapping:
        return FieldMapping(
            code=raw_mapping["code"],
            prototype_id=EntityId(raw_mapping["prototype_id"]),
            data_type=DataTypeCode(raw_mapping["data_type_code"]),
            mapping_type=MappingType(raw_mapping["mapping_type"]),
            keys=UniqueList(raw_mapping["mapping_keys"]),
            created_at=raw_mapping["created_at"],
        )

    @staticmethod
    def from_json_dict(raw_mapping: Mapping[str, Any]) -> FieldMapping:
        created_at = raw_mapping["created_at"]
        if isinstance(created_at, str):
            created_at = parse_datetime_string(created_at)

        return FieldMapping(
            code=raw_mapping["code"],
            prototype_id=EntityId(raw_mapping["prototype_id"]),
            data_type=DataTypeCode(raw_mapping["data_type_code"]),
            mapping_type=MappingType(raw_mapping["mapping_type"]),
            keys=UniqueList(raw_mapping["mapping_keys"]),
            created_at=created_at,
        )

    @staticmethod
    def to_dict(mapping: FieldMapping) -> dict[str, Any]:
        return {
            "code": mapping.code,
            "prototype_id": mapping.prototype_id(),
            "data_type_code": mapping.data_type.value,
            "mapping_type": mapping.mapping_type,
            "mapping_keys": mapping.keys,
            "created_at": mapping.created_at,
        }
