from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["PerformUnification", "PerformUnificationReply"]


@dataclass
class PerformUnification(Command):
    document_id: str
    document_type_id: str | None
    files: list[str]


@dataclass
class PerformUnificationReply(Command):
    error_type: str | None
    error_message: str | None

    @property
    def has_error(self) -> bool:
        return self.error_type is not None
