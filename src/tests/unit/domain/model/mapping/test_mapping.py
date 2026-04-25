from copy import deepcopy

import pytest

from deps_prototype.domain.exceptions import InvariantViolation
from deps_prototype.domain.model import (
    DocumentLayout,
    IllegalArgumentError,
    KeyValuePair,
    Mapping,
    MappingType,
    UniqueList,
)
from tests.factories import MappingFactory


@pytest.mark.mappings
def test_update__keys__updated():
    mapping1: Mapping = MappingFactory()
    mapping2: Mapping = MappingFactory()
    old_mapping = deepcopy(mapping1)

    mapping1.update(keys=mapping2.keys)

    assert mapping1.keys == mapping2.keys

    assert old_mapping.mapping_type == mapping1.mapping_type
    assert old_mapping.data_type == mapping1.data_type
    assert old_mapping.prototype_id == mapping1.prototype_id
    assert old_mapping.code == mapping1.code


@pytest.mark.mappings
@pytest.mark.parametrize(
    "input_keys,expected_keys,is_valid",
    (
        (UniqueList([""]), None, False),
        (UniqueList(["", "a"]), None, False),
        (UniqueList(["a", "b"]), UniqueList(["a", "b"]), True),
        (UniqueList([" a"]), UniqueList(["a"]), True),
        (UniqueList(["a "]), UniqueList(["a"]), True),
        (UniqueList(["a b"]), UniqueList(["a b"]), True),
        (UniqueList(["a  b"]), None, False),
        (UniqueList(["a . , / ' b"]), UniqueList(["a . , / ' b"]), True),
        (UniqueList([" a b "]), UniqueList(["a b"]), True),
    ),
)
def test_keys_format(input_keys: UniqueList, expected_keys: UniqueList | None, is_valid: bool) -> None:
    if is_valid:
        mapping_list = MappingFactory(keys=input_keys, mapping_type=MappingType.ONE_TO_MANY)
        assert mapping_list.keys == expected_keys
    else:
        with pytest.raises(IllegalArgumentError):
            MappingFactory(keys=input_keys, mapping_type=MappingType.ONE_TO_MANY)


def test_empty_keys__error() -> None:
    with pytest.raises(InvariantViolation):
        MappingFactory(keys=UniqueList())


@pytest.mark.mappings
def test_search_data__empty_list(mapping: Mapping, document_layout) -> None:
    data = mapping.search_data(document_layout)

    assert data == []


@pytest.mark.mappings
def test_search_data__string_mapping__ok(
    string_mapping: Mapping, document_layout: DocumentLayout, key_value_pair: KeyValuePair
) -> None:
    data = string_mapping.search_data(document_layout)

    assert data == [key_value_pair]


@pytest.mark.mappings
def test_search_data__checkmark_mapping__ok(
    checkmark_mapping: Mapping,
    document_layout: DocumentLayout,
) -> None:
    data = checkmark_mapping.search_data(document_layout)

    assert len(data) == 1

    assert data[0].key.content.lower() == checkmark_mapping.keys[0].lower()
