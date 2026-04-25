import pytest

from deps_prototype.application import UnifiedMappingService
from deps_prototype.domain.exceptions import PrototypeNotFound
from deps_prototype.domain.model import Mapping, Prototype, TabularMapping
from tests.fakes import FakeMappingRepository, FakeTabularMappingRepository


@pytest.mark.mappings
def test_delete_mappings__prototype_does_not_exist__error(
    unified_mapping_service: UnifiedMappingService,
    prototype: Prototype,
    tabular_mapping: TabularMapping,
):
    with pytest.raises(PrototypeNotFound):
        unified_mapping_service.delete_mappings(
            code=tabular_mapping.code,
            prototype_id=prototype.id(),
            tenant_id=prototype.tenant_id(),
        )


@pytest.mark.mappings
def test_delete_mappings__mapping_exists__success(
    fake_tabular_mapping_repository: FakeTabularMappingRepository,
    fake_mapping_repository: FakeMappingRepository,
    unified_mapping_service: UnifiedMappingService,
    saved_prototype: Prototype,
    mapping: Mapping,
):
    fake_mapping_repository.save(mapping)

    unified_mapping_service.delete_mappings(
        code=mapping.code,
        prototype_id=saved_prototype.id(),
        tenant_id=saved_prototype.tenant_id(),
    )

    assert (
        fake_mapping_repository.mapping_by_code(
            code=mapping.code,
            prototype_id=saved_prototype.id(),
        )
        is None
    )


@pytest.mark.mappings
def test_delete_mappings__tabular_mapping_exists__success(
    fake_mapping_repository: FakeMappingRepository,
    fake_tabular_mapping_repository: FakeTabularMappingRepository,
    unified_mapping_service: UnifiedMappingService,
    saved_prototype: Prototype,
    tabular_mapping: TabularMapping,
):
    fake_tabular_mapping_repository.save(tabular_mapping)

    unified_mapping_service.delete_mappings(
        code=tabular_mapping.code,
        prototype_id=saved_prototype.id(),
        tenant_id=saved_prototype.tenant_id(),
    )

    assert (
        fake_tabular_mapping_repository.get_by_code(
            code=tabular_mapping.code,
            prototype_id=saved_prototype.id(),
        )
        is None
    )


@pytest.mark.mappings
def test_delete_mappings__no_mappings_exist__success(
    fake_tabular_mapping_repository: FakeTabularMappingRepository,
    fake_mapping_repository: FakeMappingRepository,
    unified_mapping_service: UnifiedMappingService,
    saved_prototype: Prototype,
    tabular_mapping: TabularMapping,
):
    unified_mapping_service.delete_mappings(
        code=tabular_mapping.code,
        prototype_id=saved_prototype.id(),
        tenant_id=saved_prototype.tenant_id(),
    )
