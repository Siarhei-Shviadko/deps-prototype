import random
from pathlib import Path
from random import choice
from uuid import uuid4

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from deps_prototype import api
from deps_prototype.domain.model import (
    AllocatedTable,
    DataTypeCode,
    DocumentLayout,
    Header,
    HeaderType,
    LayoutState,
    Mapping,
    MappingType,
    Prototype,
    PrototypeFactory,
    PrototypeWithMappings,
    ReferenceLayout,
    TabularMapping,
)
from deps_prototype.entrypoint import create_fastapi
from deps_prototype.infrastructure.access_management.context_vars import user
from tests.factories import MappingFactory, TabularMappingFactory
from tests.fakes import (
    FakeCommandProducer,
    FakeDocumentTypeProxy,
    FakeDomainEventPublisher,
    FakeExtractionProxy,
)

FIRST_ELEMENT: int = 0
SECOND_ELEMENT: int = 1


@pytest.fixture(scope="session")
def app() -> FastAPI:
    fastapi_app = create_fastapi()
    yield fastapi_app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def session_containers(app):
    return app.containers


@pytest.fixture
def containers(session_containers):
    with session_containers.reset_singletons():
        yield session_containers


@pytest.fixture
def config(containers):
    return containers.config


@pytest.fixture
def repositories(session_containers):
    return session_containers.repositories


@pytest.fixture
def prototype_repository(repositories):
    return repositories.prototype()


@pytest.fixture
def query_prototype_repository(repositories):
    return repositories.query_prototype()


@pytest.fixture
def mapping_repository(repositories):
    return repositories.mapping()


@pytest.fixture
def tabular_mapping_repository(repositories):
    return repositories.tabular_mapping()


@pytest.fixture
def reference_layout_repository(repositories):
    return repositories.reference_layout()


@pytest.fixture
def application(session_containers):
    return session_containers.application


@pytest.fixture
def services(containers):
    return containers.services


@pytest.fixture
def saga_steps(containers):
    return containers.saga_steps


@pytest.fixture
def prototype_service(application):
    return application.prototype()


@pytest.fixture
def query_prototype_service(application):
    return application.query_prototype()


@pytest.fixture
def mapping_service(application):
    return application.mapping()


@pytest.fixture
def tabular_mapping_service(application):
    return application.tabular_mapping()


@pytest.fixture
def unified_mapping_service(application):
    return application.unified_mapping()


@pytest.fixture
def reference_layout_service(session_containers):
    return session_containers.reference_layout()


@pytest.fixture
def reference_layout_with_sagas_service(application):
    return application.reference_layout_with_sagas()


@pytest.fixture(autouse=True)
def fake_document_type_service(containers):
    with containers.services.document_type_service.override(FakeDocumentTypeProxy()) as dep:
        yield dep()


@pytest.fixture(autouse=True)
def fake_extraction_proxy(containers):
    with containers.services.extraction.override(FakeExtractionProxy()) as dep:
        yield dep()


@pytest.fixture(autouse=True)
def fake_domain_event_publisher(containers):
    with containers.domain_event_publisher.override(FakeDomainEventPublisher()) as dep:
        yield dep()
        del dep().last_published


@pytest.fixture(autouse=True)
def fake_command_producer(containers):
    with containers.command_producer.override(FakeCommandProducer()) as cp:
        yield cp()
        del cp().sent


@pytest.fixture
def test_command_channel():
    return None


@pytest.fixture
def tenant_id():
    return uuid4().hex


@pytest.fixture
def prototype_id():
    return uuid4().hex


@pytest.fixture
def layout_id():
    return uuid4().hex


@pytest.fixture
def language():
    return uuid4().hex


@pytest.fixture
def name():
    return uuid4().hex


@pytest.fixture
def engine():
    return uuid4().hex


@pytest.fixture
def description():
    return uuid4().hex


@pytest.fixture
def this_user(tenant_id):
    return dict(
        subject="Test",
        groups=[tenant_id],
        token="token",
        roles=[],
        organisation=tenant_id,
    )


@pytest.fixture(autouse=True)
def set_this_user(this_user):
    user.set(this_user)


@pytest.fixture(autouse=True)
def mocked_middleware(monkeypatch, mocker):
    monkeypatch.setattr(api.auth, "set_user_from_token", mocker.Mock({}))


@pytest.fixture
def create_mapping_payload():
    return {
        "code": uuid4().hex,
        "typeCode": choice(list(DataTypeCode)).value,
        "keys": [uuid4().hex for _ in range(3)],
        "mappingType": choice(list(MappingType)).value,
    }


@pytest.fixture
def create_tabular_mapping_payload():
    return {
        "code": "test",
        "headerType": choice(list(HeaderType)).value,
        "headers": [
            {
                "name": uuid4().hex,
                "aliases": [uuid4().hex, uuid4().hex],
            }
            for _ in range(random.randint(1, 5))
        ],
        "occurrenceIndex": random.randint(-10, 10),
    }


@pytest.fixture
def create_reference_layout_payload():
    return {
        "state": choice(list(LayoutState)).value,
        "blob_name": uuid4().hex,
    }


@pytest.fixture
def modify_mapping_payload():
    return {
        "keys": [uuid4().hex for _ in range(3)],
    }


@pytest.fixture
def prototype(tenant_id, prototype_id) -> Prototype:
    return PrototypeFactory.make(
        id_=prototype_id,
        tenant_id=tenant_id,
        name=uuid4().hex,
        engine="AZURE_FORM_RECOGNIZER",
        language="eng",
        description="Prototype description",
    )


@pytest.fixture
def mapping(prototype: Prototype) -> Mapping:
    return MappingFactory(prototype_id=prototype.id())


@pytest.fixture
def tabular_mapping(prototype: Prototype) -> Mapping:
    return TabularMappingFactory(prototype_id=prototype.id)


@pytest.fixture
def prototype_with_mappings(
    prototype: Prototype,
    mapping: Mapping,
    tabular_mapping: TabularMapping,
) -> PrototypeWithMappings:
    return PrototypeWithMappings(
        prototype=prototype,
        mappings=[mapping],
        tabular_mappings=[tabular_mapping],
    )


@pytest.fixture
def test_file_name():
    return uuid4().hex


@pytest.fixture
def test_layout_title(test_file_name):
    return Path(test_file_name).stem


@pytest.fixture
def test_file_content() -> bytes:
    return b"a new test document file content"


@pytest.fixture
def reference_layout(prototype, create_reference_layout_payload, test_layout_title) -> ReferenceLayout:
    return prototype.add_reference_layout(
        state=LayoutState(create_reference_layout_payload["state"]),
        blob_name=create_reference_layout_payload["blob_name"],
        title=test_layout_title,
    )


@pytest.fixture
def tabular_mapping__row_headers() -> TabularMapping:
    return TabularMappingFactory(
        occurrence_index=0,
        header_type=HeaderType.ROWS,
    )


@pytest.fixture
def tabular_mapping__column_headers() -> TabularMapping:
    return TabularMappingFactory(
        occurrence_index=0,
        header_type=HeaderType.COLUMNS,
    )


@pytest.fixture
def tabular_mapping__specific_table__row_oriented(tabular_mapping__row_headers: TabularMapping) -> TabularMapping:
    tabular_mapping__row_headers.occurrence_index = 0
    tabular_mapping__row_headers.headers = [Header(name=uuid4().hex, aliases={"ADDRESS"})]

    return tabular_mapping__row_headers


@pytest.fixture
def tabular_mapping__specific_table__column_oriented(tabular_mapping__column_headers: TabularMapping) -> TabularMapping:
    tabular_mapping__column_headers.occurrence_index = 0
    tabular_mapping__column_headers.headers = [
        Header(name=uuid4().hex, aliases={"amount"}),
        Header(name=uuid4().hex, aliases={"qty"}),
    ]

    return tabular_mapping__column_headers


@pytest.fixture
def test_allocated_table__row(
    document_layout: DocumentLayout,
    tabular_mapping__specific_table__row_oriented: TabularMapping,
) -> AllocatedTable:
    return tabular_mapping__specific_table__row_oriented.search_data(document_layout)


@pytest.fixture
def test_allocated_table__column(
    document_layout: DocumentLayout,
    tabular_mapping__specific_table__column_oriented: TabularMapping,
) -> AllocatedTable:
    return tabular_mapping__specific_table__column_oriented.search_data(document_layout)
