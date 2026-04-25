import datetime as dt

from ...exceptions import InvariantViolation
from ..shared import (
    DocumentLayout,
    EntityId,
    Guard,
    ImmutableCheck,
    KeyValuePair,
    TrimmedCollectionItemFormatCheck,
    UniqueList,
)
from .allocators import Allocator, OneToManyAllocator, OneToOneAllocator
from .data_type import DataTypeCode
from .mapping_type import MappingType

__all__ = ["Mapping"]


class Mapping:
    code = Guard[str](str, ImmutableCheck())
    prototype_id = Guard[EntityId](EntityId, ImmutableCheck())
    data_type = Guard[DataTypeCode](DataTypeCode)
    mapping_type = Guard[MappingType](MappingType, ImmutableCheck())
    keys = Guard[UniqueList[str]](UniqueList, TrimmedCollectionItemFormatCheck(r"^\S+(?:\s\S+)*$"))
    created_at = Guard[dt.datetime](dt.datetime, ImmutableCheck())

    allocators: dict[MappingType, type[Allocator]] = {
        MappingType.ONE_TO_ONE: OneToOneAllocator,
        MappingType.ONE_TO_MANY: OneToManyAllocator,
    }

    def __init__(
        self,
        code: str,
        prototype_id: EntityId,
        data_type: DataTypeCode,
        mapping_type: MappingType,
        keys: UniqueList[str],
        created_at: dt.datetime | None = None,
    ) -> None:
        self.code = code
        self.prototype_id = prototype_id
        self.data_type = data_type
        self.mapping_type = mapping_type
        self.keys = keys
        self.created_at = created_at or dt.datetime.now(tz=dt.timezone.utc)

        self._validate()

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.code = },",
                f"{self.prototype_id = },",
                f"{self.data_type = },",
                f"{self.keys = },",
                f"{self.created_at = },",
                f"{self.mapping_type = }>",
            ),
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.code == other.code

    @property
    def allocator(self) -> type[Allocator]:
        return self.allocators[self.mapping_type]

    def search_data(self, document_layout: DocumentLayout) -> list[KeyValuePair]:
        return self.allocator(document_layout, self.keys).allocate()

    def update(
        self,
        keys: UniqueList[str],
    ) -> None:
        self.keys = keys

    def _validate(self) -> None:
        if not self.keys:
            raise InvariantViolation("Mapping keys attribute cannot be empty list")
