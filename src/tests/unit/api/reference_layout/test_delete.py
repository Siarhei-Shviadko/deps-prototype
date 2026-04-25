from http import HTTPStatus
from urllib.parse import urlencode

import pytest

from deps_prototype.api.constants import V1_API_PREFIX


@pytest.mark.layouts
def test_delete_layout__no_content(client, reference_layout_service_mock, prototype_id, layout_id, tenant_id):
    reference_layout_service_mock.delete_layout.return_value = None
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/layouts/{layout_id}"

    response = client.delete(
        endpoint,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    reference_layout_service_mock.delete_layout.assert_called_once_with(
        prototype_id=prototype_id,
        layout_id=layout_id,
        tenant_id=tenant_id,
    )


@pytest.mark.layouts
def test_delete_layouts__no_content(client, reference_layout_service_mock, prototype_id, tenant_id):
    layout_ids = ["a", "b"]
    params = {"layoutIds": layout_ids}
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/layouts?{urlencode(params, doseq=True)}"
    reference_layout_service_mock.delete_layouts.return_value = None

    response = client.delete(
        endpoint,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    reference_layout_service_mock.delete_layouts.assert_called_once_with(
        prototype_id=prototype_id,
        tenant_id=tenant_id,
        layout_ids=layout_ids,
    )
