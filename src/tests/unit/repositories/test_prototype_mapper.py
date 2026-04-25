from deps_prototype.infrastructure.repositories import PrototypeMapper


def test_prototype_mapper__successful(prototype):
    prototype_dict = PrototypeMapper.to_dict(prototype)
    res = PrototypeMapper.from_dict(prototype_dict)

    assert res.id() == prototype.id()
    assert res.tenant_id() == prototype.tenant_id()
    assert res.name == prototype.name
    assert res.engine == prototype.engine
    assert res.language == prototype.language
    assert res.description == prototype.description
