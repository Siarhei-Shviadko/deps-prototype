from deps_prototype.domain.model import IPrototypeRepository, IReferenceLayoutRepository
from tests.factories import PrototypeFactory, ReferenceLayoutFactory


def test__save_reference_layout__delete_reference_layout__success(
    prototype_repository: IPrototypeRepository,
    reference_layout_repository: IReferenceLayoutRepository,
    prototype,
    reference_layout,
):
    prototype_repository.save(prototype)
    reference_layout_repository.save(reference_layout)
    saved_reference_layout = reference_layout_repository.reference_layout_of_id(
        id_=reference_layout.id(),
        prototype_id=reference_layout.prototype_id(),
    )

    assert saved_reference_layout == reference_layout

    reference_layout_repository.delete(reference_layout=reference_layout)
    deleted_reference_layout = reference_layout_repository.reference_layout_of_id(
        id_=reference_layout.id(),
        prototype_id=reference_layout.prototype_id(),
    )

    assert deleted_reference_layout is None


def test_find_reference_layouts_of_ids__success(
    prototype_repository: IPrototypeRepository,
    reference_layout_repository: IReferenceLayoutRepository,
    prototype,
):
    prototype_repository.save(prototype)

    reference_layout1 = ReferenceLayoutFactory(prototype_id=prototype.id)
    reference_layout2 = ReferenceLayoutFactory(prototype_id=prototype.id)

    reference_layout_repository.save(reference_layout1)
    reference_layout_repository.save(reference_layout2)

    reference_layouts = reference_layout_repository.reference_layouts_of_ids(
        ids=[reference_layout1.id(), reference_layout2.id()],
        prototype_id=prototype.id(),
    )

    assert reference_layouts == [reference_layout1, reference_layout2]


def test_find_reference_layouts_of_prototype__success(
    prototype_repository: IPrototypeRepository,
    reference_layout_repository: IReferenceLayoutRepository,
    reference_layout,
    prototype,
):
    prototype_repository.save(prototype)
    reference_layout_repository.save(reference_layout)

    for i in range(3):
        other_prototype = PrototypeFactory()
        prototype_repository.save(other_prototype)
        other_reference_layout = ReferenceLayoutFactory(prototype_id=other_prototype.id)
        reference_layout_repository.save(other_reference_layout)

    assert reference_layout_repository.reference_layouts_of_prototype(prototype.id()) == [reference_layout]


def test_reference_layouts_of_prototype__not_exist__empty_list(
    prototype_repository: IPrototypeRepository,
    reference_layout_repository: IReferenceLayoutRepository,
    prototype,
    reference_layout,
):
    prototype_repository.save(prototype)
    reference_layout_repository.save(reference_layout)

    other_prototype = PrototypeFactory()

    assert reference_layout_repository.reference_layouts_of_prototype(other_prototype.id()) == []


def test_delete_all__reference_layouts_not_exist__no_error(
    prototype_repository: IPrototypeRepository,
    reference_layout_repository: IReferenceLayoutRepository,
    prototype,
    reference_layout,
):
    prototype_repository.save(prototype)
    reference_layout_repository.save(reference_layout)

    reference_layout_repository.delete_all([reference_layout])

    found_reference_layout = reference_layout_repository.reference_layout_of_id(
        id_=reference_layout.id(),
        prototype_id=reference_layout.prototype_id(),
    )

    assert not found_reference_layout


def test_delete_all__reference_layouts_exist__deleted(
    prototype_repository: IPrototypeRepository,
    reference_layout_repository: IReferenceLayoutRepository,
    prototype,
    reference_layout,
):
    prototype_repository.save(prototype)
    reference_layout_repository.save(reference_layout)

    other_reference_layout = ReferenceLayoutFactory(prototype_id=prototype.id)
    reference_layout_repository.save(other_reference_layout)

    reference_layout_repository.delete_all([reference_layout, other_reference_layout])

    reference_layouts = reference_layout_repository.reference_layouts_of_ids(
        ids=[reference_layout.id(), other_reference_layout.id()],
        prototype_id=prototype.id(),
    )

    assert reference_layouts == []
