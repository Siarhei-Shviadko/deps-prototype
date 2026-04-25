from typing import Any

import pytest

from deps_prototype.api.serializers.v1 import (
    CreateMappingRequest,
    ModifyMappingRequest,
    SerializedMapping,
)
from deps_prototype.domain.model import Mapping, UniqueList
from tests.factories.mapping import MappingFactory


@pytest.mark.mappings
def test_serialized_mapping__from_model__ok():
    mapping: Mapping = MappingFactory()

    res = SerializedMapping.from_model(mapping)

    assert res.code == mapping.code
    assert res.prototype_id == mapping.prototype_id()
    assert res.data_type == mapping.data_type
    assert res.mapping_type == mapping.mapping_type

    assert res.model_dump(by_alias=True) == {
        "code": mapping.code,
        "prototypeId": mapping.prototype_id(),
        "mappingType": mapping.mapping_type,
        "dataType": mapping.data_type,
        "keys": UniqueList(mapping.keys),
    }


@pytest.mark.mappings
def test_create_mapping_request__ok(create_mapping_payload: dict[str, Any]) -> None:
    res = CreateMappingRequest(**create_mapping_payload)

    assert res.data_type == create_mapping_payload["typeCode"]
    assert res.keys == UniqueList(create_mapping_payload["keys"])
    assert res.code == create_mapping_payload["code"]
    assert res.mapping_type == create_mapping_payload["mappingType"]


@pytest.mark.mappings
def test_modify_mapping_request__ok(modify_mapping_payload: dict[str, Any]) -> None:
    res = ModifyMappingRequest(**modify_mapping_payload)

    assert res.keys == UniqueList(modify_mapping_payload["keys"])
