from .base import BusinessException, NotFoundError

__all__ = ["PrototypeNotFound", "PrototypeHasDocument"]


class PrototypeNotFound(NotFoundError):
    code = "prototype_not_found"

    def __init__(self, id_: str) -> None:
        super().__init__(f"Prototype with id: `{id_}` not found")


class PrototypeHasDocument(BusinessException):
    code = "prototype_has_document"
