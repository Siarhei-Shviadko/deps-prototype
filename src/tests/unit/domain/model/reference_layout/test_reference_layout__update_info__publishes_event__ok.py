import pytest

from deps_prototype.domain.model import LayoutState
from deps_prototype.domain.model.reference_layout.events import (
    ReferenceLayoutStateUpdated,
)
from tests.factories import ReferenceLayoutFactory


@pytest.mark.reference_layout
def test_update_info__state_change__publishes_event__ok():
    layout = ReferenceLayoutFactory.create(state=LayoutState.NEW)
    layout._events = []

    layout.update_info(state=LayoutState.UNIFICATION)

    assert len(layout.events) == 1
    event = layout.events[0]
    assert isinstance(event, ReferenceLayoutStateUpdated)
    assert event.state == "Unification"
    assert event.reference_layout_id == layout.id()
    assert event.prototype_id == layout.prototype_id()


@pytest.mark.reference_layout
def test_update_info__no_state_change__no_event_published__ok():
    layout = ReferenceLayoutFactory.create(state=LayoutState.NEW)
    layout._events = []

    layout.update_info(blob_name="new_blob.pdf")

    assert len(layout.events) == 0
