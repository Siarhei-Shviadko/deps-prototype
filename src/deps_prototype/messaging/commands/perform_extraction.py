from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["PerformPrototypeExtraction", "PerformExtractionStepReply"]


@dataclass
class PerformPrototypeExtraction(Command):
    prototype_id: str
    tenant_id: str
    document_id: int
    language: str | None = None
    engine: str | None = None


@dataclass
class PerformExtractionStepReply(Command):
    error_type: str | None
    error_message: str | None
