from http import HTTPStatus
from typing import Any

import pytest
from starlette.testclient import TestClient

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.domain.exceptions import PrototypeNotFound
from deps_prototype.domain.model import Mapping, Prototype, UniqueList

__all__ = ["assert_mappings_equal"]


def assert_mappings_equal(mapping: Mapping, raw_mapping: dict[str, Any]) -> None:
    assert raw_mapping["code"] == mapping.code
    assert raw_mapping["prototypeId"] == mapping.prototype_id()
    assert raw_mapping["keys"] == mapping.keys
    assert raw_mapping["dataType"] == mapping.data_type
    assert raw_mapping["mappingType"] == mapping.mapping_type


@pytest.mark.mappings
def test_create_mapping__prototype_doesnt_exist__404(
    client: TestClient,
    create_mapping_payload: dict[str, Any],
    prototype: Prototype,
    mapping_service_mock,
) -> None:
    prototype_id = prototype.id()
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/mappings"
    mapping_service_mock.create_mapping.side_effect = PrototypeNotFound(prototype_id)

    response = client.post(endpoint, json=create_mapping_payload)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.mappings
def test_create_mapping__prototype_exists__created(
    client: TestClient,
    prototype: Prototype,
    mapping: Mapping,
    create_mapping_payload: dict[str, Any],
    mapping_service_mock,
    tenant_id: str,
) -> None:
    prototype_id = prototype.id()
    mapping_service_mock.create_mapping.return_value = mapping
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/mappings"

    response = client.post(endpoint, json=create_mapping_payload)

    assert response.status_code == HTTPStatus.CREATED
    assert_mappings_equal(mapping, response.json())

    mapping_service_mock.create_mapping.assert_called_once_with(
        prototype_id=prototype_id,
        tenant_id=tenant_id,
        code=create_mapping_payload["code"],
        data_type=create_mapping_payload["typeCode"],
        keys=UniqueList(create_mapping_payload["keys"]),
        mapping_type=create_mapping_payload["mappingType"],
    )
