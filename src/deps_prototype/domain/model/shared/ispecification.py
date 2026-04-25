from abc import ABC, abstractmethod
from typing import Generic, TypeVar

__all__ = ["ISpecification"]

T = TypeVar("T")


class ISpecification(Generic[T], ABC):
    def __init__(self, entity: T) -> None:
        self._entity = entity

    @abstractmethod
    def check(self) -> None:
        pass

    @staticmethod
    @abstractmethod
    def _is_satisfied_by(entity: T) -> bool:
        pass
