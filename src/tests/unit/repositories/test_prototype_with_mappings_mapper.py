from deps_prototype.domain.model import PrototypeWithMappings
from deps_prototype.infrastructure.repositories import PrototypeWithMappingsMapper


def test_prototype_with_mappings_mapper(
    prototype_with_mappings: PrototypeWithMappings,
):
    prototype_with_mappings_dict = PrototypeWithMappingsMapper.to_dict(prototype_with_mappings)
    result = PrototypeWithMappingsMapper.from_dict(prototype_with_mappings_dict)

    assert result["prototype"].id() == prototype_with_mappings["prototype"].id()
    assert result["prototype"].tenant_id() == prototype_with_mappings["prototype"].tenant_id()
    assert result["prototype"].name == prototype_with_mappings["prototype"].name
    assert result["prototype"].engine == prototype_with_mappings["prototype"].engine
    assert result["prototype"].language == prototype_with_mappings["prototype"].language
    assert result["prototype"].description == prototype_with_mappings["prototype"].description

    assert len(result["mappings"]) == len(prototype_with_mappings["mappings"])

    for result_mapping, mapping in zip(result["mappings"], prototype_with_mappings["mappings"]):
        assert result_mapping.code == mapping.code
        assert result_mapping.prototype_id() == mapping.prototype_id()
        assert result_mapping.data_type == mapping.data_type
        assert result_mapping.mapping_type == mapping.mapping_type
        assert result_mapping.keys == mapping.keys
        assert result_mapping.created_at == mapping.created_at
        assert result_mapping.allocators == mapping.allocators

    assert len(result["tabular_mappings"]) == len(prototype_with_mappings["tabular_mappings"])

    for result_tabular_mapping, tabular_mapping in zip(
        result["tabular_mappings"],
        prototype_with_mappings["tabular_mappings"],
    ):
        assert result_tabular_mapping.code == tabular_mapping.code
        assert result_tabular_mapping.prototype_id() == tabular_mapping.prototype_id()
        assert result_tabular_mapping.headers == tabular_mapping.headers
        assert result_tabular_mapping.header_type == tabular_mapping.header_type
        assert result_tabular_mapping.occurrence_index == tabular_mapping.occurrence_index
        assert result_tabular_mapping.created_at == tabular_mapping.created_at
