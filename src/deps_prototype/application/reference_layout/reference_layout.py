import logging

from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher

from deps_prototype.constants import (
    COMMANDS_REPLIES_CHANNEL,
    FILE_STORAGE_COMMANDS_CHANNEL,
    REFERENCE_LAYOUT_AGGREGATE_TYPE,
)
from deps_prototype.domain.exceptions import PrototypeNotFound, ReferenceLayoutNotFound
from deps_prototype.domain.model import (
    DeleteFiles,
    IPrototypeRepository,
    IReferenceLayoutRepository,
    LayoutState,
    ParsingFeature,
    Prototype,
    ReferenceLayout,
)

__all__ = ["ReferenceLayoutService"]


class ReferenceLayoutService:
    command_channels: dict = {DeleteFiles: FILE_STORAGE_COMMANDS_CHANNEL}
    PARSING_FEATURES = {ParsingFeature.KEY_VALUE_PAIRS}

    def __init__(
        self,
        reference_layout_repository: IReferenceLayoutRepository,
        prototype_repository: IPrototypeRepository,
        domain_event_publisher: DomainEventPublisher,
        command_producer: CommandProducer,
    ) -> None:
        self._reference_layout_repository = reference_layout_repository
        self._prototype_repository = prototype_repository
        self._domain_event_publisher = domain_event_publisher
        self._command_producer = command_producer

        self._logger = logging.getLogger(self.__class__.__name__)

    def find_layouts(self, prototype_id: str, tenant_id: str) -> list[ReferenceLayout]:
        self._check_prototype_existence(prototype_id=prototype_id, tenant_id=tenant_id)
        return self._reference_layout_repository.reference_layouts_of_prototype(prototype_id=prototype_id)

    def get_layout(self, reference_layout_id: str, prototype_id: str, tenant_id: str) -> ReferenceLayout | None:
        self._check_prototype_existence(prototype_id=prototype_id, tenant_id=tenant_id)
        return self.find_layout(reference_layout_id=reference_layout_id, prototype_id=prototype_id)

    def find_layout(self, reference_layout_id: str, prototype_id: str) -> ReferenceLayout:
        if reference_layout := self._reference_layout_repository.reference_layout_of_id(
            id_=reference_layout_id,
            prototype_id=prototype_id,
        ):
            return reference_layout

        raise ReferenceLayoutNotFound(reference_layout_id)

    def update_layout(
        self,
        reference_layout_id: str,
        prototype_id: str,
        state: LayoutState | None = None,
        blob_name: str | None = None,
    ) -> None:
        reference_layout = self.find_layout(
            reference_layout_id=reference_layout_id,
            prototype_id=prototype_id,
        )
        reference_layout.update_info(state=state, blob_name=blob_name)
        self._reference_layout_repository.save(reference_layout)
        self._publish_events(reference_layout)

    def delete_layout(self, prototype_id: str, layout_id: str, tenant_id: str) -> None:
        if not self._prototype_repository.has_prototype_of_id(id_=prototype_id, tenant_id=tenant_id):
            self._logger.warning(
                "Cannot delete layout `%s`. Reason: prototype `%s` doesn't exist.",
                layout_id,
                prototype_id,
            )
            return

        layout = self._reference_layout_repository.reference_layout_of_id(id_=layout_id, prototype_id=prototype_id)
        if not layout:
            self._logger.warning("Cannot delete layout `%s`. Reason: layout doesn't exist.", layout_id)
            return

        self._reference_layout_repository.delete(reference_layout=layout)

        self._publish_events(layout)
        self._send_commands(layout)

    def delete_layouts(self, prototype_id: str, layout_ids: list[str], tenant_id: str) -> None:
        if not self._prototype_repository.has_prototype_of_id(id_=prototype_id, tenant_id=tenant_id):
            self._logger.warning(
                "Cannot delete layouts `%s`. Reason: prototype `%s` doesn't exist.",
                layout_ids,
                prototype_id,
            )
            return

        layouts = self._reference_layout_repository.reference_layouts_of_ids(ids=layout_ids, prototype_id=prototype_id)
        if not layouts:
            self._logger.warning("Cannot delete layouts `%s`. Reason: layouts don't exist.", layout_ids)
            return

        self._reference_layout_repository.delete_all(reference_layouts=layouts)

        for layout in layouts:
            self._publish_events(layout)
            self._send_commands(layout)

    def _find_prototype(self, prototype_id: str, tenant_id: str) -> Prototype | None:
        if prototype := self._prototype_repository.prototype_of_id(id_=prototype_id, tenant_id=tenant_id):
            return prototype

        raise PrototypeNotFound(prototype_id)

    def _check_prototype_existence(self, prototype_id: str, tenant_id: str) -> None:
        if self._prototype_repository.has_prototype_of_id(id_=prototype_id, tenant_id=tenant_id):
            return

        raise PrototypeNotFound(prototype_id)

    def _publish_events(self, reference_layout: ReferenceLayout) -> None:
        self._domain_event_publisher.publish(
            REFERENCE_LAYOUT_AGGREGATE_TYPE,
            reference_layout.id(),
            reference_layout.events,
        )

    def _send_commands(self, reference_layout: ReferenceLayout) -> None:
        for command in reference_layout.commands:
            channel = self.command_channels[type(command)]
            self._command_producer.send(channel, command, COMMANDS_REPLIES_CHANNEL)
