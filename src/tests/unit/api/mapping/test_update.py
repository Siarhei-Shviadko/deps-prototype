from http import HTTPStatus
from typing import Any

import pytest
from starlette.testclient import TestClient

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.domain.exceptions import MappingNotFound, PrototypeNotFound
from deps_prototype.domain.model import Mapping, Prototype, UniqueList

from .test_create import assert_mappings_equal


@pytest.mark.mappings
def test_update_mapping__mapping_doesnt_exist__404(
    client: TestClient,
    modify_mapping_payload: dict[str, Any],
    prototype: Prototype,
    mapping_service_mock,
) -> None:
    mapping_code = "some_id"
    prototype_id = prototype.id()
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/mappings/{mapping_code}"
    mapping_service_mock.modify_mapping.side_effect = MappingNotFound(mapping_code)

    response = client.put(endpoint, json=modify_mapping_payload)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.mappings
def test_update_mapping__prototype_doesnt_exist__404(
    client: TestClient,
    modify_mapping_payload: dict[str, Any],
    prototype: Prototype,
    mapping_service_mock,
) -> None:
    mapping_code = "some_id"
    prototype_id = prototype.id()
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/mappings/{mapping_code}"
    mapping_service_mock.modify_mapping.side_effect = PrototypeNotFound(mapping_code)

    response = client.put(endpoint, json=modify_mapping_payload)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.mappings
def test_update_mapping__mapping_exists__modified(
    client: TestClient,
    modify_mapping_payload: dict[str, Any],
    prototype: Prototype,
    mapping_service_mock,
    mapping: Mapping,
    tenant_id: str,
) -> None:
    prototype_id = prototype.id()
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/mappings/{mapping.code}"
    mapping_service_mock.modify_mapping.return_value = mapping

    response = client.put(endpoint, json=modify_mapping_payload)

    assert response.status_code == HTTPStatus.OK

    assert_mappings_equal(mapping, response.json())

    mapping_service_mock.modify_mapping.assert_called_once_with(
        prototype_id=prototype_id,
        mapping_code=mapping.code,
        tenant_id=tenant_id,
        keys=UniqueList(modify_mapping_payload["keys"]),
    )
