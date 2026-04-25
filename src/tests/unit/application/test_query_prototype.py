import pytest

from deps_prototype.application import QueryPrototypeService
from deps_prototype.domain.exceptions import PrototypeNotFound
from deps_prototype.domain.model import (
    IQueryPrototypeRepository,
    PrototypeWithMappings,
    TabularMapping,
)

from ...fakes import FakeQueryPrototypeRepository
from .test_prototype import compare_mappings_entities, compare_prototype_entities

__all__ = ["compare_prototypes_with_mappings", "compare_tabular_mappings_entities"]


def compare_tabular_mappings_entities(tabular_mapping1: TabularMapping, tabular_mapping2: TabularMapping) -> None:
    assert tabular_mapping1.code == tabular_mapping2.code
    assert tabular_mapping1.prototype_id() == tabular_mapping2.prototype_id()
    assert tabular_mapping1.headers == tabular_mapping2.headers
    assert tabular_mapping1.header_type == tabular_mapping2.header_type
    assert tabular_mapping1.occurrence_index == tabular_mapping2.occurrence_index
    assert tabular_mapping1.created_at == tabular_mapping2.created_at


def compare_prototypes_with_mappings(
    prototype_with_mappings1: PrototypeWithMappings,
    prototype_with_mappings2: PrototypeWithMappings,
) -> None:
    compare_prototype_entities(prototype_with_mappings1["prototype"], prototype_with_mappings2["prototype"])

    assert len(prototype_with_mappings1["mappings"]) == len(prototype_with_mappings2["mappings"])
    for mapping1, mapping2 in zip(prototype_with_mappings1["mappings"], prototype_with_mappings2["mappings"]):
        compare_mappings_entities(mapping1, mapping2)

    assert len(prototype_with_mappings1["tabular_mappings"]) == len(prototype_with_mappings2["tabular_mappings"])
    for tabular_mapping1, tabular_mapping1 in zip(
        prototype_with_mappings1["tabular_mappings"],
        prototype_with_mappings2["tabular_mappings"],
    ):
        compare_tabular_mappings_entities(tabular_mapping1, tabular_mapping1)


@pytest.mark.prototype
def test_find_prototype__prototype_doesnt_exist__error(
    prototype_with_mappings: PrototypeWithMappings,
    query_prototype_service: QueryPrototypeService,
    fake_query_prototype_repository: IQueryPrototypeRepository,
):
    prototype = prototype_with_mappings["prototype"]
    with pytest.raises(PrototypeNotFound):
        query_prototype_service.find_prototype(prototype.id(), prototype.tenant_id())


@pytest.mark.prototype
def test_find_prototype__prototype_exists__ok(
    prototype_with_mappings: PrototypeWithMappings,
    fake_query_prototype_repository: FakeQueryPrototypeRepository,
    query_prototype_service: QueryPrototypeService,
) -> None:
    prototype = prototype_with_mappings["prototype"]
    fake_query_prototype_repository._db[(prototype.id(), prototype.tenant_id())] = prototype_with_mappings

    saved_prototype_with_mappings = query_prototype_service.find_prototype(prototype.id(), prototype.tenant_id())

    compare_prototypes_with_mappings(prototype_with_mappings, saved_prototype_with_mappings)
