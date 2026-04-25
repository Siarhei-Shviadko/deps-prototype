import logging

from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..commands import PerformParsingReply, PerformUnificationReply
from ..saga_handlers import ReferenceLayoutProcessingHandlers
from ..sagas_data import (
    ReferenceLayoutProcessingSagaData,
    ReferenceLayoutProcessingSteps,
)

__all__ = ["ReferenceLayoutProcessingSaga"]


class ReferenceLayoutProcessingSaga(SimpleSaga[ReferenceLayoutProcessingSagaData]):
    def __init__(self, steps: ReferenceLayoutProcessingSteps) -> None:
        self._saga_definition = (
            # Update state
            self.step()
            .invoke_local(steps.update_reference_layout_state)
            # Unification
            .step()
            .invoke_participant(
                ReferenceLayoutProcessingSagaData.perform_unification,
                predicate=ReferenceLayoutProcessingSagaData.is_invoke_unifier,
            )
            .on_reply(PerformUnificationReply, ReferenceLayoutProcessingHandlers.evaluate_unification_result)
            # Update state
            .step()
            .invoke_local(steps.update_reference_layout_state)
            # Parsing
            .step()
            .invoke_participant(
                ReferenceLayoutProcessingSagaData.perform_parsing,
                predicate=ReferenceLayoutProcessingSagaData.is_invoke_parsing,
            )
            .on_reply(PerformParsingReply, ReferenceLayoutProcessingHandlers.evaluate_parsing_result)
            # Update state
            .step()
            .invoke_local(steps.update_reference_layout_state)
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: ReferenceLayoutProcessingSagaData) -> None:
        self._logger.info("Saga: %s for reference_layout: %s is completed successfully", saga_id, data.entity_id)

    def on_saga_failed(self, saga_id: str, data: ReferenceLayoutProcessingSagaData) -> None:
        self._logger.info("Saga: %s for reference_layout: %s is failed", saga_id, data.entity_id)

    def on_saga_rolled_back(self, saga_id: str, data: ReferenceLayoutProcessingSagaData) -> None:
        self._logger.info("Saga: %s for reference_layout: %s is rolled back", saga_id, data.entity_id)
