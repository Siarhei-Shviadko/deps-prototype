from deps_prototype.domain.model import IReferenceLayoutRepository, ReferenceLayout
from deps_prototype.extras.datasource import Database

from .mappers import ReferenceLayoutMapper
from .query_factory import ReferenceLayoutQueryFactory

__all__ = ["ReferenceLayoutRepository"]


class ReferenceLayoutRepository(IReferenceLayoutRepository):
    def __init__(self, database: Database) -> None:
        self.db = database
        self._query_factory = ReferenceLayoutQueryFactory()

    def save(self, reference_layout: ReferenceLayout) -> None:
        with self.db.connection() as conn:
            conn.execute(self._query_factory.insert(), **ReferenceLayoutMapper.to_dict(reference_layout))

    def reference_layout_of_id(self, id_: str, prototype_id: str) -> ReferenceLayout | None:
        with self.db.connection() as conn:
            raw_reference_layout = conn.execute(
                self._query_factory.select_reference_layout_by(id_, prototype_id),
            ).fetchone()
            if raw_reference_layout:
                return ReferenceLayoutMapper.from_dict(raw_reference_layout)

    def reference_layouts_of_ids(self, ids: list[str], prototype_id: str) -> list[ReferenceLayout]:
        with self.db.connection() as conn:
            raw_reference_layouts = conn.execute(
                self._query_factory.select_reference_layouts_by(ids, prototype_id),
            ).fetchall()
            return [ReferenceLayoutMapper.from_dict(reference_layout) for reference_layout in raw_reference_layouts]

    def reference_layouts_of_prototype(self, prototype_id: str) -> list[ReferenceLayout]:
        with self.db.connection() as conn:
            raw_reference_layouts = conn.execute(
                self._query_factory.select_reference_layouts_of_prototype(prototype_id),
            ).fetchall()
            return [ReferenceLayoutMapper.from_dict(reference_layout) for reference_layout in raw_reference_layouts]

    def delete(self, reference_layout: ReferenceLayout) -> None:
        with self.db.connection() as conn:
            conn.execute(
                self._query_factory.delete(reference_layout.id(), reference_layout.prototype_id()),
            )

        reference_layout.delete()

    def delete_all(self, reference_layouts: list[ReferenceLayout]) -> None:
        prototype_id = reference_layouts[0].prototype_id()

        with self.db.connection() as conn:
            conn.execute(
                self._query_factory.delete_all(
                    [reference_layout.id() for reference_layout in reference_layouts],
                    prototype_id,
                ),
            )

        for reference_layout in reference_layouts:
            reference_layout.delete()
