from typing import Protocol

from .filtering import PrototypeFilter
from .prototype import Prototype

__all__ = ["IPrototypeRepository"]


class IPrototypeRepository(Protocol):
    def find_by_filter(self, filter_: PrototypeFilter) -> list[Prototype]:
        pass

    def prototype_of_id(self, id_: str, tenant_id: str) -> Prototype | None:
        pass

    def has_prototype_of_id(self, id_: str, tenant_id: str) -> bool:
        pass

    def save(self, prototype: Prototype) -> None:
        pass

    def delete(self, prototype: Prototype) -> None:
        pass

    def delete_all(self, prototypes: list[Prototype]) -> None:
        pass

    def get_total_count_by_filter(self, filter_: PrototypeFilter) -> int:
        pass
