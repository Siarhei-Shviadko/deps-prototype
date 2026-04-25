from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

__all__ = ["PrototypeCreated", "PrototypeUpdated", "PrototypeDeleted"]


@dataclass
class PrototypeCreated(DomainEvent):
    prototype_id: str
    tenant_id: str


@dataclass
class PrototypeUpdated(DomainEvent):
    prototype_id: str
    tenant_id: str
    engine: str | None
    language: str | None
    description: str | None


@dataclass
class PrototypeDeleted(DomainEvent):
    prototype_id: str
    tenant_id: str
