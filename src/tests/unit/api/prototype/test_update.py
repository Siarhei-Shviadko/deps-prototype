from http import HTTPStatus

import pytest

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.domain.exceptions import PrototypeNotFound


@pytest.mark.prototype
def test_update__prototype_doesnt_exists__not_found(client, prototype, prototype_service_mock):
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype.id()}"
    prototype_service_mock.update_prototype.side_effect = PrototypeNotFound(prototype.id())
    payload = {
        "engine": prototype.engine,
        "language": prototype.language,
        "description": prototype.description,
    }

    response = client.patch(endpoint, json=payload)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.prototype
def test_update__prototype_exists__updated(client, prototype, prototype_service_mock):
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype.id()}"
    prototype_service_mock.update_prototype.return_value = prototype
    payload = {
        "engine": prototype.engine,
        "language": prototype.language,
        "description": prototype.description,
    }

    response = client.patch(endpoint, json=payload)

    json_response = response.json()
    assert response.status_code == HTTPStatus.OK
    assert json_response["name"] == prototype.name
    assert json_response["engine"] == prototype.engine
    assert json_response["language"] == prototype.language
    assert json_response["description"] == prototype.description

    prototype_service_mock.update_prototype.assert_called_once_with(
        description=prototype.description,
        engine=prototype.engine,
        id_=prototype.id(),
        language=prototype.language,
        tenant_id=prototype.tenant_id(),
    )
