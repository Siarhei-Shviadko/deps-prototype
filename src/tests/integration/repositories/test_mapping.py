from deps_prototype.domain.model import (
    IMappingRepository,
    IPrototypeRepository,
    Mapping,
    Prototype,
)
from tests.factories import MappingFactory, PrototypeFactory


def test__save__find__delete__ok(
    prototype_repository: IPrototypeRepository,
    mapping_repository: IMappingRepository,
    prototype: Prototype,
    mapping: Mapping,
) -> None:
    prototype_repository.save(prototype)
    mapping_repository.save(mapping)

    assert mapping_repository.mapping_by_code(code=mapping.code, prototype_id=mapping.prototype_id()) == mapping

    mapping_repository.delete(
        mapping_code=mapping.code,
        prototype_id=mapping.prototype_id(),
    )

    assert mapping_repository.mapping_by_code(code=mapping.code, prototype_id=mapping.prototype_id()) is None


def test_mappings_of_prototype__ok(
    prototype_repository: IPrototypeRepository,
    mapping_repository: IMappingRepository,
    prototype: Prototype,
) -> None:
    prototype_repository.save(prototype)

    field1 = MappingFactory(prototype_id=prototype.id())
    field2 = MappingFactory(prototype_id=prototype.id())

    mapping_repository.save(field1)
    mapping_repository.save(field2)

    assert mapping_repository.mappings_of_prototype(prototype_id=prototype.id()) == [
        field1,
        field2,
    ]


def test_fields_of_prototype__fields_dont_exist__empty_list(
    prototype_repository: IPrototypeRepository,
    mapping_repository: IMappingRepository,
    prototype: Prototype,
    mapping: Mapping,
) -> None:
    prototype_repository.save(prototype)
    mapping_repository.save(mapping)

    prototype1 = PrototypeFactory()

    assert mapping_repository.mappings_of_prototype(prototype_id=prototype1.id()) == []
