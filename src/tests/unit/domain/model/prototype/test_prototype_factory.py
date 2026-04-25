from deps_prototype.domain.model import PrototypeCreated, PrototypeFactory


def test_prototype_factory(tenant_id, prototype_id):
    name = "TestPrototype"
    description = "Test prototype"
    engine = "TESSERACT"
    language = "eng"

    prototype = PrototypeFactory.make(
        id_=prototype_id,
        tenant_id=tenant_id,
        name=name,
        description=description,
        engine=engine,
        language=language,
    )

    assert prototype.id() == prototype_id
    assert prototype.tenant_id() == tenant_id
    assert prototype.name == name
    assert prototype.description == description
    assert prototype.engine == engine
    assert prototype.language == language

    assert len(prototype.events) == 1
    assert isinstance(prototype.events[0], PrototypeCreated)
