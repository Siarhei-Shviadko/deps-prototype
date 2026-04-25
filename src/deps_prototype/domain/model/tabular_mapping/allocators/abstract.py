from abc import ABC, abstractmethod

from ...shared import Cell, DocumentLayout, Table
from ..header import Header
from ..header_type import HeaderType
from .matcher import HeaderMatchingEngine
from .table import AllocatedTable

__all__ = ["TabularAllocator"]


class TabularAllocator(ABC):
    matcher = HeaderMatchingEngine()

    def __init__(
        self,
        document_layout: DocumentLayout,
        headers: list[Header],
        occurrence_index: int,
        header_type: HeaderType,
    ) -> None:
        self._document_layout = document_layout
        self._headers = headers
        self._occurrence_index = occurrence_index
        self._header_type = header_type

    def allocate(self) -> AllocatedTable | None:
        if self._occurrence_index < 0:
            return self._allocate_by_negative_index()

        return self._allocate_by_positive_index()

    @abstractmethod
    def _get_table_header(self, table: Table) -> list[Cell]:
        pass

    def _allocate_by_positive_index(self) -> AllocatedTable | None:
        match_index: int = 0

        for page in self._document_layout.pages:
            for table in page.tables:
                unmerged_cells_table: Table = table.recreate_with_unmerged_cells()

                table_header: list[Cell] = self._get_table_header(unmerged_cells_table)

                matched_headers: list[int] = self.matcher.match_table_headers(
                    table_headers=table_header,
                    mapping_headers=self._headers,
                )

                if matched_headers is None:
                    continue

                if match_index == self._occurrence_index:
                    return AllocatedTable(
                        table=unmerged_cells_table,
                        allocated_headers_indexes=matched_headers,
                        header_type=self._header_type,
                    )

                match_index += 1

        return None

    def _allocate_by_negative_index(self) -> AllocatedTable | None:
        tables_matching_headers: list[AllocatedTable] = []

        for page in self._document_layout.pages:
            for table in page.tables:
                unmerged_cells_table: Table = table.recreate_with_unmerged_cells()

                table_header: list[Cell] = self._get_table_header(unmerged_cells_table)

                matched_headers: list[int] = self.matcher.match_table_headers(
                    table_headers=table_header,
                    mapping_headers=self._headers,
                )

                if matched_headers is None:
                    continue

                tables_matching_headers.append(
                    AllocatedTable(
                        table=unmerged_cells_table,
                        allocated_headers_indexes=matched_headers,
                        header_type=self._header_type,
                    ),
                )

        if not tables_matching_headers or abs(self._occurrence_index) > len(tables_matching_headers):
            return None

        return tables_matching_headers[self._occurrence_index]
