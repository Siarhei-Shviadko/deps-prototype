from http import HTTPStatus

from deps_prototype.api.constants import BASE_API_PREFIX


def test_healthcheck__connection_work__200(client):
    response = client.get(f"{BASE_API_PREFIX}/healthcheck")

    assert response.status_code == HTTPStatus.OK
