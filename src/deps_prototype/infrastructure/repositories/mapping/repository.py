from deps_prototype.domain.model import IMappingRepository, Mapping
from deps_prototype.extras.datasource import Database

from ..mappers import MappingMapper
from .query_factory import MappingQueryFactory

__all__ = ["MappingRepository"]


class MappingRepository(IMappingRepository):
    def __init__(self, database: Database) -> None:
        self.db = database
        self._query_factory = MappingQueryFactory()

    def mapping_by_code(self, code: str, prototype_id: str) -> Mapping | None:
        with self.db.connection() as conn:
            raw_mapping = conn.execute(self._query_factory.select_by_code(code, prototype_id)).mappings().fetchone()

            if raw_mapping:
                return MappingMapper.from_dict(raw_mapping)

    def mappings_of_prototype(self, prototype_id: str) -> list[Mapping]:
        with self.db.connection() as conn:
            raw_mappings = (
                conn.execute(self._query_factory.select_mappings_of_prototype(prototype_id)).mappings().fetchall()
            )

            return [MappingMapper.from_dict(mapping) for mapping in raw_mappings]

    def save(self, mapping: Mapping) -> None:
        with self.db.connection() as conn:
            conn.execute(self._query_factory.insert(), MappingMapper.to_dict(mapping))

    def delete(self, mapping_code: str, prototype_id: str) -> None:
        with self.db.connection() as conn:
            conn.execute(
                self._query_factory.delete(mapping_code=mapping_code, prototype_id=prototype_id),
            )
