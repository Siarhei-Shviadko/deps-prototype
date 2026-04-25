from http import HTTPStatus
from io import BytesIO

import pytest
from deps_message_flow.sagas.orchestration import ISagaInstanceRepository

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.domain.model import IReferenceLayoutRepository


@pytest.mark.reference_layout
def test_create_reference_layout__prototype_doesnt_exist__404(
    client,
    prototype_id,
    reference_layout,
    test_file_name: str,
    test_file_content: bytes,
    fake_saga_instance_repository: ISagaInstanceRepository,
    fake_reference_layout_repository: IReferenceLayoutRepository,
):
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/layouts"
    files = {
        "file": (test_file_name, BytesIO(test_file_content), "application/jpg"),
    }
    response = client.post(endpoint, files=files)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.reference_layout
def test_create_reference_layout__created(
    client,
    prototype_id,
    tenant_id,
    reference_layout,
    test_file_name: str,
    test_file_content: bytes,
    reference_layout_with_sagas_service_mock,
):
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/layouts"
    reference_layout_with_sagas_service_mock.create_layout.return_value = reference_layout.id()

    files = {
        "file": (test_file_name, BytesIO(test_file_content), "application/jpg"),
    }
    response = client.post(endpoint, files=files)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["id"]

    reference_layout_with_sagas_service_mock.create_layout.assert_called_once_with(
        prototype_id=prototype_id,
        tenant_id=tenant_id,
        file_name=test_file_name,
        file=test_file_content,
    )
