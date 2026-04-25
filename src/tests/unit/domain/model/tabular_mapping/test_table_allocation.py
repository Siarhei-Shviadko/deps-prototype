import pytest

from deps_prototype.domain.model import DocumentLayout, Header, TabularMapping


@pytest.mark.tabular_mappings
def test_search_data__nothing_allocated(
    document_layout: DocumentLayout,
    tabular_mapping: TabularMapping,
) -> None:
    assert tabular_mapping.search_data(document_layout) is None


@pytest.mark.tabular_mappings
@pytest.mark.parametrize(
    "aliases, occurrence_index, table_exist, expected_header_indexes",
    [
        (
            [{"ADDRESS"}, {"SHIP TO / COSIGNEE"}, {"EMAIL"}, {"PHONE / FAX"}],
            0,
            True,
            [2, 0, 5, 4],
        ),
        (
            [{"ADDRESS"}, {"SHIP TO / COSIGNEE"}, {"EMAIL"}, {"PHONE / FAX"}],
            -1,
            True,
            [2, 0, 5, 4],
        ),
        (
            [{"ADDRESS"}, {"PHONE", "FAX", "PHONE/ FAX"}],
            0,
            True,
            [2, 4],
        ),
        (
            [{"ADDRESS"}, {"SHIP TO / COSIGNEE"}, {"EMAIL"}, {"PHONE"}],
            0,
            False,
            None,
        ),
        (
            [{"ADDRESS"}],
            1,
            False,
            None,
        ),
        (
            [{"ADDRESS"}],
            -4,
            False,
            None,
        ),
        (
            [{"address"}, {"SHIP to/ COSIGNEE"}, {"eMAIL "}, {"PHONE/ fax"}],
            0,
            True,
            [2, 0, 5, 4],
        ),
    ],
)
def test_search_data__row_mapping(
    document_layout: DocumentLayout,
    tabular_mapping__row_headers: TabularMapping,
    aliases: list[set[str]],
    expected_header_indexes: list[int],
    table_exist: bool,
    occurrence_index: int,
) -> None:
    headers = [Header(name=f"header{i}", aliases=alias) for i, alias in enumerate(aliases)]
    tabular_mapping__row_headers.headers = headers
    tabular_mapping__row_headers.occurrence_index = occurrence_index

    allocated_table = tabular_mapping__row_headers.search_data(document_layout)

    if table_exist:
        assert allocated_table is not None
        assert allocated_table.allocated_headers_indexes == expected_header_indexes
    else:
        assert allocated_table is None


@pytest.mark.tabular_mappings
@pytest.mark.parametrize(
    "aliases, occurrence_index, table_exist, expected_header_indexes",
    [
        (
            [{"Product"}],
            0,
            True,
            [0],
        ),
        (
            [{"Product"}, {"amount"}, {"unit-price"}],
            0,
            True,
            [0, 3, 2],
        ),
        (
            [{"Product"}],
            -1,
            True,
            [0],
        ),
        (
            [{"Product"}],
            -5,
            False,
            None,
        ),
        (
            [{"Product "}],
            0,
            True,
            [0],
        ),
        (
            [{"Product asdf"}],
            0,
            False,
            None,
        ),
        (
            [{"Product asdf", "product"}],
            0,
            True,
            [0],
        ),
    ],
)
def test_search_data__column_mapping(
    document_layout: DocumentLayout,
    tabular_mapping__column_headers: TabularMapping,
    aliases: list[set[str]],
    expected_header_indexes: list[int],
    table_exist: bool,
    occurrence_index: int,
) -> None:
    headers = [Header(name=f"header{i}", aliases=alias) for i, alias in enumerate(aliases)]
    tabular_mapping__column_headers.headers = headers
    tabular_mapping__column_headers.occurrence_index = occurrence_index

    allocated_table = tabular_mapping__column_headers.search_data(document_layout)

    if table_exist:
        assert allocated_table is not None
        assert allocated_table.allocated_headers_indexes == expected_header_indexes
    else:
        assert allocated_table is None


def test_merged_cells_allocation__merged_cells_in_data(
    document_layout_merged_cells: DocumentLayout,
    tabular_mapping__column_headers: TabularMapping,
) -> None:
    tabular_mapping__column_headers.headers = [
        Header(name="AppName", aliases={"app name"}),
        Header(name="File", aliases={"file"}),
        Header(name="Drugs", aliases={"drugs"}),
        Header(name="City", aliases={"city"}),
    ]
    tabular_mapping__column_headers.occurrence_index = 0

    allocated_table = tabular_mapping__column_headers.search_data(document_layout_merged_cells)

    assert allocated_table is not None
    assert allocated_table.allocated_headers_indexes == [0, 1, 2, 3]

    cells = list(allocated_table.iter_table_cells_as_extracted())
    assert len(cells) == 20

    assert allocated_table.rows_y_coordinates == [
        0.48833686761587397,
        0.5089366858527719,
        0.5280218115722508,
        0.5280218115722508,
        0.5649803089972736,
    ]
    assert allocated_table.columns_x_coordinates == [
        0.11764705882352941,
        0.30823529411764705,
        0.4996078431372549,
        0.6901960784313725,
    ]

    assert cells[0][0] == "Y-Solowarm"
    assert cells[1][0] == "Home Ing"
    assert cells[2][0] == "Asoka"
    assert cells[3][0] == ""


def test_merged_cells_allocation__merged_cells_in_headers(
    document_layout_merged_cells: DocumentLayout,
    tabular_mapping__column_headers: TabularMapping,
) -> None:
    tabular_mapping__column_headers.headers = [
        Header(name="App Name", aliases={"app name"}),
        Header(name="File", aliases={"file"}),
        Header(name="Drug-City", aliases={"drug-city", "drug city"}),
        Header(name="Drug-City Empty Column", aliases={""}),
        Header(name="Data", aliases={"data"}),
        Header(name="Data Second Column", aliases={""}),
        Header(name="Data Third Column", aliases={""}),
    ]
    tabular_mapping__column_headers.occurrence_index = 0

    allocated_table = tabular_mapping__column_headers.search_data(document_layout_merged_cells)

    assert allocated_table is not None
    assert allocated_table.allocated_headers_indexes == [0, 1, 2, 3, 4, 5, 6]

    cells = list(allocated_table.iter_table_cells_as_extracted())
    assert len(cells) == 42

    assert allocated_table.columns_x_coordinates == [
        0.11764705882352941,
        0.22627450980392158,
        0.4596078431372549,
        0.4596078431372549,
        0.7658823529411765,
        0.7658823529411765,
        0.7658823529411765,
    ]
    assert allocated_table.rows_y_coordinates == [
        0.6664647076643442,
        0.7034232050893668,
        0.7225083308088458,
        0.7600727052408361,
        0.7976370796728264,
        0.8173280823992729,
    ]

    assert cells[0][0] == "Y- Solowarm"
    assert cells[1][0] == "Home Ing"
    assert cells[2][0] == "Asoka"
    assert cells[3][0] == "Matsoft"
