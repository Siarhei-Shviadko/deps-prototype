from ..shared import EntityId, Guard, ImmutableCheck
from .commands import DeleteFiles
from .events import ReferenceLayoutDeleted, ReferenceLayoutStateUpdated
from .layout_state import LayoutState

__all__ = ["ReferenceLayout"]


class ReferenceLayout:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    prototype_id = Guard[EntityId](EntityId, ImmutableCheck())
    title = Guard[str](str, ImmutableCheck())
    state = Guard[LayoutState](LayoutState)
    blob_name = Guard[str](str)

    def __init__(
        self,
        id_: EntityId,
        prototype_id: EntityId,
        state: LayoutState,
        blob_name: str,
        title: str | None = None,
    ):
        self.id = id_
        self.prototype_id = prototype_id
        self.state = state
        self.blob_name = blob_name

        if title:
            self.title = title

        self._events: list[object] = []
        self._commands: list[object] = []

    def __repr__(self) -> str:
        return " ".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.id = },",
                f"{self.title = },",
                f"{self.prototype_id = },",
                f"{self.state = },",
                f"{self.blob_name = }>",
            ),
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    @property
    def events(self) -> list[object]:
        return self._events

    @property
    def commands(self) -> list[object]:
        return self._commands

    def update_info(
        self,
        state: LayoutState | None = None,
        blob_name: str | None = None,
    ) -> None:
        if blob_name is not None:
            self.blob_name = blob_name
        if state is not None:
            self.state = state
            self._events.append(
                ReferenceLayoutStateUpdated(
                    reference_layout_id=self.id(),
                    prototype_id=self.prototype_id(),
                    state=state.value,
                ),
            )

    def delete(self) -> None:
        self._events.append(ReferenceLayoutDeleted(reference_layout_id=self.id()))
        self._commands.append(DeleteFiles(file_paths=[self.blob_name]))
