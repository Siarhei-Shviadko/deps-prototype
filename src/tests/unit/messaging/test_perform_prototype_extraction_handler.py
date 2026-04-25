import json
from uuid import uuid4

import pytest
from deps_message_flow.commands.common import CommandReplyOutcome

from deps_prototype.domain.exceptions import NotFoundError
from deps_prototype.messaging.commands import PerformExtractionStepReply
from deps_prototype.messaging.error_type import ErrorType
from deps_prototype.messaging.handlers import perform_prototype_extraction_handler

FIRST_ELEMENT: int = 0


@pytest.mark.extraction
def test_handler__no_errors__ok(perform_prototype_extraction_command_message, extraction_service_mock):
    extraction_service_mock.extract.return_value = None
    command = perform_prototype_extraction_command_message.command

    reply = perform_prototype_extraction_handler(perform_prototype_extraction_command_message)

    extraction_service_mock.extract.assert_called_once_with(
        document_id=command.document_id,
        prototype_id=command.prototype_id,
        tenant_id=command.tenant_id,
        language=command.language,
        engine=command.engine,
    )

    message = reply[FIRST_ELEMENT]
    message_headers = message.headers
    assert message_headers["reply_outcome_type"] == CommandReplyOutcome.SUCCESS.value
    assert message_headers["reply_type"] == PerformExtractionStepReply.__name__
    assert json.loads(message.payload) == {"error_message": None, "error_type": None}


@pytest.mark.extraction
def test_handler__business_error__ok(perform_prototype_extraction_command_message, extraction_service_mock):
    error_message = uuid4().hex
    extraction_service_mock.extract.side_effect = NotFoundError(error_message)

    reply = perform_prototype_extraction_handler(perform_prototype_extraction_command_message)

    message = reply[FIRST_ELEMENT]
    message_headers = message.headers
    assert message_headers["reply_outcome_type"] == CommandReplyOutcome.SUCCESS.value
    assert message_headers["reply_type"] == PerformExtractionStepReply.__name__
    assert json.loads(message.payload) == {
        "error_message": str(
            error_message,
        ),
        "error_type": ErrorType.BUSINESS.value,
    }


@pytest.mark.extraction
def test_handler__system_error__ok(perform_prototype_extraction_command_message, extraction_service_mock):
    error_message = uuid4().hex
    extraction_service_mock.extract.side_effect = RuntimeError(error_message)

    reply = perform_prototype_extraction_handler(perform_prototype_extraction_command_message)

    message = reply[FIRST_ELEMENT]
    message_headers = message.headers
    assert message_headers["reply_outcome_type"] == CommandReplyOutcome.SUCCESS.value
    assert message_headers["reply_type"] == PerformExtractionStepReply.__name__
    assert json.loads(message.payload) == {
        "error_message": str(
            error_message,
        ),
        "error_type": ErrorType.SYSTEM.value,
    }
