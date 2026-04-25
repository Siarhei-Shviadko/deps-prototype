from ...exceptions import ReferenceLayoutRestartingError
from ..shared import ISpecification
from .layout_state import LayoutState
from .reference_layout import ReferenceLayout

__all__ = ["CanRestartSpecification"]


class CanRestartSpecification(ISpecification[ReferenceLayout]):
    def check(self) -> None:
        if not self._is_satisfied_by(self._entity):
            raise ReferenceLayoutRestartingError

    @staticmethod
    def _is_satisfied_by(entity: ReferenceLayout) -> bool:
        return entity.state == LayoutState.FAILED
