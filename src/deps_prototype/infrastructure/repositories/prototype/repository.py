from psycopg2.errorcodes import UNIQUE_VIOLATION
from sqlalchemy.engine.base import Connection
from sqlalchemy.exc import IntegrityError

from deps_prototype.domain.exceptions import InvariantViolation
from deps_prototype.domain.model import IPrototypeRepository, Prototype, PrototypeFilter
from deps_prototype.extras.datasource import Database

from .mappers import PrototypeMapper
from .query_factory import PrototypeQueryFactory

__all__ = ["PrototypeRepository"]

FIRST_ELEMENT: int = 0


class PrototypeRepository(IPrototypeRepository):
    def __init__(self, database: Database) -> None:
        self.db = database
        self._query_factory = PrototypeQueryFactory()

    def prototype_of_id(self, id_: str, tenant_id: str) -> Prototype | None:
        with self.db.connection() as conn:
            if row := conn.execute(self._query_factory.select_prototype_by(id_, tenant_id)).fetchone():
                return PrototypeMapper.from_dict(row)
            return None

    def has_prototype_of_id(self, id_: str, tenant_id: str) -> bool:
        with self.db.connection() as conn:
            return bool(self._find_prototype_id(conn, id_, tenant_id))

    def save(self, prototype: Prototype) -> None:
        raw_prototype = PrototypeMapper.to_dict(prototype)
        try:
            with self.db.connection() as conn:
                if self._find_prototype_id(conn, raw_prototype["id"], raw_prototype["tenant_id"]):
                    self._update(conn, raw_prototype)
                else:
                    self._store(conn, raw_prototype)
        except IntegrityError as err:
            if err.orig.pgcode == UNIQUE_VIOLATION:
                raise InvariantViolation(f"Prototype with `{prototype.name}` name already exists")

            raise

    def delete(self, prototype: Prototype) -> None:
        prototype_id = prototype.id()
        with self.db.connection() as conn:
            conn.execute(self._query_factory.delete_prototype_with(prototype_id, prototype.tenant_id()))
            prototype.delete()

    def delete_all(self, prototypes: list[Prototype]) -> None:
        tenant_id = prototypes[FIRST_ELEMENT].tenant_id()
        prototype_ids_to_be_removed = {prototype.id() for prototype in prototypes}
        with self.db.connection() as conn:
            conn.execute(self._query_factory.delete_prototype_batch_with(prototype_ids_to_be_removed, tenant_id))

        for prototype in prototypes:
            prototype.delete()

    def get_total_count_by_filter(self, filter_: PrototypeFilter) -> int:
        query = self._query_factory.apply_filter_and_sort(filter_)

        with self.db.connection() as conn:
            result = conn.execute(query.alias().count()).fetchone()

        return 0 if result is None else result[0]

    def find_by_filter(self, filter_: PrototypeFilter) -> list[Prototype]:
        query = self._query_factory.apply_filter_and_sort(filter_)

        if filter_.pagination is not None:
            query = query.offset((filter_.pagination.page - 1) * filter_.pagination.per_page).limit(
                filter_.pagination.per_page,
            )

        with self.db.connection() as conn:
            prototypes = conn.execute(query).fetchall()

        return [PrototypeMapper.from_dict(prototype) for prototype in prototypes]

    def _store(self, conn: Connection, raw_prototype: dict[str, str]) -> None:
        conn.execute(self._query_factory.insert_prototype(), raw_prototype)

    def _update(self, conn: Connection, raw_prototype: dict[str, str]) -> None:
        conn.execute(self._query_factory.update_prototype_with(raw_prototype))

    def _find_prototype_id(self, conn: Connection, prototype_id: str, tenant_id: str) -> str | None:
        return conn.execute(self._query_factory.select_prototype_id_by(prototype_id, tenant_id)).fetchone()
