from http import HTTPStatus
from typing import Any

import pytest
from starlette.testclient import TestClient

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.application import TabularMappingService
from deps_prototype.domain.exceptions import (
    NotFoundError,
    PrototypeNotFound,
    TabularMappingNotFound,
)
from deps_prototype.domain.model import Prototype, TabularMapping, UniqueList


def assert_tabular_mappings_equal(tabular_mapping: TabularMapping, raw_mapping: dict[str, Any]) -> None:
    assert raw_mapping["code"] == tabular_mapping.code
    assert raw_mapping["prototypeId"] == tabular_mapping.prototype_id()
    assert raw_mapping["headers"] == [header.dict() for header in tabular_mapping.headers]
    assert raw_mapping["headerType"] == tabular_mapping.header_type
    assert raw_mapping["occurrenceIndex"] == tabular_mapping.occurrence_index


@pytest.mark.tabular_mappings
@pytest.mark.parametrize(
    "error",
    [PrototypeNotFound, TabularMappingNotFound],
)
def test_update_tabular_mapping__not_found(
    client: TestClient,
    tabular_mapping_service_mock: TabularMappingService,
    prototype_id: str,
    tabular_mapping: TabularMapping,
    error: type[NotFoundError],
) -> None:
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/tabular-mappings/{tabular_mapping.code}"
    tabular_mapping_service_mock.update_tabular_mapping.side_effect = error(prototype_id)

    response = client.patch(endpoint, json={})

    assert response.status_code == HTTPStatus.NOT_FOUND

    tabular_mapping_service_mock.update_tabular_mapping.assert_called_once()


@pytest.mark.tabular_mappings
def test_update_tabular_mapping__created(
    client: TestClient,
    tabular_mapping_service_mock: TabularMappingService,
    prototype_id: str,
    tabular_mapping: TabularMapping,
) -> None:
    tabular_mapping_service_mock.update_tabular_mapping.return_value = tabular_mapping
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}/tabular-mappings/{tabular_mapping.code}"

    response = client.patch(endpoint, json={})

    assert response.status_code == HTTPStatus.OK
    assert_tabular_mappings_equal(tabular_mapping, response.json())

    tabular_mapping_service_mock.update_tabular_mapping.assert_called_once()
