from ..shared import EntityId
from .header import Header
from .header_type import HeaderType
from .raw_header import RawHeader
from .tabular_mapping import TabularMapping

__all__ = ["TabularMappingFactory"]


class TabularMappingFactory:
    @staticmethod
    def create(
        code: str,
        prototype_id: str,
        header_type: HeaderType,
        headers: list[RawHeader],
        occurrence_index: int,
    ) -> TabularMapping:
        return TabularMapping(
            code=code,
            prototype_id=EntityId(prototype_id),
            header_type=header_type,
            headers=[Header(name=raw_header["name"], aliases=raw_header["aliases"]) for raw_header in headers],
            occurrence_index=occurrence_index,
        )
