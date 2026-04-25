from datetime import datetime

from deps_message_flow.events.common import DomainEvent

from ..reference_layout import LayoutState, ReferenceLayout
from ..shared import EntityId, FormatCheck, Guard, ImmutableCheck, TenantId, UniqueList
from .events import PrototypeDeleted, PrototypeUpdated

__all__ = ["Prototype"]


class Prototype:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    tenant_id = Guard[TenantId](TenantId, ImmutableCheck())
    name = Guard[str](str, ImmutableCheck(), FormatCheck(r"^(?![- ]+)(?!.*[- ]+$)[\w-]+( [\w-]+)*$"))
    engine = Guard[str](str)
    language = Guard[str](str)
    description = Guard[str](str)
    created_at = Guard[datetime](datetime, ImmutableCheck())

    def __init__(
        self,
        id_: EntityId,
        tenant_id: TenantId,
        name: str,
        engine: str,
        language: str,
        created_at: datetime,
        description: str | None = None,
        *,
        events: list[DomainEvent] | None = None,
    ) -> None:
        self.id = id_
        self.tenant_id = tenant_id
        self.name = name
        self.engine = engine
        self.language = language
        self.created_at = created_at

        if description:
            self.description = description

        self._events = events or []

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.id = },",
                f"{self.tenant_id = },",
                f"{self.name = },",
                f"{self.engine = },",
                f"{self.language = },",
                f"{self.created_at = },",
                f"{self.description = },",
                f"{self._events = }>",
            ),
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    @property
    def events(self) -> list[DomainEvent]:
        return self._events

    def add_reference_layout(
        self,
        blob_name: str,
        state: LayoutState,
        title: str,
    ) -> ReferenceLayout:
        reference_layout_id = EntityId()

        return ReferenceLayout(
            id_=reference_layout_id,
            prototype_id=self.id,
            state=state,
            blob_name=blob_name,
            title=title,
        )

    def update_info(
        self,
        engine: str | None = None,
        language: str | None = None,
        description: str | None = None,
    ) -> None:
        if any(item is not None for item in (engine, language, description)):
            if engine is not None:
                self.engine = engine
            if language is not None:
                self.language = language
            if description is not None:
                self.description = description

            self._events.append(
                PrototypeUpdated(
                    prototype_id=self.id(),
                    tenant_id=self.tenant_id(),
                    engine=engine,
                    language=language,
                    description=description,
                ),
            )

    def delete(self) -> None:
        self._events.append(PrototypeDeleted(prototype_id=self.id(), tenant_id=self.tenant_id()))
