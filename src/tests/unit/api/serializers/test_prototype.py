from deps_prototype.api.serializers.v1 import (
    FindPrototypesResponse,
    SerializedMapping,
    SerializedPrototype,
)
from deps_prototype.domain.model import Mapping, Prototype

FIRST_ELEMENT: int = 0


def test_find_prototypes_response__from_model__ok(prototype: Prototype) -> None:
    meta = {"a": 1, "b": 2}
    res = FindPrototypesResponse.from_model(prototypes=[prototype], meta=meta)

    assert isinstance(res.prototypes, list)
    assert isinstance(res.prototypes[FIRST_ELEMENT], SerializedPrototype)
    assert res.meta == meta

    response_dict = res.model_dump(by_alias=True)
    assert response_dict["prototypes"]
    assert response_dict["meta"] == meta
