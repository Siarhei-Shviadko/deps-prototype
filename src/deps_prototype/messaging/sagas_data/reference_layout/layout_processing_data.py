from typing import Any

from deps_message_flow.commands.consumer import (
    CommandWithDestination,
    CommandWithDestinationBuilder,
)
from deps_message_flow.sagas.orchestration import SagaData

from deps_prototype.domain.model import LayoutState, ParsingFeature

from ...commands import PerformParsing, PerformUnification
from ...error import Error
from ..shared import Destination
from .layout_processing_state_machine import ReferenceLayoutProcessingStateMachine

__all__ = ["ReferenceLayoutProcessingSagaData"]


class ReferenceLayoutProcessingSagaData(SagaData):
    def __init__(
        self,
        id_: str,
        prototype_id: str,
        engine: str,
        language: str,
        tenant_id: str,
        files: list[str],
        parsing_features: set[ParsingFeature] | None,
        *,
        state: LayoutState | None = LayoutState.NEW,
        error: Error | None = None,
    ) -> None:
        super().__init__(entity_id=id_)
        self.prototype_id = prototype_id
        self.engine = engine
        self.language = language
        self.tenant_id = tenant_id
        self.parsing_features = parsing_features
        self.files = files
        self._error = error

        self._state_machine = ReferenceLayoutProcessingStateMachine(current_state=state)

    @property
    def state(self) -> LayoutState:
        return self._state_machine.current_state

    @property
    def reference_layout_id(self) -> str | None:
        return self.entity_id

    @reference_layout_id.setter
    def reference_layout_id(self, value: str | None) -> None:
        self.entity_id = value

    @property
    def error(self) -> Error | None:
        return self._error

    @error.setter
    def error(self, error: Error) -> None:
        self._error = error

    def update_to_next_state(self) -> None:
        self._state_machine.to_next_state()

    def update_to_fail_state(self):
        self._state_machine.to_fail_state()

    def is_invoke_unifier(self) -> bool:
        return self.state == LayoutState.UNIFICATION

    def is_invoke_parsing(self) -> bool:
        return self.state == LayoutState.PARSING

    def perform_unification(self) -> CommandWithDestination:
        return (
            CommandWithDestinationBuilder.send(
                command=PerformUnification(self.entity_id, self.prototype_id, self.files),
            )
            .to(Destination.UNIFIER_SERVICE)
            .build()
        )

    def perform_parsing(self) -> CommandWithDestination:
        return (
            CommandWithDestinationBuilder.send(
                command=PerformParsing(
                    tenant_id=self.tenant_id,
                    document_id=self.reference_layout_id,
                    files=self.files,
                    engine=self.engine,
                    features=list(self.parsing_features) if self.parsing_features else None,
                    language=self.language,
                ),
            )
            .to(Destination.PARSING_SERVICE)
            .build()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_layout_id": self.entity_id,
            "prototype_id": self.prototype_id,
            "engine": self.engine,
            "language": self.language,
            "tenant_id": self.tenant_id,
            "state": self.state.value,
            "parsing_features": list(self.parsing_features),
            "files": self.files,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "ReferenceLayoutProcessingSagaData":
        return cls(
            id_=raw_data["reference_layout_id"],
            prototype_id=raw_data.get("prototype_id"),
            engine=raw_data["engine"],
            language=raw_data["language"],
            tenant_id=raw_data["tenant_id"],
            state=raw_data["state"],
            parsing_features=raw_data["parsing_features"],
            files=raw_data.get("files"),
        )
