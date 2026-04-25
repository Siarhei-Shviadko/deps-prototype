from http import HTTPStatus

import pytest

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.domain.exceptions import PrototypeNotFound, ReferenceLayoutNotFound


@pytest.mark.layouts
def test_find_layout__prototype_not_exist__not_found_error(
    client,
    prototype,
    reference_layout,
    reference_layout_service_mock,
):
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype.id.value}/layouts/{reference_layout.id.value}"
    reference_layout_service_mock.get_layout.side_effect = PrototypeNotFound(prototype.id())
    response = client.get(endpoint)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.layouts
def test_find_layout__reference_layout_not_exist__not_found_error(
    client,
    saved_prototype,
    reference_layout,
    reference_layout_service_mock,
):
    endpoint = f"{V1_API_PREFIX}/prototypes/{saved_prototype.id.value}/layouts/{reference_layout.id.value}"
    reference_layout_service_mock.get_layout.side_effect = ReferenceLayoutNotFound(reference_layout.id())
    response = client.get(endpoint)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.layouts
def test_find_layout__success(
    client,
    saved_prototype,
    fake_prototype_repository,
    fake_reference_layout_repository,
    reference_layout,
    reference_layout_service_mock,
):
    fake_reference_layout_repository.save(reference_layout)
    reference_layout_service_mock.get_layout.return_value = reference_layout

    endpoint = f"{V1_API_PREFIX}/prototypes/{saved_prototype.id.value}/layouts/{reference_layout.id.value}"

    response = client.get(endpoint)

    assert response.status_code == HTTPStatus.OK

    result_layout = response.json()

    assert result_layout["id"] == reference_layout.id()
    assert result_layout["prototypeId"] == reference_layout.prototype_id()
    assert result_layout["state"] == reference_layout.state.value
    assert result_layout["blobName"] == reference_layout.blob_name
    assert result_layout["title"] == reference_layout.title
