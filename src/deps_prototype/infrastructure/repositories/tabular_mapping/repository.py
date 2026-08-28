from sqlalchemy import Column, and_, delete, select
from sqlalchemy.dialects.postgresql import insert

from deps_prototype.domain.model import ITabularMappingRepository, TabularMapping
from deps_prototype.extras.datasource import Database

from ... import tabular_mapping_table
from ..mappers import TabularMappingMapper

__all__ = ["TabularMappingRepository"]


class TabularMappingRepository(ITabularMappingRepository):
    def __init__(self, database: Database) -> None:
        self._db = database
        self._table = tabular_mapping_table

    @property
    def columns(self) -> list[Column]:
        return [
            self._table.c.code,
            self._table.c.prototype_id,
            self._table.c.header_type,
            self._table.c.headers,
            self._table.c.occurrence_index,
            self._table.c.created_at,
        ]

    def get_by_code(self, code: str, prototype_id: str) -> TabularMapping | None:
        query = select(*self.columns).where(
            and_(
                self._table.c.code == code,
                self._table.c.prototype_id == prototype_id,
            ),
        )

        with self._db.connection() as conn:
            raw_tabular_mapping = conn.execute(query).mappings().fetchone()

            if raw_tabular_mapping:
                return TabularMappingMapper.from_dict(raw_tabular_mapping)

        return None

    def mappings_of_prototype(self, prototype_id: str) -> list[TabularMapping]:
        query = select(*self.columns).where(
            self._table.c.prototype_id == prototype_id,
        )

        with self._db.connection() as conn:
            raw_tabular_mappings = conn.execute(query).mappings().fetchall()

            return [TabularMappingMapper.from_dict(raw_tabular_mapping) for raw_tabular_mapping in raw_tabular_mappings]

    def save(self, tabular_mapping: TabularMapping) -> None:
        insert_query = insert(self._table).values()
        update_query = insert_query.on_conflict_do_update(
            constraint=self._table.primary_key,
            set_={
                "header_type": insert_query.excluded.header_type,
                "headers": insert_query.excluded.headers,
                "occurrence_index": insert_query.excluded.occurrence_index,
                "created_at": insert_query.excluded.created_at,
            },
        )

        with self._db.connection() as conn:
            conn.execute(update_query, TabularMappingMapper.to_dict(tabular_mapping))

    def delete(self, code: str, prototype_id: str) -> None:
        query = delete(self._table).where(
            and_(
                self._table.c.code == code,
                self._table.c.prototype_id == prototype_id,
            ),
        )

        with self._db.connection() as conn:
            conn.execute(query)
