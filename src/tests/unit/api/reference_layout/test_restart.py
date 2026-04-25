from http import HTTPStatus

import pytest

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.domain.model import LayoutState


@pytest.mark.reference_layout
@pytest.mark.reference_layout_restart
def test_restart_reference_layout__layout_exists__successful(
    client,
    saved_prototype,
    failed_saved_reference_layout,
):
    prototype_id = saved_prototype.id()
    layout_id = failed_saved_reference_layout.id()
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/layouts/{layout_id}/restart"

    response = client.post(endpoint)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.reference_layout
@pytest.mark.reference_layout_restart
def test_restart_reference_layout__layout_doesnt_exist__error(
    client,
    saved_prototype,
):
    prototype_id = saved_prototype.id()
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/layouts/fake_layout_id/restart"

    response = client.post(endpoint)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.reference_layout
@pytest.mark.reference_layout_restart
def test_restart_reference_layout__prototype_doesnt_exist__error(
    client,
    failed_saved_reference_layout,
):
    layout_id = failed_saved_reference_layout.id()
    endpoint = f"{V1_API_PREFIX}/prototypes/fake_prototype_id/layouts/{layout_id}/restart"

    response = client.post(endpoint)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.reference_layout
@pytest.mark.reference_layout_restart
def test_restart_reference_layout__layout_not_in_failed_state_error(
    client,
    saved_prototype,
    saved_reference_layout_in_unrestarted_state,
):
    prototype_id = saved_prototype.id()
    layout_id = saved_reference_layout_in_unrestarted_state.id()
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/layouts/{layout_id}/restart"

    response = client.post(endpoint)

    assert response.status_code == HTTPStatus.BAD_REQUEST
