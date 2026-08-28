from typing import Iterable

from sqlalchemy import Column, and_, delete, select
from sqlalchemy.dialects.postgresql import insert as _insert
from sqlalchemy.dialects.postgresql.dml import Insert
from sqlalchemy.sql import Delete, Select

from ...tables import reference_layout_table

__all__ = ["ReferenceLayoutQueryFactory"]


class ReferenceLayoutQueryFactory:
    def __init__(self):
        self._reference_layout_schema = reference_layout_table

    @property
    def reference_layout_columns(self) -> list[Column]:
        return [
            self._reference_layout_schema.c.id,
            self._reference_layout_schema.c.prototype_id,
            self._reference_layout_schema.c.state,
            self._reference_layout_schema.c.blob_name,
            self._reference_layout_schema.c.title,
        ]

    def select_reference_layouts_by(self, ids: list[str], prototype_id: str) -> Select:
        return select(*self.reference_layout_columns).where(
            and_(
                self._reference_layout_schema.c.prototype_id == prototype_id,
                self._reference_layout_schema.c.id.in_(ids),
            ),
        )

    def select_reference_layouts_of_prototype(self, prototype_id: str) -> Select:
        return select(*self.reference_layout_columns).where(
            self._reference_layout_schema.c.prototype_id == prototype_id,
        )

    def select_reference_layout_by(self, reference_layout_id: str, prototype_id: str) -> Select:
        return select(*self.reference_layout_columns).where(
            and_(
                self._reference_layout_schema.c.prototype_id == prototype_id,
                self._reference_layout_schema.c.id == reference_layout_id,
            ),
        )

    def insert(self) -> Insert:
        query = _insert(self._reference_layout_schema).values()
        return query.on_conflict_do_update(
            constraint=self._reference_layout_schema.primary_key,
            set_=dict(query.excluded),
        )

    def delete(self, id_: str, prototype_id: str) -> Delete:
        return delete(self._reference_layout_schema).where(
            and_(
                self._reference_layout_schema.c.prototype_id == prototype_id,
                self._reference_layout_schema.c.id == id_,
            ),
        )

    def delete_all(self, ids: Iterable[str], prototype_id: str) -> Delete:
        return delete(self._reference_layout_schema).where(
            and_(
                self._reference_layout_schema.c.prototype_id == prototype_id,
                self._reference_layout_schema.c.id.in_(ids),
            ),
        )
