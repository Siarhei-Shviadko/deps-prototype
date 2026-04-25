from deps_prototype.api.serializers.v1 import (
    FindReferenceLayoutsResponse,
    SerializedReferenceLayout,
)

FIRST_ELEMENT: int = 0


def test_find_layout_response__from_model__ok(reference_layout):
    res = SerializedReferenceLayout.from_model(reference_layout=reference_layout)

    assert res.id == reference_layout.id()
    assert res.prototype_id == reference_layout.prototype_id()
    assert res.state == reference_layout.state
    assert res.blob_name == reference_layout.blob_name

    response_dict = res.model_dump(by_alias=True)
    assert response_dict["id"] == reference_layout.id()
    assert response_dict["prototypeId"] == reference_layout.prototype_id()
    assert response_dict["state"] == reference_layout.state.value
    assert response_dict["blobName"] == reference_layout.blob_name


def test_find_layouts_response__from_model__ok(reference_layout):
    res = FindReferenceLayoutsResponse.from_model(reference_layouts=[reference_layout])

    assert isinstance(res.reference_layouts, list)
    assert isinstance(res.reference_layouts[FIRST_ELEMENT], SerializedReferenceLayout)

    response_dict = res.model_dump(by_alias=True)
    assert response_dict["reference_layouts"]
