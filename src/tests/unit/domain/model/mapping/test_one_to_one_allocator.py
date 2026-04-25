import pytest

from deps_prototype.domain.model.mapping.allocators import OneToOneAllocator


@pytest.mark.mappings
def test_allocate__no_kvps__empty_list(document_layout):
    for page in document_layout.pages:
        page.key_value_pairs.clear()

    res = OneToOneAllocator(document_layout, keys={"test"}).allocate()

    assert res == []


@pytest.mark.mappings
def test_allocate__kvps__not_allocated__empty_list(document_layout):
    res = OneToOneAllocator(document_layout, keys={"test"}).allocate()

    assert res == []


@pytest.mark.mappings
def test_allocate__kvps__allocated(document_layout):
    res = OneToOneAllocator(document_layout, keys={"Checked"}).allocate()

    assert len(res) == 1
