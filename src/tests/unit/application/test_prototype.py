from random import randint
from uuid import uuid4

import pytest

from deps_prototype.application import PrototypeService
from deps_prototype.constants import PROTOTYPE_AGGREGATE_TYPE
from deps_prototype.domain.exceptions import PrototypeHasDocument, PrototypeNotFound
from deps_prototype.domain.model import (
    IMappingRepository,
    IPrototypeRepository,
    Mapping,
    Pagination,
    Prototype,
    PrototypeDeleted,
    PrototypeUpdated,
    TenantId,
)
from tests.factories import PrototypeFactory
from tests.fakes.domain_event_publisher import Events

__all__ = ["compare_prototype_entities", "compare_mappings_entities"]


def compare_prototype_entities(prototype1, prototype2):
    assert prototype1 == prototype2
    assert prototype1.tenant_id == prototype2.tenant_id
    assert prototype1.name == prototype2.name
    assert prototype1.engine == prototype2.engine
    assert prototype1.language == prototype2.language
    assert prototype1.description == prototype2.description


def compare_mappings_entities(mapping1: Mapping, mapping2: Mapping) -> None:
    assert mapping1 == mapping2
    assert mapping1.prototype_id == mapping2.prototype_id
    assert mapping1.data_type == mapping2.data_type
    assert mapping1.mapping_type == mapping2.mapping_type
    assert mapping1.keys == mapping2.keys


@pytest.mark.prototype
def test_update__prototype_doesnt_exists__not_found_error(
    prototype: Prototype,
    prototype_service: PrototypeService,
) -> None:
    with pytest.raises(PrototypeNotFound):
        prototype_service.update_prototype(
            id_=prototype.id(),
            tenant_id=prototype.tenant_id(),
            engine=prototype.engine,
            language=prototype.language,
            description=prototype.description,
        )


@pytest.mark.prototype
def test_update__prototype_exists__updated(
    prototype: Prototype,
    fake_prototype_repository: IPrototypeRepository,
    prototype_service: PrototypeService,
    fake_domain_event_publisher,
):
    fake_prototype_repository.save(prototype)
    new_prototype = PrototypeFactory(id_=prototype.id, tenant_id=prototype.tenant_id)

    updated_prototype = prototype_service.update_prototype(
        id_=new_prototype.id(),
        tenant_id=new_prototype.tenant_id(),
        engine=new_prototype.engine,
        language=new_prototype.language,
        description=new_prototype.description,
    )

    assert updated_prototype.engine == new_prototype.engine
    assert updated_prototype.language == new_prototype.language
    assert updated_prototype.description == new_prototype.description

    updated_prototype = fake_prototype_repository.prototype_of_id(prototype.id(), prototype.tenant_id())
    assert updated_prototype.engine == new_prototype.engine
    assert updated_prototype.language == new_prototype.language
    assert updated_prototype.description == new_prototype.description

    last_published: Events = fake_domain_event_publisher.last_published
    assert last_published.aggregate_id == new_prototype.id()
    assert last_published.aggregate_type == PROTOTYPE_AGGREGATE_TYPE
    assert last_published.events == [
        PrototypeUpdated(
            prototype_id=new_prototype.id(),
            tenant_id=new_prototype.tenant_id(),
            engine=new_prototype.engine,
            language=new_prototype.language,
            description=new_prototype.description,
        ),
    ]


@pytest.mark.prototype
def test_find_prototype__prototype_doesnt_exist__error(
    prototype: Prototype,
    prototype_service: PrototypeService,
    fake_prototype_repository: IPrototypeRepository,
    fake_mapping_repository: IMappingRepository,
):
    with pytest.raises(PrototypeNotFound):
        prototype_service.find_prototype(prototype.id(), prototype.tenant_id())


@pytest.mark.prototype
def test_find_prototype__prototype_exists__ok(
    mapping: Mapping,
    prototype: Prototype,
    fake_prototype_repository: IPrototypeRepository,
    fake_mapping_repository: IMappingRepository,
    prototype_service: PrototypeService,
) -> None:
    fake_prototype_repository.save(prototype)
    fake_mapping_repository.save(mapping)

    saved_prototype, saved_mappings = prototype_service.find_prototype(prototype.id(), prototype.tenant_id())

    compare_prototype_entities(saved_prototype, prototype)
    compare_mappings_entities(saved_mappings[0], mapping)


@pytest.mark.prototype
def test_delete_prototype__prototype_doesnt_exist__no_event(
    prototype: Prototype,
    prototype_service: PrototypeService,
    fake_prototype_repository: IPrototypeRepository,
    fake_domain_event_publisher,
):
    prototype_service.delete_prototype(prototype.id(), prototype.tenant_id())

    assert fake_domain_event_publisher.last_published is None


@pytest.mark.prototype
def test_delete_prototype__prototype_exists__deleted(
    prototype: Prototype,
    document_proxy_mock,
    prototype_service: PrototypeService,
    fake_prototype_repository: IPrototypeRepository,
    fake_domain_event_publisher,
):
    fake_prototype_repository.save(prototype)
    document_proxy_mock.get_prototype_ids_with_documents.return_value = []
    event = PrototypeDeleted(prototype_id=prototype.id(), tenant_id=prototype.tenant_id())
    assert fake_prototype_repository.prototype_of_id(prototype.id(), prototype.tenant_id())

    prototype_service.delete_prototype(prototype.id(), prototype.tenant_id())

    assert fake_prototype_repository.prototype_of_id(prototype.id(), prototype.tenant_id()) is None
    assert fake_domain_event_publisher.last_published.events == [event]
    document_proxy_mock.get_prototype_ids_with_documents.assert_called_once_with([prototype.id()])


@pytest.mark.prototype
def test_delete_prototype__prototype_exists__document_exists__not_deleted_no_events(
    prototype: Prototype,
    document_proxy_mock,
    prototype_service: PrototypeService,
    fake_prototype_repository: IPrototypeRepository,
    fake_domain_event_publisher,
):
    document_proxy_mock.get_prototype_ids_with_documents.return_value = [uuid4().hex]
    fake_prototype_repository.save(prototype)

    with pytest.raises(PrototypeHasDocument):
        prototype_service.delete_prototype(prototype.id(), prototype.tenant_id())

    assert fake_domain_event_publisher.last_published is None
    document_proxy_mock.get_prototype_ids_with_documents.assert_called_once_with([prototype.id()])


@pytest.mark.prototype
def test_delete_prototypes__prototype_doesnt_exist__no_event(
    prototype: Prototype,
    prototype_service: PrototypeService,
    fake_prototype_repository: IPrototypeRepository,
    fake_domain_event_publisher,
):
    prototype1 = PrototypeFactory()
    fake_prototype_repository.save(prototype1)

    prototype_service.delete_prototypes([prototype.id()], prototype.tenant_id())

    assert fake_domain_event_publisher.last_published is None
    assert prototype1 == fake_prototype_repository.prototype_of_id(prototype1.id(), prototype1.tenant_id())


@pytest.mark.prototype
def test_delete_prototypes__prototypes_exist__deleted_only_for_tenant(
    prototype,
    document_proxy_mock,
    prototype_service: PrototypeService,
    fake_prototype_repository: IPrototypeRepository,
    fake_domain_event_publisher,
):
    document_proxy_mock.get_prototype_ids_with_documents.return_value = []
    prototype1 = PrototypeFactory(tenant_id=prototype.tenant_id)
    prototype2 = PrototypeFactory()
    fake_prototype_repository.save(prototype)
    fake_prototype_repository.save(prototype1)
    fake_prototype_repository.save(prototype2)
    event = PrototypeDeleted(prototype_id=prototype.id(), tenant_id=prototype.tenant_id())
    assert fake_prototype_repository.prototype_of_id(prototype.id(), prototype.tenant_id())
    assert fake_prototype_repository.prototype_of_id(prototype1.id(), prototype1.tenant_id())
    assert fake_prototype_repository.prototype_of_id(prototype2.id(), prototype2.tenant_id())

    prototype_service.delete_prototypes([prototype.id(), prototype2.id()], prototype.tenant_id())

    assert fake_prototype_repository.prototype_of_id(prototype.id(), prototype.tenant_id()) is None
    assert fake_prototype_repository.prototype_of_id(prototype1.id(), prototype1.tenant_id())
    assert fake_prototype_repository.prototype_of_id(prototype2.id(), prototype2.tenant_id())
    assert fake_domain_event_publisher.last_published.events == [event]
    document_proxy_mock.get_prototype_ids_with_documents.assert_called_once_with([prototype.id(), prototype2.id()])


@pytest.mark.prototype
def test_delete_prototypes__prototypes_exist__document_exists__not_deleted_no_events(
    prototype,
    document_proxy_mock,
    prototype_service: PrototypeService,
    fake_prototype_repository: IPrototypeRepository,
    fake_domain_event_publisher,
):
    document_proxy_mock.get_prototype_ids_with_documents.return_value = [uuid4().hex]
    fake_prototype_repository.save(prototype)

    with pytest.raises(PrototypeHasDocument):
        prototype_service.delete_prototypes([prototype.id()], prototype.tenant_id())

    assert fake_domain_event_publisher.last_published is None
    document_proxy_mock.get_prototype_ids_with_documents.assert_called_once_with([prototype.id()])


@pytest.mark.prototype
def test_list_meta__prototypes_exist__pagination_unset__ok(
    tenant_id,
    prototype,
    fake_prototype_repository: IPrototypeRepository,
    prototype_service: PrototypeService,
):
    prototype_amount: int = randint(20, 40)
    prototypes = PrototypeFactory.build_batch(prototype_amount, tenant_id=TenantId(tenant_id))
    expected_meta = {"size": prototype_amount, "total": prototype_amount}
    for prototype in prototypes:
        fake_prototype_repository.save(prototype)

    gotten_prototypes, meta = prototype_service.find_prototypes(tenant_id=tenant_id)

    assert len(gotten_prototypes) == prototype_amount
    assert meta == expected_meta


@pytest.mark.prototype
def test_list_meta__prototypes_exist__pagination_set__ok(
    tenant_id,
    prototype,
    fake_prototype_repository: IPrototypeRepository,
    prototype_service: PrototypeService,
):
    prototype_amount: int = randint(20, 40)
    prototypes = PrototypeFactory.build_batch(prototype_amount, tenant_id=TenantId(tenant_id))
    expected_meta = {"size": Pagination.per_page, "total": prototype_amount}
    for prototype in prototypes:
        fake_prototype_repository.save(prototype)

    gotten_prototypes, meta = prototype_service.find_prototypes(
        tenant_id=tenant_id,
        page=Pagination.page,
        per_page=Pagination.per_page,
    )

    assert len(gotten_prototypes) == Pagination.per_page
    assert meta == expected_meta


@pytest.mark.prototype
def test_list_meta__prototypes_dont_exist__ok(
    fake_prototype_repository: IPrototypeRepository,
    prototype_service: PrototypeService,
):
    expected_meta = {"size": 0, "total": 0}

    gotten_prototypes, meta = prototype_service.find_prototypes()

    assert not gotten_prototypes
    assert meta == expected_meta
