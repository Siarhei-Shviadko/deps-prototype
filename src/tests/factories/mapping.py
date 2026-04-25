from typing import Any

import factory
from factory.fuzzy import FuzzyChoice
from faker import Faker

from deps_prototype.domain.model import DataTypeCode, EntityId, Mapping
from deps_prototype.domain.model import MappingFactory as DomainMappingFactory
from deps_prototype.domain.model import MappingType, UniqueList

__all__ = ["MappingFactory"]

fake = Faker()


class MappingFactory(factory.Factory):
    class Meta:
        model = Mapping

    code = factory.Faker("pystr")
    prototype_id = factory.Faker("pystr")
    keys = factory.LazyAttribute(lambda obj: UniqueList(fake.words(nb=3, unique=True)))
    mapping_type = FuzzyChoice(MappingType)
    data_type = FuzzyChoice(DataTypeCode)

    @classmethod
    def _create(cls, _, *args: Any, **kwargs: Any) -> Mapping:
        return DomainMappingFactory.create(
            code=kwargs["code"],
            prototype_id=kwargs["prototype_id"],
            keys=kwargs["keys"],
            mapping_type=kwargs["mapping_type"],
            data_type=kwargs["data_type"],
        )
