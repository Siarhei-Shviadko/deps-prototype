from copy import deepcopy

from deps_prototype.domain.model import (
    IPrototypeRepository,
    Pagination,
    Prototype,
    PrototypeFilter,
    PrototypeSorting,
    PrototypeSortingField,
    SortingDirection,
)

__all__ = ["FakePrototypeRepository"]

FIRST_ELEMENT: int = 0


class FakePrototypeRepository(IPrototypeRepository):
    def __init__(self):
        self._db: dict[tuple[str, str], Prototype] = {}

    def find_by_filter(self, filter_: PrototypeFilter) -> list[Prototype]:
        prototypes = self._apply_filters(list(self._db.values()), filter_)

        if filter_.pagination is not None:
            prototypes = self._apply_pagination(prototypes, filter_.pagination)

        return prototypes

    def prototype_of_id(self, id_: str, tenant_id: str) -> Prototype | None:
        return self._db.get((tenant_id, id_))

    def has_prototype_of_id(self, id_: str, tenant_id: str) -> bool:
        return (tenant_id, id_) in self._db

    def save(self, prototype: Prototype) -> None:
        prototype = deepcopy(prototype)
        prototype.events.clear()
        self._db[(prototype.tenant_id(), prototype.id())] = prototype

    def delete(self, prototype: Prototype) -> None:
        id_ = prototype.id()
        tenant_id = prototype.tenant_id()
        if self.has_prototype_of_id(id_, tenant_id):
            del self._db[(tenant_id, id_)]
            prototype.delete()

    def delete_all(self, prototypes: list[Prototype]) -> None:
        tenant_id = prototypes[FIRST_ELEMENT].tenant_id()
        for prototype in prototypes:
            del self._db[(tenant_id, prototype.id())]
            prototype.delete()

    def get_total_count_by_filter(self, filter_: PrototypeFilter) -> int:
        return len(self._apply_filters(list(self._db.values()), filter_))

    def _apply_filters(self, prototypes: list[Prototype], filter_: PrototypeFilter) -> list[Prototype]:
        prototypes = [prototype for prototype in prototypes if self._accept_value(prototype, filter_)]
        prototypes = self._sort_prototypes(prototypes, filter_.sorting)
        return prototypes

    @staticmethod
    def _accept_value(prototype: Prototype, filter_: PrototypeFilter) -> bool:
        accept = True

        if filter_.tenant_id is not None:
            accept = accept and prototype.tenant_id() == filter_.tenant_id

        if filter_.ids is not None:
            accept = accept and prototype.id() in filter_.ids

        if filter_.languages is not None:
            accept = accept and prototype.language in filter_.languages

        if filter_.engines is not None:
            accept = accept and prototype.engine in filter_.engines

        if filter_.name is not None:
            accept = accept and filter_.name.lower() in prototype.name.lower()

        if (datetime_range := filter_.datetime_range) is not None:
            if datetime_range.start is not None:
                accept = accept and prototype.created_at >= datetime_range.start

            if datetime_range.end is not None:
                accept = accept and prototype.created_at <= datetime_range.end

        return accept

    @staticmethod
    def _apply_pagination(prototypes: list[Prototype], pagination: Pagination) -> list[Prototype]:
        first_prototype_index = (pagination.page - 1) * pagination.per_page

        return (
            prototypes[first_prototype_index : first_prototype_index + pagination.per_page]
            if first_prototype_index < len(prototypes)
            else []
        )

    @staticmethod
    def _sort_prototypes(prototypes: list[Prototype], sorting: PrototypeSorting) -> list[Prototype]:
        def _key(prototype):
            if sorting.field == PrototypeSortingField.ID:
                return prototype.id()
            elif sorting.field == PrototypeSortingField.LANGUAGE:
                return prototype.language
            elif sorting.field == PrototypeSortingField.CREATED_AT:
                return prototype.created_at
            elif sorting.field == PrototypeSortingField.ENGINE:
                return prototype.engine
            else:
                return prototype.name

        return sorted(prototypes, key=_key, reverse=sorting.direction == SortingDirection.DESC)
