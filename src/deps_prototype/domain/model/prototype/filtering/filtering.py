from dataclasses import dataclass, field
from datetime import datetime

from ...shared import DatetimeRange, Pagination, SortingDirection
from .sorting import PrototypeSorting
from .sorting_field import PrototypeSortingField

__all__ = ["PrototypeFilter"]


@dataclass
class PrototypeFilter:
    tenant_id: str | None = None
    ids: list[str] | None = None
    name: str | None = None
    languages: list[str] | None = None
    engines: list[str] | None = None
    pagination: Pagination | None = None
    datetime_range: DatetimeRange | None = None
    sorting: PrototypeSorting = field(default_factory=PrototypeSorting)

    def __init__(
        self,
        tenant_id: str | None = None,
        ids: list[str] | None = None,
        name: str | None = None,
        languages: list[str] | None = None,
        engines: list[str] | None = None,
        page: int | None = None,
        per_page: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        sorting_field: PrototypeSortingField = PrototypeSorting.field,
        sorting_direction: SortingDirection = PrototypeSorting.direction,
    ):
        self.tenant_id = tenant_id
        self.ids = ids
        self.name = name
        self.languages = languages
        self.engines = engines
        self.sorting = PrototypeSorting(field=sorting_field, direction=sorting_direction)

        if page is not None and per_page is not None:
            self.pagination = Pagination(page=page, per_page=per_page)

        if start_date is not None or end_date is not None:
            self.datetime_range = DatetimeRange(start=start_date, end=end_date)
