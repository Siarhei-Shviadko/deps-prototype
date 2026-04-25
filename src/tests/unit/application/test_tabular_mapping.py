import random
from typing import Any
from uuid import uuid4

import pytest

from deps_prototype.application import TabularMappingService
from deps_prototype.domain.exceptions import PrototypeNotFound, TabularMappingNotFound
from deps_prototype.domain.model import (
    HeaderType,
    IPrototypeRepository,
    ITabularMappingRepository,
    Prototype,
    RawHeader,
    TabularMapping,
)
from tests.fakes import FakeTabularMappingRepository


@pytest.mark.mappings
def test_create_tabular_mapping__prototype_doesnt_exist__not_found_error(
    create_tabular_mapping_payload: dict[str, Any],
    tabular_mapping_service: TabularMappingService,
    prototype: Prototype,
    tenant_id,
):
    with pytest.raises(PrototypeNotFound):
        tabular_mapping_service.create_tabular_mapping(
            code="test",
            prototype_id=prototype.id(),
            tenant_id=tenant_id,
            header_type=HeaderType(create_tabular_mapping_payload["headerType"]),
            headers=[
                RawHeader(name=header["name"], aliases=set(header["aliases"]))
                for header in create_tabular_mapping_payload["headers"]
            ],
            occurrence_index=create_tabular_mapping_payload["occurrenceIndex"],
        )


@pytest.mark.mappings
def test_create_tabular_mapping__success(
    fake_tabular_mapping_repository: FakeTabularMappingRepository,
    create_tabular_mapping_payload: dict[str, Any],
    tabular_mapping_service: TabularMappingService,
    saved_prototype: Prototype,
    tenant_id,
):
    tabular_mapping_service.create_tabular_mapping(
        code="test",
        prototype_id=saved_prototype.id(),
        tenant_id=tenant_id,
        header_type=HeaderType(create_tabular_mapping_payload["headerType"]),
        headers=[
            RawHeader(name=header["name"], aliases=set(header["aliases"]))
            for header in create_tabular_mapping_payload["headers"]
        ],
        occurrence_index=create_tabular_mapping_payload["occurrenceIndex"],
    )

    saved_mappings = fake_tabular_mapping_repository.get_all()
    assert len(saved_mappings) == 1


@pytest.mark.mappings
def test_update_tabular_mapping__prototype_not_found(
    fake_prototype_repository: IPrototypeRepository,
    tabular_mapping_service: TabularMappingService,
    tabular_mapping: TabularMapping,
    prototype_id: str,
    tenant_id: str,
):
    with pytest.raises(PrototypeNotFound):
        tabular_mapping_service.update_tabular_mapping(
            prototype_id=prototype_id,
            tenant_id=tenant_id,
            code=tabular_mapping.code,
            headers=[
                RawHeader(name=uuid4().hex, aliases=set([uuid4().hex, uuid4().hex]))
                for _ in range(random.randint(1, 5))
            ],
        )


@pytest.mark.mappings
def test_update_tabular_mapping__tabular_mapping_not_found(
    tabular_mapping_service: TabularMappingService,
    tabular_mapping: TabularMapping,
    saved_prototype: Prototype,
    tenant_id: str,
):
    with pytest.raises(TabularMappingNotFound):
        tabular_mapping_service.update_tabular_mapping(
            prototype_id=saved_prototype.id(),
            tenant_id=tenant_id,
            code=tabular_mapping.code,
        )


@pytest.mark.mappings
def test_update_tabular_mapping__success(
    tabular_mapping_service: TabularMappingService,
    fake_tabular_mapping_repository: ITabularMappingRepository,
    tabular_mapping: TabularMapping,
    saved_prototype: Prototype,
    tenant_id: str,
):
    fake_tabular_mapping_repository.save(tabular_mapping)

    headers = [
        RawHeader(name=uuid4().hex, aliases={uuid4().hex, uuid4().hex}),
        RawHeader(name=uuid4().hex, aliases={uuid4().hex, uuid4().hex}),
    ]

    tabular_mapping_service.update_tabular_mapping(
        prototype_id=saved_prototype.id(),
        tenant_id=tenant_id,
        code=tabular_mapping.code,
        header_type=HeaderType.ROWS,
        headers=headers,
        occurrence_index=random.randint(1, 20),
    )

    saved_mapping = fake_tabular_mapping_repository.get_by_code(
        code=tabular_mapping.code,
        prototype_id=saved_prototype.id(),
    )
    assert tabular_mapping == saved_mapping
