from typing import Any, Mapping

from deps_prototype.domain.model import (
    EntityId,
    Prototype,
    PrototypeWithMappings,
    TenantId,
)

from ..mappers import MappingMapper, TabularMappingMapper

__all__ = ["PrototypeMapper", "PrototypeWithMappingsMapper"]


class PrototypeMapper:
    @staticmethod
    def to_dict(prototype: Prototype) -> dict[str, Any]:
        return {
            "id": prototype.id(),
            "tenant_id": prototype.tenant_id(),
            "name": prototype.name,
            "language": prototype.language,
            "engine": prototype.engine,
            "description": prototype.description,
            "created_at": prototype.created_at,
        }

    @staticmethod
    def from_dict(raw_prototype: Mapping) -> Prototype:
        return Prototype(
            id_=EntityId(raw_prototype["id"]),
            tenant_id=TenantId(raw_prototype["tenant_id"]),
            name=raw_prototype["name"],
            language=raw_prototype["language"],
            engine=raw_prototype["engine"],
            description=raw_prototype["description"],
            created_at=raw_prototype["created_at"],
        )


class PrototypeWithMappingsMapper:
    @staticmethod
    def to_dict(prototype_with_mappings: PrototypeWithMappings) -> dict[str, Any]:
        return {
            **PrototypeMapper.to_dict(prototype_with_mappings["prototype"]),
            "mappings": [MappingMapper.to_dict(mapping) for mapping in prototype_with_mappings["mappings"]],
            "tabular_mappings": [
                TabularMappingMapper.to_dict(tabular_mapping)
                for tabular_mapping in prototype_with_mappings["tabular_mappings"]
            ],
        }

    @staticmethod
    def from_dict(raw_prototype_with_mappings: Mapping) -> PrototypeWithMappings:
        return PrototypeWithMappings(
            prototype=Prototype(
                id_=EntityId(raw_prototype_with_mappings["id"]),
                tenant_id=TenantId(raw_prototype_with_mappings["tenant_id"]),
                name=raw_prototype_with_mappings["name"],
                language=raw_prototype_with_mappings["language"],
                engine=raw_prototype_with_mappings["engine"],
                description=raw_prototype_with_mappings["description"],
                created_at=raw_prototype_with_mappings["created_at"],
            ),
            mappings=[MappingMapper.from_json_dict(mapping) for mapping in raw_prototype_with_mappings["mappings"]],
            tabular_mappings=[
                TabularMappingMapper.from_json_dict(tabular_mapping)
                for tabular_mapping in raw_prototype_with_mappings["tabular_mappings"]
            ],
        )
