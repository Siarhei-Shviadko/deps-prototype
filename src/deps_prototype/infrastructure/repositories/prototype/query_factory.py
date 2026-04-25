from sqlalchemy import Column, and_, asc, delete, desc, func, insert, select, update
from sqlalchemy.sql import Delete, Insert, Select, Update
from sqlalchemy.sql.expression import UnaryExpression

from deps_prototype.domain.model import (
    PrototypeFilter,
    PrototypeSorting,
    PrototypeSortingField,
    SortingDirection,
)

from ...tables import prototype_table


class PrototypeQueryFactory:
    def __init__(self) -> None:
        self._prototype_table_schema = prototype_table

    @property
    def prototype_columns(self) -> list[Column]:
        return [
            self._prototype_table_schema.c.id,
            self._prototype_table_schema.c.tenant_id,
            self._prototype_table_schema.c.name,
            self._prototype_table_schema.c.engine,
            self._prototype_table_schema.c.language,
            self._prototype_table_schema.c.description,
            self._prototype_table_schema.c.created_at,
            self._prototype_table_schema.c.field_names,
        ]

    @property
    def prototype_id_column(self) -> list[Column]:
        return [self._prototype_table_schema.c.id]

    def select_prototype_by(self, prototype_id: str, tenant_id: str) -> Select:
        return select(self.prototype_columns).where(
            and_(
                prototype_table.c.tenant_id == tenant_id,
                prototype_table.c.id == prototype_id,
            ),
        )

    def select_prototype_id_by(self, prototype_id: str, tenant_id: str) -> Select:
        return select(self.prototype_id_column).where(
            and_(
                prototype_table.c.tenant_id == tenant_id,
                prototype_table.c.id == prototype_id,
            ),
        )

    def update_prototype_with(self, prototype: dict[str, str]) -> Update:
        return update(self._prototype_table_schema).where(prototype_table.c.id == prototype["id"]).values(**prototype)

    def insert_prototype(self) -> Insert:
        return insert(self._prototype_table_schema)

    def delete_prototype_with(self, prototype_id: str, tenant_id: str) -> Delete:
        return delete(self._prototype_table_schema).where(
            and_(
                prototype_table.c.id == prototype_id,
                prototype_table.c.tenant_id == tenant_id,
            ),
        )

    def delete_prototype_batch_with(self, prototype_ids: set[str], tenant_id: str) -> Delete:
        return delete(self._prototype_table_schema).where(
            and_(
                prototype_table.c.tenant_id == tenant_id,
                prototype_table.c.id.in_(prototype_ids),
            ),
        )

    def apply_filter_and_sort(self, filter_: PrototypeFilter) -> Select:
        filter_query = self._filter_prototype(filter_)
        sort_expression = self._sort_prototype(filter_.sorting)
        return filter_query.order_by(sort_expression)

    def _filter_prototype(self, filter_: PrototypeFilter) -> Select:  # noqa: WPS231
        query = select(self.prototype_columns)

        if filter_.tenant_id is not None:
            query = query.where(prototype_table.c.tenant_id == filter_.tenant_id)

        if filter_.ids is not None:
            query = query.where(prototype_table.c.id.in_(filter_.ids))

        if filter_.languages is not None:
            query = query.where(prototype_table.c.language.in_(filter_.languages))

        if filter_.engines is not None:
            query = query.where(prototype_table.c.engine.in_(filter_.engines))

        if filter_.name is not None:
            query = query.where(func.lower(prototype_table.c.name).contains(filter_.name.lower()))

        if (datetime_range := filter_.datetime_range) is not None:
            if datetime_range.start is not None and datetime_range.end is not None:
                query = query.where(prototype_table.c.created_at.between(datetime_range.start, datetime_range.end))

            elif datetime_range.start is not None:
                query = query.where(prototype_table.c.created_at >= datetime_range.start)

            elif datetime_range.end is not None:
                query = query.where(prototype_table.c.created_at <= datetime_range.end)

        return query

    @staticmethod
    def _sort_prototype(sorting: PrototypeSorting) -> UnaryExpression:
        sort_options = {
            PrototypeSortingField.ID: prototype_table.c.id,
            PrototypeSortingField.LANGUAGE: prototype_table.c.language,
            PrototypeSortingField.CREATED_AT: prototype_table.c.created_at,
            PrototypeSortingField.ENGINE: prototype_table.c.engine,
        }
        sort_query = sort_options.get(sorting.field, prototype_table.c.name)
        if sorting.direction == SortingDirection.DESC:
            sort_query = desc(sort_query)
        else:
            sort_query = asc(sort_query)

        return sort_query
