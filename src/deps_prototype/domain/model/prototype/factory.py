from datetime import datetime

from ..shared import EntityId, TenantId
from .events import PrototypeCreated
from .prototype import Prototype

__all__ = ["PrototypeFactory"]


class PrototypeFactory:
    @staticmethod
    def make(
        id_: str,
        tenant_id: str,
        name: str,
        engine: str,
        language: str,
        description: str | None = None,
    ) -> Prototype:
        prototype_id = EntityId(id_)

        return Prototype(
            id_=prototype_id,
            tenant_id=TenantId(tenant_id),
            name=name,
            engine=engine,
            language=language,
            description=description,
            created_at=datetime.now(),
            events=[
                PrototypeCreated(
                    tenant_id=tenant_id,
                    prototype_id=prototype_id(),
                ),
            ],
        )
