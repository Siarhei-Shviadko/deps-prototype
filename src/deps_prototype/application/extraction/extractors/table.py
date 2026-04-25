from deps_extracted_data import ExtractedData

from deps_prototype.domain.model import AllocatedTable, TabularMapping

from .abstract import ITableExtractor

__all__ = ["TableExtractor"]


class TableExtractor(ITableExtractor):
    def extract(self, data: AllocatedTable, mapping: TabularMapping, extracted_data: ExtractedData) -> None:
        table = self.extracted_field_factory.create_table(
            field_code=mapping.code,
            columns=data.columns_x_coordinates,
            rows=data.rows_y_coordinates,
            cells=list(data.iter_table_cells_as_extracted()),
            coordinates=data.table_coordinates,
        )

        extracted_data.add_table(table)
