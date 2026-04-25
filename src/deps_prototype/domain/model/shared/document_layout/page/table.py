from dataclasses import dataclass
from typing import Any

from deps_extracted_data.model import SourceBboxCoordinates

from .polygon import Polygon

__all__ = ["Cell", "Table"]

_DEFAULT_CONFIDENCE = -1.0


@dataclass
class Cell:
    page_id: str
    content: str
    column_index: int
    column_span: int
    row_index: int
    row_span: int
    kind: str
    polygon: Polygon
    confidence: float = _DEFAULT_CONFIDENCE

    @classmethod
    def from_dict(cls, page_id: str, cell: dict[str, Any], paragraphs_store: dict[str, dict[str, Any]]) -> "Cell":
        if cell.get("paragraphId") in paragraphs_store:
            cell["content"] = paragraphs_store[cell["paragraphId"]]["content"]
            cell["confidence"] = paragraphs_store[cell["paragraphId"]]["confidence"]

        return cls(
            page_id=page_id,
            content=cell["content"],
            column_index=cell["columnIndex"],
            column_span=cell["columnSpan"],
            row_index=cell["rowIndex"],
            row_span=cell["rowSpan"],
            kind=cell["kind"],
            polygon=Polygon.from_dict(cell["polygon"]),
            confidence=cell.get("confidence", _DEFAULT_CONFIDENCE),
        )

    @property
    def source_bbox_coordinates(self) -> list[SourceBboxCoordinates]:
        return [
            SourceBboxCoordinates(
                value=self.page_id,
                bboxes=[self.polygon.to_bbox()],
            ),
        ]

    def recreate_unmerged(self, column_offset: int = 0, row_offset: int = 0) -> "Cell":
        return Cell(
            page_id=self.page_id,
            content=self.content if column_offset == 0 and row_offset == 0 else "",
            column_index=self.column_index + column_offset,
            column_span=1,
            row_index=self.row_index + row_offset,
            row_span=1,
            kind=self.kind,
            polygon=self.polygon,  # Assuming polygon is the same for all unmerged cells
            confidence=self.confidence,
        )


@dataclass
class Table:
    page_id: str
    confidence: float
    column_count: int
    row_count: int
    polygon: Polygon
    cell: list[Cell]

    @classmethod
    def from_dict(cls, page_id: str, table: dict[str, Any], paragraphs_store: dict[str, dict[str, Any]]) -> "Table":
        return cls(
            page_id=page_id,
            confidence=table["confidence"],
            column_count=table["columnCount"],
            row_count=table["rowCount"],
            polygon=Polygon.from_dict(table["polygon"]),
            cell=[Cell.from_dict(page_id, cell, paragraphs_store) for cell in table["cells"]],
        )

    def recreate_with_unmerged_cells(self) -> "Table":
        return Table(
            page_id=self.page_id,
            confidence=self.confidence,
            column_count=self.column_count,
            row_count=self.row_count,
            polygon=self.polygon,
            cell=self._unmerge_cells(),
        )

    def _unmerge_cells(self) -> list[Cell]:
        unmerged_cells = []

        for cell in self.cell:
            for column_offset in range(cell.column_span):
                for row_offset in range(cell.row_span):
                    unmerged_cells.append(
                        cell.recreate_unmerged(column_offset=column_offset, row_offset=row_offset),
                    )

        return unmerged_cells
