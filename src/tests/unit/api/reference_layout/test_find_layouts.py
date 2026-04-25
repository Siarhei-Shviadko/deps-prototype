from http import HTTPStatus

import pytest

from deps_prototype.api.constants import V1_API_PREFIX


@pytest.mark.layouts
def test_find_layouts__success(
    client, prototype, fake_prototype_repository, fake_reference_layout_repository, reference_layout
):
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype.id.value}/layouts"

    fake_prototype_repository.save(prototype)
    fake_reference_layout_repository.save(reference_layout)

    response = client.get(endpoint)

    assert response.status_code == HTTPStatus.OK

    result_layouts = response.json()["reference_layouts"]

    assert len(result_layouts) == 1
    assert result_layouts[0]["id"] == reference_layout.id()
    assert result_layouts[0]["prototypeId"] == reference_layout.prototype_id()
    assert result_layouts[0]["state"] == reference_layout.state.value
    assert result_layouts[0]["blobName"] == reference_layout.blob_name
    assert result_layouts[0]["title"] == reference_layout.title


@pytest.mark.layouts
def test_find_layouts__no_layouts__success(client, prototype, fake_prototype_repository):
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype.id.value}/layouts"

    fake_prototype_repository.save(prototype)

    response = client.get(endpoint)

    assert response.status_code == HTTPStatus.OK
    assert response.json()["reference_layouts"] == []
