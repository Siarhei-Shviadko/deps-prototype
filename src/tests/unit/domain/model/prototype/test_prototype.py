import pytest

from deps_prototype.domain.model import (
    EntityId,
    IllegalArgumentError,
    Prototype,
    PrototypeDeleted,
    PrototypeUpdated,
    ReferenceLayout,
)
from tests.factories import PrototypeFactory


@pytest.mark.prototype
def test_add_reference_layout__ok(prototype: Prototype, reference_layout: ReferenceLayout):
    new_reference_layout = prototype.add_reference_layout(
        state=reference_layout.state,
        blob_name=reference_layout.blob_name,
        title=reference_layout.title,
    )

    assert isinstance(new_reference_layout, ReferenceLayout)
    assert new_reference_layout.id
    assert isinstance(new_reference_layout.id, EntityId)
    assert new_reference_layout.prototype_id == new_reference_layout.prototype_id
    assert new_reference_layout.state == reference_layout.state
    assert new_reference_layout.blob_name == reference_layout.blob_name
    assert new_reference_layout.title == reference_layout.title


@pytest.mark.prototype
def test_update_info__all_fields(prototype: Prototype) -> None:
    prototype._events.clear()
    new_prototype = PrototypeFactory(id_=prototype.id, tenant_id=prototype.tenant_id)

    prototype.update_info(
        engine=new_prototype.engine,
        language=new_prototype.language,
        description=new_prototype.description,
    )

    assert prototype.engine == new_prototype.engine
    assert prototype.language == new_prototype.language
    assert prototype.description == new_prototype.description

    assert (
        PrototypeUpdated(
            prototype_id=new_prototype.id(),
            tenant_id=new_prototype.tenant_id(),
            engine=new_prototype.engine,
            language=new_prototype.language,
            description=new_prototype.description,
        )
        in prototype.events
    )


@pytest.mark.prototype
def test_update_info__all_are_none__not_updated(prototype: Prototype) -> None:
    prototype._events.clear()
    old_name = prototype.name
    old_engine = prototype.engine
    old_language = prototype.language
    old_description = prototype.description

    prototype.update_info()

    assert prototype.name == old_name
    assert prototype.engine == old_engine
    assert prototype.language == old_language
    assert prototype.description == old_description

    assert not prototype.events


@pytest.mark.prototype
def test_delete__event_added(prototype: Prototype) -> None:
    event = PrototypeDeleted(prototype_id=prototype.id(), tenant_id=prototype.tenant_id())
    assert event not in prototype.events

    prototype.delete()

    assert event in prototype.events


@pytest.mark.prototype
@pytest.mark.parametrize(
    "name,is_valid",
    (
        ("1", True),
        ("en", True),
        ("бе", True),
        ("钟希娜", True),
        ("Words with spaces", True),
        ("1234", True),
        ("snake_case", True),
        ("Words-with-dashes", True),
        ("Words-with-dashes and spaces", True),
        ("", False),
        (" ", False),
        ("-", False),
        ("%%$@", False),
        ("trailing space ", False),
        ("- Dash-started", False),
        ("Dash ended -", False),
        ("Multiple  Spaces", False),
        ("A + B", False),
        ("🐍", False),
    ),
)
def test_create__name_checked(name: str, is_valid: bool) -> None:
    if is_valid:
        assert PrototypeFactory(name=name).name == name
    else:
        with pytest.raises(IllegalArgumentError):
            PrototypeFactory(name=name)
