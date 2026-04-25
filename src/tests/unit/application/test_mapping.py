from typing import Any

import pytest

from deps_prototype.application import MappingService
from deps_prototype.domain.exceptions import (
    MappingAlreadyExists,
    MappingNotFound,
    PrototypeNotFound,
)
from deps_prototype.domain.model import (
    DataTypeCode,
    IMappingRepository,
    IPrototypeRepository,
    Mapping,
    MappingType,
    Prototype,
    UniqueList,
)
from deps_prototype.infrastructure.repositories import PrototypeRepository

FIRST_ELEMENT: int = 0


@pytest.mark.mappings
def test_create_mapping__prototype_doesnt_exist__not_found_error(
    create_mapping_payload: dict[str, Any],
    mapping_service: MappingService,
    prototype: Prototype,
    tenant_id,
):
    with pytest.raises(PrototypeNotFound):
        mapping_service.create_mapping(
            code=create_mapping_payload["code"],
            prototype_id=prototype.id(),
            tenant_id=tenant_id,
            data_type=DataTypeCode(create_mapping_payload["typeCode"]),
            keys=UniqueList(create_mapping_payload["keys"]),
            mapping_type=MappingType(create_mapping_payload["mappingType"]),
        )


@pytest.mark.mappings
def test_create_mapping__mapping_with_code_exists__error(
    create_mapping_payload: dict[str, Any],
    mapping_service: MappingService,
    saved_prototype: Prototype,
    tenant_id,
):
    _ = mapping_service.create_mapping(
        code=create_mapping_payload["code"],
        prototype_id=saved_prototype.id(),
        tenant_id=tenant_id,
        data_type=DataTypeCode(create_mapping_payload["typeCode"]),
        keys=UniqueList(create_mapping_payload["keys"]),
        mapping_type=MappingType(create_mapping_payload["mappingType"]),
    )

    with pytest.raises(MappingAlreadyExists):
        mapping_service.create_mapping(
            code=create_mapping_payload["code"],
            prototype_id=saved_prototype.id(),
            tenant_id=tenant_id,
            data_type=DataTypeCode(create_mapping_payload["typeCode"]),
            keys=UniqueList(create_mapping_payload["keys"]),
            mapping_type=MappingType(create_mapping_payload["mappingType"]),
        )


@pytest.mark.mappings
def test_create_mapping__prototype_exists__created(
    create_mapping_payload: dict[str, Any],
    fake_prototype_repository: PrototypeRepository,
    fake_mapping_repository: IMappingRepository,
    mapping_service: MappingService,
    saved_prototype: Prototype,
    tenant_id,
):
    type_code = DataTypeCode(create_mapping_payload["typeCode"])

    mapping = mapping_service.create_mapping(
        code=create_mapping_payload["code"],
        prototype_id=saved_prototype.id(),
        tenant_id=tenant_id,
        data_type=type_code,
        keys=UniqueList(create_mapping_payload["keys"]),
        mapping_type=MappingType(create_mapping_payload["mappingType"]),
    )

    saved_mapping = fake_mapping_repository.mapping_by_code(mapping.code, mapping.prototype_id())
    assert isinstance(saved_mapping, Mapping)
    assert saved_mapping.code == mapping.code
    assert saved_mapping.prototype_id == saved_prototype.id
    assert saved_mapping.keys == mapping.keys
    assert saved_mapping.mapping_type == mapping.mapping_type


@pytest.mark.mappings
def test_update_mapping__prototype_doesnt_exist__not_found_error(
    mapping_service: MappingService,
    prototype: Prototype,
    tenant_id: str,
    mapping: Mapping,
):
    with pytest.raises(PrototypeNotFound):
        mapping_service.modify_mapping(
            prototype_id=prototype.id(),
            mapping_code=mapping.code,
            tenant_id=tenant_id,
            keys=UniqueList(["new_key"]),
        )


@pytest.mark.mappings
def test_update_mapping__prototype_exists__mapping_doesnt_exist__not_found_error(
    fake_prototype_repository,
    mapping_service: MappingService,
    prototype: Prototype,
    tenant_id: str,
    mapping: Mapping,
):
    fake_prototype_repository.save(prototype)

    with pytest.raises(MappingNotFound):
        mapping_service.modify_mapping(
            prototype_id=prototype.id(),
            mapping_code=mapping.code,
            tenant_id=tenant_id,
            keys=UniqueList(["new_key"]),
        )


@pytest.mark.mappings
def test_update_mapping__prototype_exists__mapping_exists__updated(
    fake_domain_event_publisher,
    fake_prototype_repository: IPrototypeRepository,
    fake_mapping_repository: IMappingRepository,
    modify_mapping_payload: dict[str, Any],
    mapping_service: MappingService,
    prototype: Prototype,
    tenant_id: str,
    mapping: Mapping,
):
    fake_prototype_repository.save(prototype)
    fake_mapping_repository.save(mapping)

    mapping_service.modify_mapping(
        prototype_id=prototype.id(),
        tenant_id=tenant_id,
        mapping_code=mapping.code,
        keys=UniqueList(modify_mapping_payload["keys"]),
    )

    updated_mapping = fake_mapping_repository.mapping_by_code(
        code=mapping.code,
        prototype_id=mapping.prototype_id(),
    )

    assert updated_mapping == mapping
    assert updated_mapping.keys == UniqueList(modify_mapping_payload["keys"])


@pytest.mark.mappings
def test_delete_mapping__prototype_doesnt_exist__error(
    fake_domain_event_publisher,
    mapping_service: MappingService,
    prototype: Prototype,
    tenant_id: str,
    mapping: Mapping,
) -> None:
    with pytest.raises(PrototypeNotFound):
        mapping_service.delete_mapping(prototype_id=prototype.id(), mapping_code=mapping.code, tenant_id=tenant_id)


@pytest.mark.mappings
def test_delete_mapping__prototype_exists__mapping_doesnt_exist__no_error(
    fake_domain_event_publisher,
    fake_prototype_repository: IPrototypeRepository,
    mapping_service: MappingService,
    prototype: Prototype,
    tenant_id: str,
    mapping: Mapping,
) -> None:
    fake_prototype_repository.save(prototype)

    mapping_service.delete_mapping(prototype_id=prototype.id(), mapping_code=mapping.code, tenant_id=tenant_id)


@pytest.mark.mappings
def test_delete_mapping__prototype_exists__mapping_exists__deleted(
    fake_domain_event_publisher,
    fake_prototype_repository: IPrototypeRepository,
    fake_mapping_repository: IMappingRepository,
    mapping_service: MappingService,
    prototype: Prototype,
    tenant_id: str,
    mapping: Mapping,
) -> None:
    fake_prototype_repository.save(prototype)
    fake_mapping_repository.save(mapping)

    mapping_service.delete_mapping(
        prototype_id=prototype.id(),
        mapping_code=mapping.code,
        tenant_id=tenant_id,
    )

    assert fake_mapping_repository.mapping_by_code(mapping.code, mapping.prototype_id()) is None
