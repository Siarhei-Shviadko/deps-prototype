from deps_message_flow.events.publisher import DomainEventPublisher

from deps_prototype.domain.exceptions import (
    MappingAlreadyExists,
    MappingNotFound,
    PrototypeNotFound,
)
from deps_prototype.domain.model import (
    DataTypeCode,
    IMappingRepository,
    IPrototypeRepository,
    Mapping,
    MappingFactory,
    MappingType,
    UniqueList,
)

__all__ = ["MappingService"]


class MappingService:
    def __init__(
        self,
        mapping_repository: IMappingRepository,
        prototype_repository: IPrototypeRepository,
        domain_event_publisher: DomainEventPublisher,
    ) -> None:
        self._mapping_repository = mapping_repository
        self._prototype_repository = prototype_repository
        self._domain_event_publisher = domain_event_publisher

    def create_mapping(
        self,
        code: str,
        prototype_id: str,
        tenant_id: str,
        data_type: DataTypeCode,
        mapping_type: MappingType,
        keys: UniqueList[str],
    ) -> Mapping:
        self._check_prototype_existence(prototype_id=prototype_id, tenant_id=tenant_id)

        mapping = self._create_mapping(
            code=code,
            prototype_id=prototype_id,
            data_type=data_type,
            mapping_type=mapping_type,
            keys=keys,
        )

        self._mapping_repository.save(mapping)

        return mapping

    def delete_mapping(self, prototype_id: str, tenant_id: str, mapping_code: str) -> None:
        self._check_prototype_existence(prototype_id=prototype_id, tenant_id=tenant_id)

        self._mapping_repository.delete(mapping_code=mapping_code, prototype_id=prototype_id)

    def modify_mapping(
        self,
        prototype_id: str,
        mapping_code: str,
        tenant_id: str,
        keys: UniqueList[str],
    ) -> Mapping:
        mapping = self._find_mapping(prototype_id=prototype_id, tenant_id=tenant_id, mapping_code=mapping_code)
        mapping.update(keys=keys)

        self._mapping_repository.save(mapping)

        return mapping

    def _find_mapping(self, prototype_id: str, tenant_id: str, mapping_code: str) -> Mapping:
        self._check_prototype_existence(prototype_id=prototype_id, tenant_id=tenant_id)
        if mapping := self._mapping_repository.mapping_by_code(code=mapping_code, prototype_id=prototype_id):
            return mapping

        raise MappingNotFound(mapping_code)

    def _check_prototype_existence(self, prototype_id: str, tenant_id: str) -> None:
        if self._prototype_repository.has_prototype_of_id(id_=prototype_id, tenant_id=tenant_id):
            return

        raise PrototypeNotFound(prototype_id)

    def _create_mapping(
        self,
        code: str,
        prototype_id: str,
        data_type: DataTypeCode,
        mapping_type: MappingType,
        keys: UniqueList[str],
    ) -> Mapping:
        if self._mapping_repository.mapping_by_code(code=code, prototype_id=prototype_id) is not None:
            raise MappingAlreadyExists(code)

        return MappingFactory.create(
            code=code,
            prototype_id=prototype_id,
            data_type=data_type,
            mapping_type=mapping_type,
            keys=keys,
        )
