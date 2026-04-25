from ..shared import EntityId, UniqueList
from .data_type import DataTypeCode
from .mapping import Mapping
from .mapping_type import MappingType

__all__ = ["MappingFactory"]


class MappingFactory:
    @staticmethod
    def create(
        code: str,
        prototype_id: str,
        data_type: DataTypeCode,
        keys: UniqueList[str],
        mapping_type: MappingType,
    ) -> Mapping:
        return Mapping(
            code=code,
            prototype_id=EntityId(prototype_id),
            data_type=DataTypeCode(data_type),
            mapping_type=MappingType(mapping_type),
            keys=keys,
        )
