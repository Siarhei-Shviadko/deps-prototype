from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

__all__ = ["ReferenceLayoutDeleted", "ReferenceLayoutStateUpdated"]


@dataclass
class ReferenceLayoutDeleted(DomainEvent):
    reference_layout_id: str


@dataclass
class ReferenceLayoutStateUpdated(DomainEvent):
    reference_layout_id: str
    prototype_id: str
    state: str
