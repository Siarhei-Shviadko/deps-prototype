from ...shared import Cell, Table
from .abstract import TabularAllocator

__all__ = ["ColumnOrientedTabularAllocator"]


class ColumnOrientedTabularAllocator(TabularAllocator):
    def _get_table_header(self, table: Table) -> list[Cell]:
        return [cell for cell in table.cell if cell.row_index == 0]
