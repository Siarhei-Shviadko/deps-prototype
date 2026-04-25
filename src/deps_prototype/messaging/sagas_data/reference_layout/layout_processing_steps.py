from typing import TYPE_CHECKING

from .layout_processing_data import ReferenceLayoutProcessingSagaData

if TYPE_CHECKING:
    from deps_prototype.application import ReferenceLayoutService

__all__ = ["ReferenceLayoutProcessingSteps"]


class ReferenceLayoutProcessingSteps:
    def __init__(self, reference_layout_service: "ReferenceLayoutService") -> None:
        self._reference_layout_service = reference_layout_service

    def update_reference_layout_state(self, data: ReferenceLayoutProcessingSagaData) -> None:
        self._update_state(data)
        self._reference_layout_service.update_layout(
            reference_layout_id=data.reference_layout_id,
            prototype_id=data.prototype_id,
            state=data.state,
        )

    @staticmethod
    def _update_state(data: ReferenceLayoutProcessingSagaData) -> None:
        if data.error is not None:
            data.update_to_fail_state()
        else:
            data.update_to_next_state()
