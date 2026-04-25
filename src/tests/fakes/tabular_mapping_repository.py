from deps_prototype.domain.model import ITabularMappingRepository, TabularMapping

__all__ = ["FakeTabularMappingRepository"]


class FakeTabularMappingRepository(ITabularMappingRepository):
    def __init__(self):
        self._db: dict[tuple[str, str], TabularMapping] = {}

    def get_by_code(self, code: str, prototype_id: str) -> TabularMapping | None:
        return self._db.get((code, prototype_id))

    def mappings_of_prototype(self, prototype_id: str) -> list[TabularMapping]:
        return [mapping for mapping in self._db.values() if mapping.prototype_id() == prototype_id]

    def save(self, tabular_mapping: TabularMapping) -> None:
        self._db[(tabular_mapping.code, tabular_mapping.prototype_id())] = tabular_mapping

    def delete(self, code: str, prototype_id: str) -> None:
        self._db.pop((code, prototype_id), None)

    def get_all(self) -> list[TabularMapping]:
        return list(self._db.values())
