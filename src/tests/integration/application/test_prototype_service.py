from datetime import datetime, timedelta
from uuid import uuid4

from deps_prototype.application import IExtractionProxy, PrototypeService
from deps_prototype.constants import PROTOTYPE_AGGREGATE_TYPE
from deps_prototype.domain.model import (
    IPrototypeRepository,
    PrototypeCreated,
    PrototypeSortingField,
    SortingDirection,
    TenantId,
)
from tests.factories import PrototypeFactory
from tests.fakes import FakeDocumentTypeProxy, FakeDomainEventPublisher


def test_prototype_service__create_prototype(
    tenant_id: str,
    prototype_service: PrototypeService,
    prototype_repository: IPrototypeRepository,
    fake_domain_event_publisher: FakeDomainEventPublisher,
    fake_document_type_service: FakeDocumentTypeProxy,
    fake_extraction_proxy: IExtractionProxy,
) -> None:
    name = "TestPrototype"
    description = "Test prototype"
    engine = "TESSERACT"
    language = "eng"

    prototype_id = prototype_service.create_prototype(
        tenant_id=tenant_id,
        name=name,
        description=description,
        engine=engine,
        language=language,
    )
    prototype_from_repo = prototype_repository.prototype_of_id(id_=prototype_id, tenant_id=tenant_id)

    assert prototype_from_repo.tenant_id() == tenant_id
    assert prototype_from_repo.name == name
    assert prototype_from_repo.description == description
    assert prototype_from_repo.engine == engine
    assert prototype_from_repo.language == language
    assert prototype_from_repo.created_at is not None

    published_events = fake_domain_event_publisher.last_published

    assert published_events.aggregate_type == PROTOTYPE_AGGREGATE_TYPE
    assert published_events.aggregate_id == prototype_id
    assert isinstance(published_events.events[0], PrototypeCreated)


def test_find_prototypes(
    prototype_service: PrototypeService,
    prototype_repository: IPrototypeRepository,
    fake_domain_event_publisher: FakeDomainEventPublisher,
) -> None:
    tenant_id = uuid4().hex
    engines = set()
    languages = set()
    ids = []
    expected_prototypes = []
    name = uuid4().hex
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() + timedelta(days=1)
    page = 3
    per_page = 2

    for i in range(10):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"a{name}{i}",
            created_at=datetime.now(),
        )
        engines.add(prototype.engine)
        languages.add(prototype.language)
        prototype_repository.save(prototype)
        ids.append(prototype.id())
        expected_prototypes.append(prototype)

    for i in range(3):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"b{name}{i}",
            created_at=start_date - timedelta(days=3),
        )
        engines.add(prototype.engine)
        languages.add(prototype.language)
        prototype_repository.save(prototype)

    for i in range(3):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"c{i}",
            created_at=start_date + timedelta(days=3),
        )
        prototype_repository.save(prototype)
        ids.append(prototype.id())
        engines.add(prototype.engine)
        languages.add(prototype.language)

    for i in range(3):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"e{name}{i}",
            created_at=start_date + timedelta(days=3),
        )
        prototype_repository.save(prototype)
        ids.append(prototype.id())
        languages.add(prototype.language)

    for i in range(3):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"f{i}",
            created_at=start_date - timedelta(days=3),
        )
        engines.add(prototype.engine)
        prototype_repository.save(prototype)
        ids.append(prototype.id())

    for i in range(3):
        prototype = PrototypeFactory(
            tenant_id=TenantId(tenant_id),
            name=f"g{i}",
            created_at=start_date + timedelta(days=3),
        )
        prototype_repository.save(prototype)
        ids.append(prototype.id())

    for i in range(3):
        prototype_repository.save(
            PrototypeFactory(
                name=f"h{i}",
                created_at=start_date + timedelta(days=3),
            ),
        )

    result_prototypes = prototype_service.find_prototypes(
        tenant_id=tenant_id,
        engines=list(engines),
        languages=list(languages),
        ids=ids,
        name=name,
        start_date=start_date,
        end_date=end_date,
        sorting_field=PrototypeSortingField.ID,
        sorting_direction=SortingDirection.ASC,
        page=page,
        per_page=per_page,
    )

    first_item_index = (page - 1) * per_page

    assert (
        result_prototypes[0]
        == sorted(expected_prototypes, key=lambda x: x.id())[first_item_index : first_item_index + per_page]
    )
