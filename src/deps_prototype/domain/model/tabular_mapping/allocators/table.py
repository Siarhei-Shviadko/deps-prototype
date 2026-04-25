from dataclasses import dataclass
from typing import Generator

from deps_extracted_data import RawCell, TableCellCoordinates
from deps_extracted_data.model import SourceBboxCoordinates

from ...shared import Cell, Table
from ..header_type import HeaderType

__all__ = ["AllocatedTable"]


@dataclass
class AllocatedTable:
    table: Table
    header_type: HeaderType
    allocated_headers_indexes: list[int]

    def __post_init__(self) -> None:
        self._header_index_to_cells: dict[int, list[Cell]] = {
            header_index: self._list_header_cells(header_index) for header_index in self.allocated_headers_indexes
        }

    @property
    def table_coordinates(self) -> SourceBboxCoordinates:
        return SourceBboxCoordinates(
            value=self.table.page_id,
            bboxes=[self.table.polygon.to_bbox()],
        )

    @property
    def columns_x_coordinates(self) -> list[float]:
        header_type_to_coordinates = {
            HeaderType.COLUMNS: self._column_x_coordinates__column_header,
            HeaderType.ROWS: self._column_x_coordinates__row_header,
        }

        return header_type_to_coordinates[self.header_type]()

    @property
    def rows_y_coordinates(self) -> list[float]:
        header_type_to_coordinates = {
            HeaderType.COLUMNS: self._row_y_coordinates__column_header,
            HeaderType.ROWS: self._row_y_coordinates__row_header,
        }

        return header_type_to_coordinates[self.header_type]()

    def iter_table_cells_as_extracted(self) -> Generator[RawCell, None, None]:
        for positional_column_idx, header_index in enumerate(self.allocated_headers_indexes):
            cells = self._header_index_to_cells[header_index]

            # skip first header cell, as it is a header itself
            for positional_row_idx, cell in enumerate(cells[1:]):
                yield (
                    cell.content,
                    cell.confidence,
                    TableCellCoordinates(
                        column=positional_column_idx,
                        row=positional_row_idx,
                        column_span=1,
                        row_span=1,
                    ),
                    cell.source_bbox_coordinates,
                    None,
                )

    def _list_header_cells(self, index: int) -> list[Cell]:
        if self.header_type == HeaderType.ROWS:
            return [cell for cell in self.table.cell if cell.row_index == index]

        return [cell for cell in self.table.cell if cell.column_index == index]

    def _column_x_coordinates__column_header(self) -> list[float]:
        columns_coordinates: list[float] = []

        for header_index in self.allocated_headers_indexes:
            header_cells_coordinates: list[float] = [
                min(cell.polygon.xs) for cell in self._header_index_to_cells[header_index]
            ]
            columns_coordinates.append(min(header_cells_coordinates))

        return columns_coordinates

    def _column_x_coordinates__row_header(self) -> list[float]:
        columns_coordinates: list[float] = []

        # we assume that all headers have the same number of columns
        first_row: list[Cell] = list(self._header_index_to_cells.values())[0]

        # skip first header cell, as it is a header itself
        for cell in first_row[1:]:
            columns_coordinates.append(min(cell.polygon.xs))

        return columns_coordinates

    def _row_y_coordinates__column_header(self) -> list[float]:
        rows_coordinates: list[float] = []

        # we assume that all headers have the same number of rows
        first_column: list[Cell] = list(self._header_index_to_cells.values())[0]

        # skip first header cell, as it is a header itself
        for cell in first_column[1:]:
            rows_coordinates.append(min(cell.polygon.ys))

        return rows_coordinates

    def _row_y_coordinates__row_header(self) -> list[float]:
        rows_coordinates: list[float] = []

        for header_index in self.allocated_headers_indexes:
            header_cells_coordinates: list[float] = [
                min(cell.polygon.ys) for cell in self._header_index_to_cells[header_index]
            ]
            rows_coordinates.append(min(header_cells_coordinates))

        return rows_coordinates
