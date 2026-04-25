from http import HTTPStatus

from deps_message_flow.sagas.orchestration import ISagaInstanceRepository

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.application import IDocumentTypeProxy, IExtractionProxy


def test_create_prototype(
    client,
    prototype_id: str,
    fake_saga_instance_repository: ISagaInstanceRepository,
    fake_document_type_service: IDocumentTypeProxy,
    fake_extraction_proxy: IExtractionProxy,
):
    endpoint = f"{V1_API_PREFIX}/prototypes"
    payload = {
        "name": "test",
        "engine": "TESSERACT",
        "language": "eng",
        "description": "test",
    }

    response = client.post(endpoint, json=payload)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["id"]
