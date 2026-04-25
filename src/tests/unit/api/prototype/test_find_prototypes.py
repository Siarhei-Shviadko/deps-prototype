from datetime import datetime, timedelta
from http import HTTPStatus
from random import randint
from uuid import uuid4

import pytest
from dateutil import parser

from deps_prototype.api.constants import V1_API_PREFIX
from deps_prototype.domain.model import (
    PrototypeSortingField,
    SortingDirection,
    TenantId,
)
from tests.factories import PrototypeFactory

__all__ = ["compare_prototypes"]


def make_query(
    page: int | None = None,
    per_page: int | None = None,
    ids: list[str] | None = None,
    name: str | None = None,
    engines: list[str] | None = None,
    languages: list[str] | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    sorting_field: PrototypeSortingField = PrototypeSortingField.CREATED_AT,
    sorting_direction: SortingDirection = SortingDirection.DESC,
) -> str:
    query = f"sortField={sorting_field.value}&sortDirect={sorting_direction.value}"
    query = f"{query}&name={name}" if name is not None else query
    query = f"{query}&startDate={start_date}" if start_date is not None else query
    query = f"{query}&endDate={end_date}" if end_date is not None else query
    query = f"{query}&page={page}" if page is not None else query
    query = f"{query}&perPage={per_page}" if per_page is not None else query

    if ids:
        for id_ in ids:
            query = f"{query}&id={id_}"

    if engines:
        for engine in engines:
            query = f"{query}&engine={engine}"

    if languages:
        for language in languages:
            query = f"{query}&language={language}"

    return query


def compare_prototypes(expected_prototype, result_prototype) -> None:
    assert result_prototype["id"] == expected_prototype.id()
    assert result_prototype["name"] == expected_prototype.name
    assert result_prototype["engine"] == expected_prototype.engine
    assert result_prototype["language"] == expected_prototype.language
    assert result_prototype["description"] == expected_prototype.description
    assert parser.parse(result_prototype["createdAt"]) == expected_prototype.created_at


@pytest.mark.prototype
def test_find_prototypes__without_filter(client, fake_prototype_repository, tenant_id):
    endpoint = f"{V1_API_PREFIX}/prototypes"
    expected_prototypes = []

    for _ in range(3):
        prototype = PrototypeFactory(tenant_id=TenantId(tenant_id))
        fake_prototype_repository.save(prototype)
        expected_prototypes.append(prototype)

    response = client.get(endpoint)

    assert response.status_code == HTTPStatus.OK

    result_prototypes = response.json()["prototypes"]

    assert len(result_prototypes) == len(expected_prototypes)

    for result_prototype, expected_prototype in zip(
        result_prototypes, sorted(expected_prototypes, key=lambda p: p.created_at, reverse=True)
    ):
        compare_prototypes(expected_prototype, result_prototype)


@pytest.mark.prototype
def test_find_prototypes__with_filter(client, fake_prototype_repository, tenant_id):
    ids = []
    engines = set()
    languages = set()
    expected_prototypes = []
    name = uuid4().hex
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() + timedelta(days=1)
    page = 3
    per_page = 2

    for i in range(10):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"{name}{i}",
            created_at=start_date,
        )
        engines.add(prototype.engine)
        languages.add(prototype.language)
        fake_prototype_repository.save(prototype)
        ids.append(prototype.id())
        expected_prototypes.append(prototype)

    for i in range(3):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"{name}{i}",
            created_at=start_date - timedelta(days=3),
        )
        fake_prototype_repository.save(prototype)
        engines.add(prototype.engine)
        languages.add(prototype.language)

    for i in range(3):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"{i}",
            created_at=start_date - timedelta(days=3),
        )
        fake_prototype_repository.save(prototype)
        ids.append(prototype.id())
        engines.add(prototype.engine)
        languages.add(prototype.language)

    for i in range(3):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"{name}{i}",
            created_at=start_date - timedelta(days=3),
        )
        fake_prototype_repository.save(prototype)
        ids.append(prototype.id())
        languages.add(prototype.language)

    for i in range(3):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"{i}",
            created_at=start_date,
        )
        fake_prototype_repository.save(prototype)
        ids.append(prototype.id())
        engines.add(prototype.engine)

    for i in range(3):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"{i}",
            created_at=end_date + timedelta(days=3),
        )
        fake_prototype_repository.save(prototype)
        ids.append(prototype.id())

    for i in range(3):
        fake_prototype_repository.save(
            PrototypeFactory(
                name=f"{i}",
                created_at=end_date,
            ),
        )

    query = make_query(
        page=page,
        per_page=per_page,
        ids=ids,
        name=name,
        start_date=start_date,
        end_date=end_date,
        sorting_field=PrototypeSortingField.NAME,
        sorting_direction=SortingDirection.ASC,
    )
    endpoint = f"{V1_API_PREFIX}/prototypes?{query}"

    response = client.get(endpoint)

    assert response.status_code == HTTPStatus.OK

    result_prototypes = response.json()["prototypes"]

    first_item_index = (page - 1) * per_page
    expected_prototypes = sorted(expected_prototypes, key=lambda p: p.name)[
        first_item_index : first_item_index + per_page
    ]

    assert len(result_prototypes) == len(expected_prototypes)

    for result_prototype, expected_prototype in zip(result_prototypes, expected_prototypes):
        compare_prototypes(expected_prototype, result_prototype)


@pytest.mark.prototype
def test_find_prototypes__meta_added(client, prototype_service_mock, tenant_id):
    total: int = randint(0, 100)
    prototype_amount: int = randint(0, 10)
    endpoint = f"{V1_API_PREFIX}/prototypes"
    prototypes = PrototypeFactory.build_batch(prototype_amount, tenant_id=TenantId(tenant_id))
    expected_meta = {"size": len(prototypes), "total": total}
    prototype_service_mock.find_prototypes.return_value = prototypes, expected_meta

    response = client.get(endpoint)

    assert response.status_code == HTTPStatus.OK

    assert response.json()["meta"] == expected_meta
