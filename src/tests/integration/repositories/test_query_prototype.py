from deps_prototype.domain.model import (
    IMappingRepository,
    IPrototypeRepository,
    IQueryPrototypeRepository,
    ITabularMappingRepository,
    PrototypeWithMappings,
)


def test_query_prototype_repository__find_prototype_with_mappings(
    prototype_repository: IPrototypeRepository,
    mapping_repository: IMappingRepository,
    tabular_mapping_repository: ITabularMappingRepository,
    query_prototype_repository: IQueryPrototypeRepository,
    prototype_with_mappings: PrototypeWithMappings,
):
    prototype_repository.save(prototype_with_mappings["prototype"])
    for mapping in prototype_with_mappings["mappings"]:
        mapping_repository.save(mapping)
    for tabular_mapping in prototype_with_mappings["tabular_mappings"]:
        tabular_mapping_repository.save(tabular_mapping)

    assert (
        query_prototype_repository.find_prototype_with_mappings(
            id_=prototype_with_mappings["prototype"].id(), tenant_id=prototype_with_mappings["prototype"].tenant_id()
        )
        == prototype_with_mappings
    )
