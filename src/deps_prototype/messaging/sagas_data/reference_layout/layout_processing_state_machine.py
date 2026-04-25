from deps_prototype.domain.model import LayoutState

__all__ = ["ReferenceLayoutProcessingStateMachine"]


class ReferenceLayoutProcessingStateMachine:
    LAYOUT_STATES_ORDER = [
        LayoutState.NEW,
        LayoutState.UNIFICATION,
        LayoutState.PARSING,
        LayoutState.READY,
    ]
    FAILED_LAYOUT_STATE = LayoutState.FAILED

    def __init__(self, current_state: LayoutState):
        self._current_state = current_state

    @property
    def current_state(self) -> LayoutState:
        return self._current_state

    def to_next_state(self) -> None:
        self._current_state = self._find_next_state(state=self._current_state)

    def to_fail_state(self) -> None:
        self._current_state = self.FAILED_LAYOUT_STATE

    def _find_next_state(self, state: LayoutState) -> LayoutState:
        try:
            index = self.LAYOUT_STATES_ORDER.index(state)

            if index >= len(self.LAYOUT_STATES_ORDER) - 1:
                raise RuntimeError(f"Cannot find next state for finished state - '{state}'")

            return self.LAYOUT_STATES_ORDER[index + 1]

        except ValueError:
            raise RuntimeError(f"Cannot find next state for state - '{state}'")
