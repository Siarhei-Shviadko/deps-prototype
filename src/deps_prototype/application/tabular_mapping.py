from deps_prototype.domain.exceptions import (
    PrototypeNotFound,
    TabularMappingAlreadyExists,
    TabularMappingNotFound,
)
from deps_prototype.domain.model import (
    HeaderType,
    IPrototypeRepository,
    ITabularMappingRepository,
    RawHeader,
    TabularMapping,
    TabularMappingFactory,
)

__all__ = ["TabularMappingService"]


class TabularMappingService:
    def __init__(
        self,
        tabular_mapping_repository: ITabularMappingRepository,
        prototype_repository: IPrototypeRepository,
    ) -> None:
        self._tabular_mapping_repository = tabular_mapping_repository
        self._prototype_repository = prototype_repository

    def create_tabular_mapping(
        self,
        code: str,
        prototype_id: str,
        tenant_id: str,
        header_type: HeaderType,
        headers: list[RawHeader],
        occurrence_index: int,
    ) -> TabularMapping:
        self._check_prototype_existence(prototype_id=prototype_id, tenant_id=tenant_id)

        if self._tabular_mapping_repository.get_by_code(code, prototype_id) is not None:
            raise TabularMappingAlreadyExists(code)

        mapping = TabularMappingFactory.create(
            code=code,
            prototype_id=prototype_id,
            header_type=header_type,
            headers=headers,
            occurrence_index=occurrence_index,
        )
        self._tabular_mapping_repository.save(mapping)

        return mapping

    def update_tabular_mapping(
        self,
        prototype_id: str,
        tenant_id: str,
        code: str,
        header_type: HeaderType | None = None,
        headers: list[RawHeader] | None = None,
        occurrence_index: int | None = None,
    ) -> TabularMapping:
        mapping = self._find_mapping(prototype_id=prototype_id, tenant_id=tenant_id, code=code)

        if all(value_to_update is None for value_to_update in (header_type, headers, occurrence_index)):
            return mapping

        mapping.update(header_type=header_type, headers=headers, occurrence_index=occurrence_index)
        self._tabular_mapping_repository.save(tabular_mapping=mapping)

        return mapping

    def _check_prototype_existence(self, prototype_id: str, tenant_id: str) -> None:
        if self._prototype_repository.has_prototype_of_id(id_=prototype_id, tenant_id=tenant_id):
            return

        raise PrototypeNotFound(prototype_id)

    def _find_mapping(self, prototype_id: str, tenant_id: str, code: str) -> TabularMapping:
        self._check_prototype_existence(prototype_id=prototype_id, tenant_id=tenant_id)
        if tabular_mapping := self._tabular_mapping_repository.get_by_code(code=code, prototype_id=prototype_id):
            return tabular_mapping

        raise TabularMappingNotFound(code)
