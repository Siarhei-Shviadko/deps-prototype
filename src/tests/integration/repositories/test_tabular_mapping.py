from deps_prototype.domain.model import (
    IPrototypeRepository,
    ITabularMappingRepository,
    Prototype,
)
from tests.factories import TabularMappingFactory


def test_tabular_mapping_save__ok(
    prototype_repository: IPrototypeRepository,
    tabular_mapping_repository: ITabularMappingRepository,
    prototype: Prototype,
) -> None:
    prototype_repository.save(prototype)

    mapping_ = TabularMappingFactory(prototype_id=prototype.id)
    tabular_mapping_repository.save(mapping_)

    assert tabular_mapping_repository.get_by_code(code=mapping_.code, prototype_id=prototype.id()) == mapping_


def test_tabular_mapping_delete__success(
    prototype_repository: IPrototypeRepository,
    tabular_mapping_repository: ITabularMappingRepository,
    prototype: Prototype,
) -> None:
    prototype_repository.save(prototype)

    mapping_ = TabularMappingFactory(prototype_id=prototype.id)
    tabular_mapping_repository.save(mapping_)

    assert tabular_mapping_repository.get_by_code(code=mapping_.code, prototype_id=prototype.id()) == mapping_

    tabular_mapping_repository.delete(code=mapping_.code, prototype_id=mapping_.prototype_id())

    assert tabular_mapping_repository.get_by_code(code=mapping_.code, prototype_id=prototype.id()) is None


def test_tabular_mapping__get_of_prototype__empty_list(
    prototype_repository: IPrototypeRepository,
    tabular_mapping_repository: ITabularMappingRepository,
    prototype: Prototype,
) -> None:
    prototype_repository.save(prototype)

    mappings = tabular_mapping_repository.mappings_of_prototype(prototype.id())

    assert len(mappings) == 0


def test_tabular_mapping__get_of_prototype__success(
    prototype_repository: IPrototypeRepository,
    tabular_mapping_repository: ITabularMappingRepository,
    prototype: Prototype,
) -> None:
    prototype_repository.save(prototype)

    mapping_1 = TabularMappingFactory(prototype_id=prototype.id)
    mapping_2 = TabularMappingFactory(prototype_id=prototype.id)

    tabular_mapping_repository.save(mapping_1)
    tabular_mapping_repository.save(mapping_2)

    mappings = tabular_mapping_repository.mappings_of_prototype(prototype.id())

    assert len(mappings) == 2
    assert mapping_1 in mappings
    assert mapping_2 in mappings
