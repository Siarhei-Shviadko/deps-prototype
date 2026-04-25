import pytest

from deps_prototype.domain.model import AllocatedTable


@pytest.mark.tabular_mappings
def test_allocated_table_rows_coordinates(
    test_allocated_table__row: AllocatedTable,
    test_allocated_table__column: AllocatedTable,
) -> None:
    assert test_allocated_table__row.rows_y_coordinates == [0.24478245489918643]
    assert test_allocated_table__column.rows_y_coordinates == [
        0.4372125928546162,
        0.48107534488857445,
        0.5256455606650159,
        0.5695083126989742,
        0.6098337460205164,
        0.6441457375309515,
    ]


@pytest.mark.tabular_mappings
def test_allocated_table_columns_coordinates(
    test_allocated_table__row: AllocatedTable,
    test_allocated_table__column: AllocatedTable,
) -> None:
    assert test_allocated_table__row.columns_x_coordinates == [0.704]
    assert test_allocated_table__column.columns_x_coordinates == [0.7695, 0.3435]


@pytest.mark.tabular_mappings
def test_allocated_table_counting_cells(
    test_allocated_table__row: AllocatedTable,
    test_allocated_table__column: AllocatedTable,
) -> None:
    assert len(list(test_allocated_table__row.iter_table_cells_as_extracted())) == 1
    assert len(list(test_allocated_table__column.iter_table_cells_as_extracted())) == 12
