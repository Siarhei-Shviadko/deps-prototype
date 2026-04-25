from deps_prototype.domain.model import IMappingRepository, Mapping

__all__ = ["FakeMappingRepository"]


class FakeMappingRepository(IMappingRepository):
    def __init__(self):
        self._db: dict[tuple[str, str], Mapping] = {}

    def mapping_by_code(self, code: str, prototype_id: str) -> Mapping | None:
        return self._db.get((code, prototype_id))

    def mappings_of_prototype(self, prototype_id: str) -> list[Mapping]:
        return [field for field in self._db.values() if field.prototype_id() == prototype_id]

    def save(self, mapping: Mapping) -> None:
        self._db[(mapping.code, mapping.prototype_id())] = mapping

    def delete(self, mapping_code: str, prototype_id: str) -> None:
        if (mapping_code, prototype_id) in self._db:
            del self._db[(mapping_code, prototype_id)]
