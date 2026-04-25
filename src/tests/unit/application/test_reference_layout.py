from unittest import mock

import pytest

from deps_prototype.application import (
    ReferenceLayoutService,
    ReferenceLayoutServiceWithSagas,
)
from deps_prototype.constants import (
    COMMANDS_REPLIES_CHANNEL,
    FILE_STORAGE_COMMANDS_CHANNEL,
    REFERENCE_LAYOUT_AGGREGATE_TYPE,
)
from deps_prototype.domain.exceptions import (
    PrototypeNotFound,
    ReferenceLayoutCreationFailed,
    ReferenceLayoutNotFound,
)
from deps_prototype.domain.model import (
    DeleteFiles,
    IPrototypeRepository,
    IReferenceLayoutRepository,
    Prototype,
    ReferenceLayout,
    ReferenceLayoutDeleted,
)
from tests.fakes import FakeStorageService

FIRST_ELEMENT: int = 0
LAST_ELEMENT: int = -1


@pytest.mark.layouts
def test_find_layouts__success(
    tenant_id: str,
    prototype: Prototype,
    reference_layout: ReferenceLayout,
    fake_prototype_repository: IPrototypeRepository,
    fake_reference_layout_repository: IReferenceLayoutRepository,
    reference_layout_service: ReferenceLayoutService,
):
    fake_prototype_repository.save(prototype)
    fake_reference_layout_repository.save(reference_layout)

    reference_layouts = reference_layout_service.find_layouts(prototype.id(), tenant_id)

    assert len(reference_layouts) == 1
    assert reference_layouts[0] == reference_layout


@pytest.mark.layouts
def test_find_layouts__no_layouts__success(
    tenant_id: str,
    prototype: Prototype,
    fake_prototype_repository: IPrototypeRepository,
    reference_layout_service: ReferenceLayoutService,
):
    fake_prototype_repository.save(prototype)

    reference_layouts = reference_layout_service.find_layouts(prototype.id(), tenant_id)

    assert reference_layouts == []


@pytest.mark.reference_layout
def test_create_reference_layout__prototype_not_exist__error(
    reference_layout_with_sagas_service: ReferenceLayoutServiceWithSagas,
    prototype: Prototype,
    tenant_id: str,
    test_file_name: str,
    test_file_content: bytes,
):
    with pytest.raises(PrototypeNotFound):
        reference_layout_with_sagas_service.create_layout(
            prototype_id=prototype.id(),
            tenant_id=tenant_id,
            file_name=test_file_name,
            file=test_file_content,
        )


@pytest.mark.reference_layout
def test_create_reference_layout__reference_layout_not_saved__error(
    reference_layout_with_sagas_service: ReferenceLayoutServiceWithSagas,
    fake_reference_layout_repository: IReferenceLayoutRepository,
    fake_file_storage_proxy: FakeStorageService,
    saved_prototype: Prototype,
    tenant_id: str,
    test_file_name: str,
    test_file_content: bytes,
):
    fake_reference_layout_repository.save = mock.Mock(side_effect=RuntimeError())
    fake_file_storage_proxy.delete_file = mock.MagicMock()  # type: ignore

    with pytest.raises(ReferenceLayoutCreationFailed):
        reference_layout_with_sagas_service.create_layout(
            prototype_id=saved_prototype.id(),
            tenant_id=tenant_id,
            file_name=test_file_name,
            file=test_file_content,
        )
    fake_file_storage_proxy.delete_file.assert_called_once()


@pytest.mark.layouts
def test_delete_layout__no_prototype__no_error_no_event(
    reference_layout_service: ReferenceLayoutService,
    fake_domain_event_publisher,
    fake_command_producer,
    prototype_id,
    tenant_id,
    layout_id,
):
    reference_layout_service.delete_layout(prototype_id=prototype_id, layout_id=layout_id, tenant_id=tenant_id)

    assert fake_domain_event_publisher.last_published is None
    assert not fake_command_producer.sent


@pytest.mark.layouts
def test_delete_layout__no_layout__no_error_no_event(
    reference_layout_service: ReferenceLayoutService,
    fake_domain_event_publisher,
    fake_command_producer,
    saved_prototype,
    layout_id,
):
    reference_layout_service.delete_layout(
        prototype_id=saved_prototype.id(),
        layout_id=layout_id,
        tenant_id=saved_prototype.tenant_id(),
    )

    assert fake_domain_event_publisher.last_published is None
    assert not fake_command_producer.sent


@pytest.mark.layouts
def test_delete_layout__deleted(
    fake_reference_layout_repository: IReferenceLayoutRepository,
    fake_domain_event_publisher,
    reference_layout_service: ReferenceLayoutService,
    saved_reference_layout: ReferenceLayout,
    fake_command_producer,
    saved_prototype,
):
    assert fake_reference_layout_repository.reference_layout_of_id(
        id_=saved_reference_layout.id(),
        prototype_id=saved_prototype.id(),
    )

    reference_layout_service.delete_layout(
        prototype_id=saved_prototype.id(),
        layout_id=saved_reference_layout.id(),
        tenant_id=saved_prototype.tenant_id(),
    )

    assert not fake_reference_layout_repository.reference_layout_of_id(
        id_=saved_reference_layout.id(),
        prototype_id=saved_prototype.id(),
    )

    assert fake_domain_event_publisher.last_published.events[FIRST_ELEMENT] == ReferenceLayoutDeleted(
        reference_layout_id=saved_reference_layout.id(),
    )
    assert fake_domain_event_publisher.last_published.aggregate_type == REFERENCE_LAYOUT_AGGREGATE_TYPE
    assert fake_domain_event_publisher.last_published.aggregate_id == saved_reference_layout.id()

    assert len(fake_command_producer.sent) == 1
    command = fake_command_producer.sent[FIRST_ELEMENT]
    assert command.command == DeleteFiles([saved_reference_layout.blob_name])
    assert command.channel == FILE_STORAGE_COMMANDS_CHANNEL
    assert command.reply_to == COMMANDS_REPLIES_CHANNEL


@pytest.mark.layouts
def test_delete_layouts__no_prototype__no_error_no_event(
    fake_domain_event_publisher,
    reference_layout_service: ReferenceLayoutService,
    fake_command_producer,
    prototype_id,
    tenant_id,
    layout_id,
):
    reference_layout_service.delete_layouts(prototype_id=prototype_id, layout_ids=[layout_id], tenant_id=tenant_id)

    assert fake_domain_event_publisher.last_published is None
    assert not fake_command_producer.sent


@pytest.mark.layouts
def test_delete_layouts__no_layouts__no_error_no_event(
    fake_domain_event_publisher,
    reference_layout_service: ReferenceLayoutService,
    fake_command_producer,
    saved_prototype,
    layout_id,
):
    reference_layout_service.delete_layouts(
        prototype_id=saved_prototype.id(),
        layout_ids=[layout_id],
        tenant_id=saved_prototype.tenant_id(),
    )

    assert fake_domain_event_publisher.last_published is None
    assert not fake_command_producer.sent


@pytest.mark.layouts
def test_delete_layouts__deleted(
    fake_reference_layout_repository: IReferenceLayoutRepository,
    fake_domain_event_publisher,
    reference_layout_service: ReferenceLayoutService,
    saved_reference_layouts: list[ReferenceLayout],
    fake_command_producer,
    saved_prototype,
):
    for layout in saved_reference_layouts:
        assert fake_reference_layout_repository.reference_layout_of_id(
            id_=layout.id(),
            prototype_id=saved_prototype.id(),
        )

    reference_layout_service.delete_layouts(
        prototype_id=saved_prototype.id(),
        layout_ids=[l.id() for l in saved_reference_layouts],
        tenant_id=saved_prototype.tenant_id(),
    )

    for layout in saved_reference_layouts:
        assert not fake_reference_layout_repository.reference_layout_of_id(
            id_=layout.id(),
            prototype_id=saved_prototype.id(),
        )

    assert fake_domain_event_publisher.last_published.events[FIRST_ELEMENT] == ReferenceLayoutDeleted(
        reference_layout_id=saved_reference_layouts[LAST_ELEMENT].id(),
    )
    assert fake_domain_event_publisher.last_published.aggregate_type == REFERENCE_LAYOUT_AGGREGATE_TYPE
    assert fake_domain_event_publisher.last_published.aggregate_id == saved_reference_layouts[LAST_ELEMENT].id()

    assert len(fake_command_producer.sent) == len(saved_reference_layouts)
    for command, layout in zip(fake_command_producer.sent, saved_reference_layouts):
        assert command.command == DeleteFiles([layout.blob_name])
        assert command.channel == FILE_STORAGE_COMMANDS_CHANNEL
        assert command.reply_to == COMMANDS_REPLIES_CHANNEL


@pytest.mark.layouts
def test_find_layout__success(
    reference_layout_service: ReferenceLayoutService,
    fake_reference_layout_repository: IReferenceLayoutRepository,
    tenant_id: str,
    saved_prototype: Prototype,
    reference_layout: ReferenceLayout,
):
    fake_reference_layout_repository.save(reference_layout)
    result_reference_layout = reference_layout_service.get_layout(
        reference_layout.id(), saved_prototype.id(), tenant_id
    )

    assert reference_layout == result_reference_layout


@pytest.mark.layouts
def test_find_layout__prototype_not_exist__not_found_error(
    tenant_id: str,
    prototype,
    reference_layout,
    reference_layout_service: ReferenceLayoutService,
):
    with pytest.raises(PrototypeNotFound):
        reference_layout_service.get_layout(
            reference_layout_id=reference_layout.id(),
            prototype_id=prototype.id(),
            tenant_id=tenant_id,
        )


@pytest.mark.layouts
def test_find_layout__reference_layout_not_exist__not_found_error(
    tenant_id: str,
    saved_prototype,
    reference_layout,
    reference_layout_service: ReferenceLayoutService,
):
    with pytest.raises(ReferenceLayoutNotFound):
        reference_layout_service.get_layout(
            reference_layout_id=reference_layout.id(),
            prototype_id=saved_prototype.id(),
            tenant_id=tenant_id,
        )
