from typing import Generic, Iterable, TypeVar, Union

from ...exceptions import InvariantViolation

__all__ = ["UniqueList"]

T = TypeVar("T")


class UniqueList(Generic[T], list):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        if len(self) != len(set(self)):
            raise InvariantViolation("All values in the list must be unique.")

    def append(self, value: T) -> None:
        self._check_invariant(value)
        return super().append(value)

    def insert(self, index: int, value: T) -> None:  # type: ignore
        self._check_invariant(value)
        return super().insert(index, value)

    def extend(self, iterable: Iterable) -> None:
        self._check_invariant(iterable)
        return super().extend(iterable)

    def _check_invariant(self, value: Union[T, Iterable]) -> None:
        if isinstance(value, Iterable):
            if set(value).intersection(set(self)):
                raise InvariantViolation("All values in the list must be unique.")
        if value in self:
            raise InvariantViolation(f"Value `{value}` has already exist!")
