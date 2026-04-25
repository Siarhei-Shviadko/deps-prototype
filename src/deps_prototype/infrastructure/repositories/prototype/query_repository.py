from sqlalchemy import Column, and_, func, select, text

from deps_prototype.domain.model import IQueryPrototypeRepository, PrototypeWithMappings
from deps_prototype.extras.datasource import Database

from ...tables import mapping_table, prototype_table, tabular_mapping_table
from .mappers import PrototypeWithMappingsMapper

__all__ = ["QueryPrototypeRepository"]


class QueryPrototypeRepository(IQueryPrototypeRepository):
    def __init__(self, database: Database) -> None:
        self._db = database

    @property
    def prototype_columns(self) -> list[Column]:
        return [
            prototype_table.c.id,
            prototype_table.c.tenant_id,
            prototype_table.c.name,
            prototype_table.c.engine,
            prototype_table.c.language,
            prototype_table.c.description,
            prototype_table.c.created_at,
            prototype_table.c.field_names,
        ]

    @property
    def mapping_columns(self) -> list[Column]:
        return [
            mapping_table.c.code,
            mapping_table.c.prototype_id,
            mapping_table.c.data_type_code,
            mapping_table.c.mapping_type,
            mapping_table.c.mapping_keys,
            mapping_table.c.created_at,
        ]

    @property
    def tabular_mapping_columns(self) -> list[Column]:
        return [
            tabular_mapping_table.c.code,
            tabular_mapping_table.c.prototype_id,
            tabular_mapping_table.c.header_type,
            tabular_mapping_table.c.headers,
            tabular_mapping_table.c.occurrence_index,
            tabular_mapping_table.c.created_at,
        ]

    def find_prototype_with_mappings(self, id_: str, tenant_id: str) -> PrototypeWithMappings | None:
        mapping_cte = (
            select(
                [
                    func.coalesce(
                        func.json_agg(
                            func.row_to_json(text(f"{mapping_table.name}.*")),
                        ),
                        text("'[]'::json"),
                    ).label("mappings"),
                ],
            )
            .where(mapping_table.c.prototype_id == id_)
            .cte("prototype_mappings")
        )

        tabular_mapping_cte = (
            select(
                [
                    func.coalesce(
                        func.json_agg(
                            func.row_to_json(text(f"{tabular_mapping_table.name}.*")),
                        ),
                        text("'[]'::json"),
                    ).label("tabular_mappings"),
                ],
            )
            .where(tabular_mapping_table.c.prototype_id == id_)
            .cte("prototype_tabular_mappings")
        )

        query = select(
            [
                *self.prototype_columns,
                mapping_cte,
                tabular_mapping_cte,
            ],
        ).where(
            and_(
                prototype_table.c.id == id_,
                prototype_table.c.tenant_id == tenant_id,
            ),
        )

        with self._db.connection() as conn:
            row = conn.execute(query).fetchone()

        return PrototypeWithMappingsMapper.from_dict(row) if row else None
