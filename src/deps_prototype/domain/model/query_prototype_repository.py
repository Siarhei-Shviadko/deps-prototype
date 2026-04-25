from .prototype_with_mappings import PrototypeWithMappings

__all__ = ["IQueryPrototypeRepository"]


class IQueryPrototypeRepository:
    def find_prototype_with_mappings(self, id_: str, tenant_id: str) -> PrototypeWithMappings | None:
        pass
