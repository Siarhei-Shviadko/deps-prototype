from http import HTTPStatus

import pytest
from starlette.testclient import TestClient

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.application import QueryPrototypeService
from deps_prototype.domain.exceptions import PrototypeNotFound
from deps_prototype.domain.model import PrototypeWithMappings

from ..mapping import assert_mappings_equal
from ..tabular_mapping import assert_tabular_mappings_equal
from .test_find_prototypes import compare_prototypes

FIRST_ELEMENT: int = 0


@pytest.mark.prototype
def test_find__prototype_doesnt_exist__not_found_error(
    client: TestClient,
    prototype_id: str,
    query_prototype_service_mock: QueryPrototypeService,
) -> None:
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}"
    query_prototype_service_mock.find_prototype.side_effect = PrototypeNotFound(prototype_id)

    response = client.get(endpoint)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.prototype
def test_find__prototype_exists__ok(
    client: TestClient,
    prototype_id: str,
    prototype_with_mappings: PrototypeWithMappings,
    query_prototype_service_mock: QueryPrototypeService,
) -> None:
    endpoint = f"{V1_API_PREFIX}/prototypes/{prototype_id}"
    query_prototype_service_mock.find_prototype.return_value = prototype_with_mappings

    response = client.get(endpoint)

    response_dict = response.json()
    raw_mapping = response_dict["mappings"][FIRST_ELEMENT]
    raw_tabular_mapping = response_dict["tabularMappings"][FIRST_ELEMENT]

    assert response.status_code == HTTPStatus.OK

    compare_prototypes(prototype_with_mappings["prototype"], response_dict)

    assert_mappings_equal(prototype_with_mappings["mappings"][FIRST_ELEMENT], raw_mapping)
    assert_tabular_mappings_equal(prototype_with_mappings["tabular_mappings"][FIRST_ELEMENT], raw_tabular_mapping)
