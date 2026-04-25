from datetime import timezone

import factory
from faker import Faker

from deps_prototype.domain.model import EntityId, Prototype, PrototypeCreated, TenantId

__all__ = ["PrototypeFactory"]

fake = Faker()


class PrototypeFactory(factory.Factory):
    class Meta:
        model = Prototype

    id_ = factory.LazyAttribute(lambda obj: EntityId())
    tenant_id = factory.LazyAttribute(lambda obj: TenantId(fake.pystr()))
    name = factory.Faker("pystr")
    language = factory.Faker("pystr")
    engine = factory.Faker("pystr")
    description = factory.Faker("pystr")
    created_at = factory.Faker("date_time", tzinfo=timezone.utc)

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        kwargs["events"] = [
            PrototypeCreated(
                prototype_id=kwargs["id_"],
                tenant_id=kwargs["tenant_id"],
            )
        ]
        return kwargs
