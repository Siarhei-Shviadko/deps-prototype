from deps_message_flow.sagas.orchestration import SagaDataMapping

from .prototype import PrototypeCreationSagaData
from .reference_layout import ReferenceLayoutProcessingSagaData

__all__ = ["make_saga_data_mapping"]


def make_saga_data_mapping() -> SagaDataMapping:
    return SagaDataMapping(
        {
            PrototypeCreationSagaData.__name__: PrototypeCreationSagaData,
            ReferenceLayoutProcessingSagaData.__name__: ReferenceLayoutProcessingSagaData,
        },
    )
