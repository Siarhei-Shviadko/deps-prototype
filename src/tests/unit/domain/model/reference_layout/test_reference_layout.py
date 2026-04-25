import pytest

from deps_prototype.domain.model import LayoutState


@pytest.mark.reference_layout
def test_update_info__all_fields(reference_layout, create_reference_layout_payload):
    new_state = LayoutState(create_reference_layout_payload["state"])
    new_blob_name = create_reference_layout_payload["blob_name"]

    reference_layout.update_info(state=new_state, blob_name=new_blob_name)

    assert reference_layout.state == new_state
    assert reference_layout.blob_name == new_blob_name


@pytest.mark.reference_layout
def test_update_info__none_fields__not_updated(reference_layout):
    old_state = reference_layout.state
    old_blob_name = reference_layout.blob_name

    reference_layout.update_info()

    assert reference_layout.state == old_state
    assert reference_layout.blob_name == old_blob_name
