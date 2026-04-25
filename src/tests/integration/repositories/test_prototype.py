from datetime import datetime, timedelta
from random import randint
from uuid import uuid4

import pytest

from deps_prototype.domain.exceptions import InvariantViolation
from deps_prototype.domain.model import (
    PrototypeFilter,
    PrototypeSortingField,
    SortingDirection,
    TenantId,
)
from tests.factories import PrototypeFactory


def test_prototype_repository__save__find__delete(prototype_repository):
    prototype = PrototypeFactory()

    prototype_repository.save(prototype)

    assert prototype_repository.has_prototype_of_id(id_=prototype.id(), tenant_id=prototype.tenant_id())
    assert prototype_repository.prototype_of_id(id_=prototype.id(), tenant_id=prototype.tenant_id()) == prototype

    prototype_repository.delete(prototype)

    assert not prototype_repository.has_prototype_of_id(id_=prototype.id(), tenant_id=prototype.tenant_id())
    assert prototype_repository.prototype_of_id(id_=prototype.id(), tenant_id=prototype.tenant_id()) is None


def test_save__same_name__error(prototype_repository, tenant_id):
    name = uuid4().hex
    tenant_id = TenantId(tenant_id)
    prototype_repository.save(PrototypeFactory(name=name, tenant_id=tenant_id))

    with pytest.raises(InvariantViolation):
        prototype_repository.save(PrototypeFactory(name=name, tenant_id=tenant_id))


def test_prototype_repository__find_by_filter__tenant_id(prototype_repository):
    expected_prototypes = []

    tenant_id = uuid4().hex

    for _ in range(3):
        prototype = PrototypeFactory(tenant_id=TenantId(tenant_id))
        prototype_repository.save(prototype)
        expected_prototypes.append(prototype)

    for _ in range(3):
        prototype = PrototypeFactory()
        prototype_repository.save(prototype)

    result_prototypes = prototype_repository.find_by_filter(
        PrototypeFilter(
            tenant_id=tenant_id,
            sorting_field=PrototypeSortingField.NAME,
            sorting_direction=SortingDirection.ASC,
        )
    )

    assert result_prototypes == sorted(expected_prototypes, key=lambda p: p.name)


def test_prototype_repository__find_by_filter__name(prototype_repository):
    name = uuid4().hex
    expected_prototypes = []

    for i in range(3):
        prototype = PrototypeFactory(name=f"{i}{name}{i}")
        prototype_repository.save(prototype)
        expected_prototypes.append(prototype)

    for i in range(3):
        prototype = PrototypeFactory(name=f"{i}{i}")
        prototype_repository.save(prototype)

    result_prototypes = prototype_repository.find_by_filter(
        PrototypeFilter(
            name=name,
            sorting_field=PrototypeSortingField.ID,
            sorting_direction=SortingDirection.DESC,
        )
    )

    assert result_prototypes == sorted(expected_prototypes, key=lambda p: p.id(), reverse=True)


def test_prototype_repository__find_by_filter__language(prototype_repository):
    languages = [uuid4().hex, uuid4().hex, uuid4().hex]
    expected_prototypes = []

    for i in range(3):
        prototype = PrototypeFactory(language=languages[i])
        prototype_repository.save(prototype)
        expected_prototypes.append(prototype)

    for i in range(3):
        prototype = PrototypeFactory()
        prototype_repository.save(prototype)

    result_prototypes = prototype_repository.find_by_filter(
        PrototypeFilter(
            languages=languages,
            sorting_field=PrototypeSortingField.ENGINE,
            sorting_direction=SortingDirection.ASC,
        )
    )

    assert result_prototypes == sorted(expected_prototypes, key=lambda p: p.engine)


def test_prototype_repository__find_by_filter__engines(prototype_repository):
    engines = [uuid4().hex, uuid4().hex, uuid4().hex]
    expected_prototypes = []

    for i in range(3):
        prototype = PrototypeFactory(engine=engines[i])
        prototype_repository.save(prototype)
        expected_prototypes.append(prototype)

    for i in range(3):
        prototype = PrototypeFactory()
        prototype_repository.save(prototype)

    result_prototypes = prototype_repository.find_by_filter(
        PrototypeFilter(
            engines=engines,
            sorting_field=PrototypeSortingField.LANGUAGE,
            sorting_direction=SortingDirection.ASC,
        )
    )

    assert result_prototypes == sorted(expected_prototypes, key=lambda p: p.language)


def test_prototype_repository__find_by_filter__ids(prototype_repository):
    ids = []
    expected_prototypes = []

    for i in range(3):
        prototype = PrototypeFactory()
        ids.append(prototype.id())
        prototype_repository.save(prototype)
        expected_prototypes.append(prototype)

    for i in range(3):
        prototype = PrototypeFactory()
        prototype_repository.save(prototype)

    result_prototypes = prototype_repository.find_by_filter(
        PrototypeFilter(
            ids=ids,
            sorting_field=PrototypeSortingField.CREATED_AT,
            sorting_direction=SortingDirection.DESC,
        )
    )

    assert result_prototypes == sorted(expected_prototypes, key=lambda p: p.created_at, reverse=True)


def test_prototype_repository__find_by_filter__creation_date(prototype_repository):
    tenant_id = uuid4().hex
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() + timedelta(days=1)

    expected_prototypes = []

    for i in range(3):
        prototype = PrototypeFactory(tenant_id=TenantId(tenant_id), created_at=datetime.now())
        prototype_repository.save(prototype)
        expected_prototypes.append(prototype)

    for i in range(3):
        prototype = PrototypeFactory(tenant_id=TenantId(tenant_id), created_at=end_date + timedelta(days=1))
        prototype_repository.save(prototype)

    for i in range(3):
        prototype = PrototypeFactory(tenant_id=TenantId(tenant_id), created_at=start_date - timedelta(days=1))
        prototype_repository.save(prototype)

    result_prototypes = prototype_repository.find_by_filter(
        PrototypeFilter(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            sorting_field=PrototypeSortingField.CREATED_AT,
            sorting_direction=SortingDirection.DESC,
        )
    )

    assert result_prototypes == sorted(expected_prototypes, key=lambda p: p.created_at, reverse=True)


def test_prototype_repository__find_by_filter__pagination(prototype_repository):
    tenant_id = uuid4().hex
    expected_prototypes = []
    page = 2
    per_page = 3

    for i in range(10):
        prototype = PrototypeFactory(tenant_id=TenantId(tenant_id))
        prototype_repository.save(prototype)
        expected_prototypes.append(prototype)

    result_prototypes = prototype_repository.find_by_filter(
        PrototypeFilter(
            tenant_id=tenant_id,
            page=page,
            per_page=per_page,
            sorting_field=PrototypeSortingField.CREATED_AT,
            sorting_direction=SortingDirection.DESC,
        )
    )

    first_item_index = (page - 1) * per_page
    assert (
        result_prototypes
        == sorted(expected_prototypes, key=lambda p: p.created_at, reverse=True)[
            first_item_index : first_item_index + per_page
        ]
    )

    page = 100

    result_prototypes = prototype_repository.find_by_filter(
        PrototypeFilter(
            tenant_id=tenant_id,
            page=page,
            per_page=per_page,
            sorting_field=PrototypeSortingField.CREATED_AT,
            sorting_direction=SortingDirection.DESC,
        )
    )

    assert result_prototypes == []


def test_get_total_count_by_filter__prototypes_dont_exist__0(prototype_repository, tenant_id):
    prototypes = PrototypeFactory.build_batch(randint(1, 10))
    for prototype in prototypes:
        prototype_repository.save(prototype)

    res = prototype_repository.get_total_count_by_filter(PrototypeFilter(tenant_id=tenant_id))

    assert res == 0


def test_get_total_count_by_filter__prototypes_exist__not_0(
    prototype_repository,
    tenant_id,
    engine,
    language,
):
    prototype_amount: int = randint(20, 40)
    prototypes = PrototypeFactory.build_batch(
        prototype_amount,
        tenant_id=TenantId(tenant_id),
        engine=engine,
        language=language,
    )
    for prototype in prototypes:
        prototype_repository.save(prototype)

    filter_ = PrototypeFilter(
        tenant_id=tenant_id,
        engines=[engine],
        languages=[language],
    )

    res = prototype_repository.get_total_count_by_filter(filter_)

    assert res == prototype_amount


def test_get_total_count_by_filter__prototypes_not_exist_by_filter(
    prototype_repository,
    tenant_id,
    engine,
    language,
):
    prototype_amount: int = randint(20, 40)
    prototypes = PrototypeFactory.build_batch(
        prototype_amount,
        tenant_id=TenantId(tenant_id),
        engine=engine,
        language=language,
    )
    for prototype in prototypes:
        prototype_repository.save(prototype)

    filter_ = PrototypeFilter(
        name=uuid4().hex,
        tenant_id=tenant_id,
        engines=[engine],
        languages=[language],
    )

    res = prototype_repository.get_total_count_by_filter(filter_)

    assert res == 0
