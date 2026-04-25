import datetime as dt

import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from faker import Faker

from deps_prototype.domain.model import EntityId, Header, HeaderType, TabularMapping

__all__ = ["TabularMappingFactory"]

fake = Faker()


class HeaderFactory(factory.Factory):
    class Meta:
        model = Header

    name = factory.Faker("word")
    aliases = factory.LazyFunction(lambda: {fake.word() for _ in range(2)})


class TabularMappingFactory(factory.Factory):
    class Meta:
        model = TabularMapping

    code = factory.Faker("pystr")
    prototype_id = factory.LazyFunction(lambda: EntityId(fake.uuid4()))
    header_type = FuzzyChoice(list(HeaderType))
    headers = factory.LazyAttribute(lambda _: [HeaderFactory() for _ in range(3)])
    occurrence_index = FuzzyInteger(0, 10)
    created_at = factory.LazyFunction(lambda: dt.datetime.now(tz=dt.timezone.utc))
