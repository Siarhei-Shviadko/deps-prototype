from http import HTTPStatus
from typing import Any

import pytest
from starlette.testclient import TestClient

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.domain.exceptions import PrototypeNotFound
from deps_prototype.domain.model import Prototype, TabularMapping, UniqueList

__all__ = ["assert_tabular_mappings_equal"]


def assert_tabular_mappings_equal(tabular_mapping: TabularMapping, raw_mapping: dict[str, Any]) -> None:
    assert raw_mapping["code"] == tabular_mapping.code
    assert raw_mapping["prototypeId"] == tabular_mapping.prototype_id()
    assert raw_mapping["headers"] == [header.to_dict() for header in tabular_mapping.headers]
    assert raw_mapping["headerType"] == tabular_mapping.header_type
    assert raw_mapping["occurrenceIndex"] == tabular_mapping.occurrence_index


@pytest.mark.tabular_mappings
def test_create_mapping__prototype_doesnt_exist__404(
    client: TestClient,
    create_tabular_mapping_payload: dict[str, Any],
    prototype: Prototype,
    tabular_mapping_service_mock,
) -> None:
    prototype_id = prototype.id()
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/tabular-mappings"
    tabular_mapping_service_mock.create_tabular_mapping.side_effect = PrototypeNotFound(prototype_id)

    response = client.post(endpoint, json=create_tabular_mapping_payload)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.tabular_mappings
def test_create_mapping__prototype_exists__created(
    client: TestClient,
    prototype: Prototype,
    tabular_mapping: TabularMapping,
    create_tabular_mapping_payload: dict[str, Any],
    tabular_mapping_service_mock,
    tenant_id: str,
) -> None:
    prototype_id = prototype.id()
    tabular_mapping_service_mock.create_tabular_mapping.return_value = tabular_mapping
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/tabular-mappings"

    response = client.post(endpoint, json=create_tabular_mapping_payload)

    assert response.status_code == HTTPStatus.CREATED
    assert_tabular_mappings_equal(tabular_mapping, response.json())

    tabular_mapping_service_mock.create_tabular_mapping.assert_called_once()
