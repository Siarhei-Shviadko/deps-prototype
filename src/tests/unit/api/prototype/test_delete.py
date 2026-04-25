from http import HTTPStatus

import pytest

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.application import PrototypeService


@pytest.mark.prototype
def test_delete__no_error(
    client,
    prototype,
    prototype_service_mock: PrototypeService,
):
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype.id()}"
    prototype_service_mock.delete_prototype.return_value = None

    response = client.delete(endpoint)

    assert response.status_code == HTTPStatus.NO_CONTENT
    prototype_service_mock.delete_prototype.assert_called_once_with(
        id_=prototype.id(),
        tenant_id=prototype.tenant_id(),
    )


@pytest.mark.prototype
def test_delete_all__no_error(
    client,
    prototype,
    prototype_service_mock: PrototypeService,
):
    endpoint = f"{V1_API_PREFIX}/prototypes"
    params = {"ids": [prototype.id()]}
    prototype_service_mock.delete_prototypes.return_value = None

    response = client.delete(endpoint, params=params)

    assert response.status_code == HTTPStatus.NO_CONTENT
    prototype_service_mock.delete_prototypes.assert_called_once_with(
        ids=[prototype.id()],
        tenant_id=prototype.tenant_id(),
    )
