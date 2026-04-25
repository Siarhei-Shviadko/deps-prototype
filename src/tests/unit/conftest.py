import json
from copy import deepcopy
from random import randint
from typing import Any
from uuid import uuid4

import pytest
from deps_extracted_data import ExtractedDataFactory
from deps_message_flow.commands.common import CommandMessageHeaders
from deps_message_flow.commands.consumer import CommandMessage
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_prototype.application import IDocumentTypeProxy, IExtractionProxy
from deps_prototype.domain.model import (
    DataTypeCode,
    DocumentLayout,
    IPrototypeRepository,
    IReferenceLayoutRepository,
    LayoutState,
    Mapping,
    MappingType,
    Prototype,
    UniqueList,
)
from deps_prototype.messaging.sagas_data import (
    PrototypeCreationSteps,
    ReferenceLayoutProcessingSteps,
)
from tests.factories import MappingFactory, ReferenceLayoutFactory
from tests.fakes import (
    FakeMappingRepository,
    FakePrototypeRepository,
    FakeQueryPrototypeRepository,
    FakeReferenceLayoutRepository,
    FakeSagaInstanceRepository,
    FakeStorageService,
    FakeTabularMappingRepository,
)

FIRST_ELEMENT: int = 0


@pytest.fixture
def postgres_datasource_mock(mocker, containers):
    mock = mocker.Mock(containers.datasources.postgres_datasource())
    containers.datasources.postgres_datasource.override(mock)

    yield mock

    containers.datasources.reset_override()


@pytest.fixture(autouse=True)
def fake_prototype_repository(containers):
    with containers.repositories.prototype.override(FakePrototypeRepository()) as repo:
        yield repo()


@pytest.fixture
def prototype_repository_mock(containers, mocker):
    with containers.repositories.prototype.override(mocker.Mock(containers.repositories.prototype.cls)) as repo:
        yield repo()


@pytest.fixture(autouse=True)
def fake_query_prototype_repository(containers):
    with containers.repositories.query_prototype.override(FakeQueryPrototypeRepository()) as repo:
        yield repo()


@pytest.fixture(autouse=True)
def fake_mapping_repository(containers):
    with containers.repositories.mapping.override(FakeMappingRepository()) as repo:
        yield repo()


@pytest.fixture(autouse=True)
def fake_tabular_mapping_repository(containers):
    with containers.repositories.tabular_mapping.override(FakeTabularMappingRepository()) as repo:
        yield repo()


@pytest.fixture(autouse=True)
def fake_reference_layout_repository(containers):
    with containers.repositories.reference_layout.override(FakeReferenceLayoutRepository()) as repo:
        yield repo()


@pytest.fixture
def mapping_repository_mock(containers, mocker):
    with containers.repositories.mapping.override(mocker.Mock(containers.repositories.mapping.cls)) as repo:
        yield repo()


@pytest.fixture(autouse=True)
def fake_saga_instance_repository(containers):
    with containers.repositories.saga_instance.override(FakeSagaInstanceRepository()) as dep:
        yield dep()


@pytest.fixture()
def mapping_service_mock(application, mocker):
    with application.mapping.override(mocker.Mock(application.mapping.cls)) as service:
        yield service()


@pytest.fixture()
def tabular_mapping_service_mock(application, mocker):
    with application.tabular_mapping.override(mocker.Mock(application.tabular_mapping.cls)) as service:
        yield service()


@pytest.fixture()
def prototype_service_mock(application, mocker):
    with application.prototype.override(mocker.Mock(application.prototype.cls)) as service:
        yield service()


@pytest.fixture()
def query_prototype_service_mock(application, mocker):
    with application.query_prototype.override(mocker.Mock(application.query_prototype.cls)) as service:
        yield service()


@pytest.fixture()
def reference_layout_service(containers):
    return containers.reference_layout()


@pytest.fixture()
def reference_layout_service_mock(containers, mocker):
    with containers.reference_layout.override(mocker.Mock(containers.reference_layout.cls)) as service:
        yield service()


@pytest.fixture()
def reference_layout_with_sagas_service_mock(application, mocker):
    with application.reference_layout_with_sagas.override(
        mocker.Mock(application.reference_layout_with_sagas.cls)
    ) as service:
        yield service()


@pytest.fixture(autouse=True)
def fake_file_storage_proxy(containers):
    with containers.services.file_storage.override(FakeStorageService()) as service:
        yield service()


@pytest.fixture()
def extraction_service(application):
    return application.extraction()


@pytest.fixture()
def extraction_service_mock(application, mocker):
    with application.extraction.override(mocker.Mock(application.extraction.cls)) as service:
        yield service()


@pytest.fixture()
def extraction_proxy(services):
    return services.extraction()


@pytest.fixture()
def extraction_proxy_mock(services, mocker):
    with services.extraction.override(mocker.Mock(services.extraction.cls)) as proxy:
        yield proxy()


@pytest.fixture()
def parsing_proxy(services):
    return services.parsing()


@pytest.fixture()
def parsing_proxy_mock(services, mocker):
    with services.parsing.override(mocker.Mock(services.parsing.cls)) as proxy:
        yield proxy()


@pytest.fixture()
def document_proxy(services):
    return services.document()


@pytest.fixture()
def document_proxy_mock(services, mocker):
    with services.document.override(mocker.Mock(services.document.cls)) as proxy:
        yield proxy()


@pytest.fixture
def saved_prototype(prototype: Prototype, fake_prototype_repository: IPrototypeRepository) -> Prototype:
    fake_prototype_repository.save(prototype)

    return prototype


@pytest.fixture
def saved_reference_layout(reference_layout, fake_reference_layout_repository):
    fake_reference_layout_repository.save(reference_layout)

    return reference_layout


@pytest.fixture
def failed_saved_reference_layout(prototype, fake_reference_layout_repository, test_layout_title):
    layout = prototype.add_reference_layout(
        state=LayoutState("Failed"),
        blob_name=uuid4().hex,
        title=test_layout_title,
    )
    fake_reference_layout_repository.save(layout)

    return layout


@pytest.fixture(params=["New", "Unification", "Parsing", "Ready"])
def saved_reference_layout_in_unrestarted_state(
    request, prototype, fake_reference_layout_repository, test_layout_title
):
    layout = prototype.add_reference_layout(
        state=LayoutState(request.param),
        blob_name=uuid4().hex,
        title=test_layout_title,
    )
    fake_reference_layout_repository.save(layout)

    return layout


@pytest.fixture
def saved_reference_layouts(fake_reference_layout_repository: IReferenceLayoutRepository, prototype):
    layouts = ReferenceLayoutFactory.build_batch(size=3, prototype_id=prototype.id)
    for layout in layouts:
        fake_reference_layout_repository.save(layout)

    return layouts


@pytest.fixture
def prototype_deleted_envelope(mocker, prototype):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event.prototype_id = prototype.id()
    dee.event.tenant_id = prototype.tenant_id()

    return dee


@pytest.fixture
def prototype_creation_steps(
    fake_document_type_service: IDocumentTypeProxy,
    fake_extraction_proxy: IExtractionProxy,
    fake_prototype_repository: IPrototypeRepository,
    fake_domain_event_publisher,
):
    return PrototypeCreationSteps(
        document_type_service=fake_document_type_service,
        extraction_service=fake_extraction_proxy,
        prototype_repository=fake_prototype_repository,
        domain_event_publisher=fake_domain_event_publisher,
    )


@pytest.fixture
def reference_layout_processing_steps(reference_layout_service):
    return ReferenceLayoutProcessingSteps(
        reference_layout_service=reference_layout_service,
    )


@pytest.fixture
def document_id():
    return randint(1, 99)


@pytest.fixture
def perform_prototype_extraction_command_message(mocker, saved_prototype, tenant_id, document_id):
    cm = mocker.Mock(CommandMessage)
    cm.command.prototype_id = saved_prototype.id()
    cm.command.tenant_id = tenant_id
    cm.command.document_id = document_id
    cm.command.language = None
    cm.command.engine = None
    cm.message.headers = {CommandMessageHeaders.REPLY_TO: "TestDestination"}

    return cm


@pytest.fixture
def document_layout_dict():
    with open("tests/data/document_layout.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture
def document_layout_merged_cells_dict():
    with open("tests/data/azure-merged-cells-tables.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture
def document_layout(document_layout_dict):
    return deepcopy(DocumentLayout.from_dict(document_layout_dict))


@pytest.fixture
def document_layout_merged_cells(document_layout_merged_cells_dict: dict[str, Any]) -> DocumentLayout:
    return deepcopy(DocumentLayout.from_dict(document_layout_merged_cells_dict))


@pytest.fixture
def extracted_data(document_id):
    return ExtractedDataFactory.make_extracted_data(document_id=document_id)


@pytest.fixture
def string_mapping(prototype: Prototype) -> Mapping:
    return MappingFactory(
        mapping_type=MappingType.ONE_TO_ONE,
        keys=UniqueList(["airway bill no."]),
        data_type=DataTypeCode.STRING,
        prototype_id=prototype.id(),
    )


@pytest.fixture
def checkmark_mapping(prototype: Prototype) -> Mapping:
    return MappingFactory(
        mapping_type=MappingType.ONE_TO_ONE,
        keys=UniqueList(["Checked"]),
        data_type=DataTypeCode.CHECKMARK,
        prototype_id=prototype.id(),
    )


@pytest.fixture
def mappings(string_mapping: Mapping, checkmark_mapping: Mapping) -> list[Mapping]:
    return [string_mapping, checkmark_mapping]


@pytest.fixture
def saved_mappings(fake_mapping_repository, mappings: list[Mapping]) -> list[Mapping]:
    for mapping in mappings:
        fake_mapping_repository.save(mapping)

    return mappings


@pytest.fixture
def key_value_pairs(document_layout):
    return list(document_layout.key_value_pairs)


@pytest.fixture
def key_value_pair(key_value_pairs):
    return key_value_pairs[FIRST_ELEMENT]


@pytest.fixture
def key_value_pair_with_checkmark(key_value_pairs):
    return key_value_pairs[1]
