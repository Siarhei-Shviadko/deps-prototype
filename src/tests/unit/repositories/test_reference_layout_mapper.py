from deps_prototype.infrastructure.repositories import ReferenceLayoutMapper


def test_reference_layout_mapper__successful(reference_layout):
    reference_layout_dict = ReferenceLayoutMapper.to_dict(reference_layout)

    assert reference_layout.id() == reference_layout_dict["id"]
    assert reference_layout.prototype_id() == reference_layout_dict["prototype_id"]
    assert reference_layout.state == reference_layout_dict["state"]
    assert reference_layout.blob_name == reference_layout_dict["blob_name"]

    reference_layout_from_dict = ReferenceLayoutMapper.from_dict(reference_layout_dict)

    assert reference_layout_from_dict.id() == reference_layout.id()
    assert reference_layout_from_dict.prototype_id() == reference_layout.prototype_id()
    assert reference_layout_from_dict.state == reference_layout.state
    assert reference_layout_from_dict.blob_name == reference_layout.blob_name
