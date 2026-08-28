from sqlalchemy import Column, and_, delete, select
from sqlalchemy.dialects.postgresql import insert as _insert
from sqlalchemy.dialects.postgresql.dml import Insert
from sqlalchemy.sql import Delete, Select

from ...tables import mapping_table

__all__ = ["MappingQueryFactory"]


class MappingQueryFactory:
    def __init__(self):
        self._table = mapping_table

    @property
    def columns(self) -> list[Column]:
        return [
            self._table.c.code,
            self._table.c.prototype_id,
            self._table.c.data_type_code,
            self._table.c.mapping_type,
            self._table.c.mapping_keys,
            self._table.c.created_at,
        ]

    def select_mappings_of_prototype(self, prototype_id: str) -> Select:
        return (
            select(*self.columns).where(self._table.c.prototype_id == prototype_id).order_by(self._table.c.created_at)
        )

    def select_by_code(self, mapping_code: str, prototype_id: str) -> Select:
        return select(*self.columns).where(
            and_(self._table.c.prototype_id == prototype_id, self._table.c.code == mapping_code),
        )

    def insert(self) -> Insert:
        query = _insert(self._table).values()
        return query.on_conflict_do_update(
            constraint=self._table.primary_key,
            set_={
                "data_type_code": query.excluded.data_type_code,
                "mapping_type": query.excluded.mapping_type,
                "mapping_keys": query.excluded.mapping_keys,
                "created_at": query.excluded.created_at,
            },
        )

    def delete(self, mapping_code: str, prototype_id: str) -> Delete:
        return delete(self._table).where(
            and_(self._table.c.prototype_id == prototype_id, self._table.c.code == mapping_code),
        )
