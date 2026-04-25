from deps_prototype.domain.exceptions import PrototypeNotFound
from deps_prototype.domain.model import (
    IMappingRepository,
    IPrototypeRepository,
    ITabularMappingRepository,
)

__all__ = ["UnifiedMappingService"]


class UnifiedMappingService:
    def __init__(
        self,
        mapping_repository: IMappingRepository,
        tabular_mapping_repository: ITabularMappingRepository,
        prototype_repository: IPrototypeRepository,
    ) -> None:
        self._mapping_repository = mapping_repository
        self._tabular_mapping_repository = tabular_mapping_repository
        self._prototype_repository = prototype_repository

    def delete_mappings(self, code: str, prototype_id: str, tenant_id: str) -> None:
        self._check_prototype_existence(prototype_id=prototype_id, tenant_id=tenant_id)

        self._mapping_repository.delete(mapping_code=code, prototype_id=prototype_id)
        self._tabular_mapping_repository.delete(code=code, prototype_id=prototype_id)

    def _check_prototype_existence(self, prototype_id: str, tenant_id: str) -> None:
        if self._prototype_repository.has_prototype_of_id(id_=prototype_id, tenant_id=tenant_id):
            return

        raise PrototypeNotFound(prototype_id)
