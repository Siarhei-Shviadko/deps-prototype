import contextlib
import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.common import (
    CommandMessageHeaders,
    make_message_for_command,
)
from deps_message_flow.commands.consumer import CommandHandlerReplyBuilder
from deps_message_flow.commands.consumer.command_message import CommandMessage
from deps_message_flow.events.mappers import JsonMapper
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)
from deps_message_flow.messaging.common import IMessage

from deps_prototype.api import get_current_user_tenant
from deps_prototype.application import (
    ExtractionService,
    PrototypeService,
    UnifiedMappingService,
)
from deps_prototype.containers import Containers
from deps_prototype.domain.exceptions import (
    BusinessException,
    PrototypeHasDocument,
    PrototypeNotFound,
)
from deps_prototype.domain.model.prototype import PROTOTYPE_EXTRACTOR_CODE

from .commands import PerformExtractionStepReply, PerformPrototypeExtraction
from .error_type import ErrorType
from .events import DocumentTypeDeleted, ExtractorFieldDeleted

__all__ = ["handle_extractor_field_deletion", "perform_prototype_extraction_handler", "document_type_deleted_handler"]

logger = logging.getLogger(__name__)

REPLY_TO_MOCK = "NONE"


@inject
def handle_extractor_field_deletion(
    dee: DomainEventEnvelope[ExtractorFieldDeleted],
    unified_mapping_service: UnifiedMappingService = Provide[Containers.application.unified_mapping],
) -> None:
    if dee.event.extractor_type != PROTOTYPE_EXTRACTOR_CODE:
        return

    try:
        unified_mapping_service.delete_mappings(
            code=dee.event.code,
            prototype_id=dee.event.document_type_code,
            tenant_id=get_current_user_tenant(),
        )
    except PrototypeNotFound:
        logger.warning(
            f"Couldn't delete mapping for Prototype `{dee.event.document_type_code}`, because Prototype not found.",
        )


@inject
def perform_prototype_extraction_handler(
    command_message: CommandMessage[PerformPrototypeExtraction],
    extraction: ExtractionService = Provide[Containers.application.extraction],
) -> list[IMessage]:
    document_id = command_message.command.document_id
    error_type = None
    error_message = None

    try:
        extraction.extract(
            document_id=document_id,
            prototype_id=command_message.command.prototype_id,
            tenant_id=command_message.command.tenant_id,
            engine=command_message.command.engine,
            language=command_message.command.language,
        )
    except BusinessException as e:
        error_type, error_message = ErrorType.BUSINESS, str(e)
    except Exception as e:
        error_type, error_message = ErrorType.SYSTEM, str(e)

    if error_type is not None:
        logger.error(
            "Failed to perform extraction for document `%s`! Reason: %s",
            document_id,
            error_message,
            exc_info=True,
        )

    command_reply = PerformExtractionStepReply(error_type=error_type, error_message=error_message)
    message_reply = make_message_for_command(
        channel=command_message.message.headers[CommandMessageHeaders.REPLY_TO],
        payload=JsonMapper().serialize(command_reply),
        command_type=command_reply.__class__.__name__,
        reply_to=REPLY_TO_MOCK,
    )
    return [CommandHandlerReplyBuilder.with_success(message_reply)]


@inject
def document_type_deleted_handler(
    dee: DomainEventEnvelope[DocumentTypeDeleted],
    prototype_service: PrototypeService = Provide[Containers.application.prototype],
) -> None:
    with contextlib.suppress(PrototypeHasDocument):
        prototype_service.delete_prototype(
            id_=dee.event.document_type,
            tenant_id=dee.event.tenant,
        )
