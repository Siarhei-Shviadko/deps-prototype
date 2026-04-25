import factory
from factory.fuzzy import FuzzyChoice
from faker import Faker

from deps_prototype.domain.model import EntityId, LayoutState, ReferenceLayout

__all__ = ["ReferenceLayoutFactory"]

fake = Faker()


class ReferenceLayoutFactory(factory.Factory):
    class Meta:
        model = ReferenceLayout

    id_ = factory.LazyAttribute(lambda obj: EntityId())
    prototype_id = factory.LazyAttribute(lambda obj: EntityId())
    state = FuzzyChoice(LayoutState)
    blob_name = factory.Faker("pystr")
    title = factory.Faker("pystr")
