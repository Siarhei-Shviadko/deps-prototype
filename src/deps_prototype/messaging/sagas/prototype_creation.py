import logging

from deps_message_flow.sagas.orchestration_simple_dsl import SimpleSaga

from ..exceptions import SagaFailed, SagaRolledBack
from ..sagas_data import PrototypeCreationSagaData, PrototypeCreationSteps

__all__ = ["PrototypeCreationSaga"]


class PrototypeCreationSaga(SimpleSaga[PrototypeCreationSagaData]):
    def __init__(self, steps: PrototypeCreationSteps) -> None:
        self._saga_definition = (
            self.step()
            .invoke_local(steps.create_document_type)
            .with_compensation(steps.delete_document_type)
            .step()
            .invoke_local(steps.create_prototype)
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: PrototypeCreationSagaData) -> None:
        self._logger.info("Saga: %s for prototype %s creation is completed successfully", saga_id, data.prototype_id)

    def on_saga_rolled_back(self, saga_id: str, data: PrototypeCreationSagaData) -> None:
        self._logger.warning("Saga: %s for prototype %s creation is rolled back", saga_id, data.prototype_id)
        raise SagaRolledBack("Prototype creation saga failed and rolled back")

    def on_saga_failed(self, saga_id: str, data: PrototypeCreationSagaData) -> None:
        self._logger.error("Saga: %s for prototype %s creation is failed", saga_id, data.prototype_id)
        raise SagaFailed("Prototype creation saga failed")
