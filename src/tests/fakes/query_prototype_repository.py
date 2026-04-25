from deps_prototype.domain.model import IQueryPrototypeRepository, PrototypeWithMappings

__all__ = ["FakeQueryPrototypeRepository"]


class FakeQueryPrototypeRepository(IQueryPrototypeRepository):
    def __init__(self):
        self._db: dict[tuple[str, str], PrototypeWithMappings] = {}

    def find_prototype_with_mappings(self, id_: str, tenant_id: str) -> PrototypeWithMappings | None:
        return self._db.get((id_, tenant_id))
