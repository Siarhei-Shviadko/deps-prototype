from .base import NotFoundError, PrototypeException

__all__ = ["ReferenceLayoutNotFound", "ReferenceLayoutCreationFailed", "ReferenceLayoutRestartingError"]


class ReferenceLayoutNotFound(NotFoundError):
    code = "reference_layout_not_found"

    def __init__(self, id_: str) -> None:
        super().__init__(f"ReferenceLayout with id: `{id_}` not found")


class ReferenceLayoutCreationFailed(PrototypeException):
    code = "reference_layout_creation_failed"


class ReferenceLayoutRestartingError(PrototypeException):
    code = "reference_layout_restarting_error"
