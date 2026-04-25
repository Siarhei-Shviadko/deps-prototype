from ...shared import KeyValuePair
from .abstract import Allocator

__all__ = ["OneToManyAllocator"]


class OneToManyAllocator(Allocator):
    def allocate(self) -> list[KeyValuePair]:
        key_value_pairs = []
        for key_value_pair in self._document_layout.key_value_pairs:
            if self.comparer.is_content_satisfying(self._keys, key_value_pair.key_content):
                key_value_pairs.append(key_value_pair)

        return key_value_pairs
