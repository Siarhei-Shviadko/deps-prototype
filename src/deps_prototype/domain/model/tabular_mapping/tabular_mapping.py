import datetime as dt

from deps_prototype.domain.model import (
    CollectionLengthCheck,
    DocumentLayout,
    EntityId,
    Guard,
    ImmutableCheck,
)

from .allocators import (
    AllocatedTable,
    ColumnOrientedTabularAllocator,
    RowOrientedTabularAllocator,
    TabularAllocator,
)
from .header import Header
from .header_type import HeaderType
from .raw_header import RawHeader

__all__ = ["TabularMapping"]


class TabularMapping:
    code = Guard[str](str, ImmutableCheck())
    prototype_id = Guard[EntityId](EntityId, ImmutableCheck())
    header_type = Guard[HeaderType](HeaderType)
    headers = Guard[list[Header]](
        list,
        CollectionLengthCheck(min_length=1),
    )
    occurrence_index = Guard[int](int)
    created_at = Guard[dt.datetime](dt.datetime, ImmutableCheck())

    def __init__(
        self,
        code: str,
        prototype_id: EntityId,
        header_type: HeaderType,
        headers: list[Header],
        occurrence_index: int,
        created_at: dt.datetime | None = None,
    ) -> None:
        self.code = code
        self.prototype_id = prototype_id
        self.header_type = header_type
        self.headers = headers
        self.occurrence_index = occurrence_index
        self.created_at = created_at or dt.datetime.now(tz=dt.timezone.utc)

        self._allocators: dict[HeaderType, type[TabularAllocator]] = {
            HeaderType.ROWS: RowOrientedTabularAllocator,
            HeaderType.COLUMNS: ColumnOrientedTabularAllocator,
        }

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.code = },",
                f"{self.prototype_id = },",
                f"{self.header_type = },",
                f"{self.occurrence_index = },",
                f"{self.created_at = },",
            ),
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.code == other.code

    def update(
        self,
        header_type: HeaderType | None = None,
        headers: list[RawHeader] | None = None,
        occurrence_index: int | None = None,
    ) -> None:
        if header_type is not None:
            self.header_type = header_type
        if headers is not None:
            self.headers = [Header(name=header["name"], aliases=header["aliases"]) for header in headers]
        if occurrence_index is not None:
            self.occurrence_index = occurrence_index

    @property
    def allocator(self) -> type[TabularAllocator]:
        return self._allocators[self.header_type]

    def search_data(self, document_layout: DocumentLayout) -> AllocatedTable | None:
        return self.allocator(
            document_layout=document_layout,
            headers=self.headers,
            occurrence_index=self.occurrence_index,
            header_type=self.header_type,
        ).allocate()
