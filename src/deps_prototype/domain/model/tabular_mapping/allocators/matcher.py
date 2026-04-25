from difflib import SequenceMatcher

from ...shared import Cell
from ..header import Header

__all__ = ["HeaderMatchingEngine"]

AllocatedIndexes = list[int]


class HeaderMatchingEngine:
    _SIMILARITY_THRESHOLD = 0.8

    def match_table_headers(
        self,
        table_headers: list[Cell],
        mapping_headers: list[Header],
    ) -> AllocatedIndexes | None:
        allocated_indexes: AllocatedIndexes = []

        for header_to_find in mapping_headers:
            for alias in header_to_find.aliases:
                found_header_idx = self._search_for_header_alias(
                    alias=alias,
                    table_headers=table_headers,
                    allocated_headers_indexes=allocated_indexes,
                )

                if found_header_idx is not None:
                    allocated_indexes.append(found_header_idx)
                    break

        # table is allocated only if all headers are found
        if len(allocated_indexes) != len(mapping_headers):
            return None

        return allocated_indexes

    def _search_for_header_alias(
        self,
        alias: str,
        table_headers: list[Cell],
        allocated_headers_indexes: AllocatedIndexes,
    ) -> int | None:
        for idx, table_header in enumerate(table_headers):
            if self._strings_fuzzy_equal(table_header.content, alias) and idx not in allocated_headers_indexes:
                return idx

        return None

    def _strings_fuzzy_equal(self, str1: str, str2: str) -> bool:
        return SequenceMatcher(None, str1.lower().strip(), str2.lower().strip()).ratio() > self._SIMILARITY_THRESHOLD
