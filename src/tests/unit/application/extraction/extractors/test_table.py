import pytest
from deps_extracted_data.model import ExtractedData, Table

from deps_prototype.application import TableExtractor
from deps_prototype.domain.model import AllocatedTable, DocumentLayout, TabularMapping

FIRST_ELEMENT: int = 0


@pytest.mark.extraction
def test_extract__ok(
    tabular_mapping__specific_table__row_oriented: TabularMapping,
    test_allocated_table__row: AllocatedTable,
    document_layout: DocumentLayout,
    extracted_data: ExtractedData,
) -> None:
    extractor = TableExtractor()

    extractor.extract(test_allocated_table__row, tabular_mapping__specific_table__row_oriented, extracted_data)

    assert len(extracted_data.fields) == 1
    field = extracted_data.fields[FIRST_ELEMENT]

    assert isinstance(field.data, Table)
    assert field.field_code == tabular_mapping__specific_table__row_oriented.code

    table_data = field.data
    assert [c.x for c in table_data.columns] == test_allocated_table__row.columns_x_coordinates
    assert [r.y for r in table_data.rows] == test_allocated_table__row.rows_y_coordinates

    assert len(table_data.cells) == len(list(test_allocated_table__row.iter_table_cells_as_extracted()))

    layout_cells = list(test_allocated_table__row.iter_table_cells_as_extracted())
    first_ed_cell, first_layout_cell = table_data.cells[FIRST_ELEMENT], layout_cells[FIRST_ELEMENT]

    assert first_ed_cell.value == first_layout_cell[0]
    assert first_ed_cell.confidence == first_layout_cell[1]
    assert first_ed_cell.table_cell_coordinates == first_layout_cell[2]
    assert first_ed_cell.source_bbox_coordinates == first_layout_cell[3]
