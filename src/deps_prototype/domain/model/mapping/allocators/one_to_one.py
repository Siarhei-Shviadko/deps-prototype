from ...shared import KeyValuePair
from .abstract import Allocator

__all__ = ["OneToOneAllocator"]


class OneToOneAllocator(Allocator):
    def allocate(self) -> list[KeyValuePair]:
        for key_value_pair in self._document_layout.key_value_pairs:
            if self.comparer.is_content_satisfying(self._keys, key_value_pair.key_content):
                return [key_value_pair]

        return []
