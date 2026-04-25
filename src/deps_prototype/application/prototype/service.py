import logging
from datetime import datetime

from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.sagas.orchestration import Saga, SagaInstanceFactory

from deps_prototype.constants import PROTOTYPE_AGGREGATE_TYPE
from deps_prototype.domain.exceptions import PrototypeHasDocument, PrototypeNotFound
from deps_prototype.domain.model import (
    IMappingRepository,
    IPrototypeRepository,
    Mapping,
    Prototype,
    PrototypeFilter,
    PrototypeSortingField,
    SortingDirection,
)
from deps_prototype.messaging.sagas import PrototypeCreationSaga
from deps_prototype.messaging.sagas_data import PrototypeCreationSagaData

from .interfaces import IDocumentProxy
from .prototype_list import PrototypeList

__all__ = ["PrototypeService"]


class PrototypeService:
    def __init__(
        self,
        prototype_repository: IPrototypeRepository,
        mapping_repository: IMappingRepository,
        domain_event_publisher: DomainEventPublisher,
        saga_instance_factory: SagaInstanceFactory,
        sagas: list[Saga],
        document_proxy: IDocumentProxy,
    ) -> None:
        self._prototype_repository = prototype_repository
        self._mapping_repository = mapping_repository
        self._domain_event_publisher = domain_event_publisher
        self._sagas = {saga.__class__: saga for saga in sagas}
        self._saga_instance_factory = saga_instance_factory
        self._document_proxy = document_proxy

        self._logger = logging.getLogger(self.__class__.__name__)

    def create_prototype(
        self,
        name: str,
        language: str,
        engine: str,
        tenant_id: str,
        description: str | None = None,
    ) -> str:
        prototype_saga_data = PrototypeCreationSagaData(
            name=name,
            language=language,
            engine=engine,
            tenant_id=tenant_id,
            description=description,
        )
        si = self._saga_instance_factory.create(
            self._sagas[PrototypeCreationSaga],
            prototype_saga_data,
        )
        self._logger.info(
            "Saga create_prototype %s is created",
            si.saga_id,
        )
        return prototype_saga_data.prototype_id

    def find_prototypes(
        self,
        page: int | None = None,
        per_page: int | None = None,
        tenant_id: str | None = None,
        ids: list[str] | None = None,
        name: str | None = None,
        engines: list[str] | None = None,
        languages: list[str] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        sorting_field: PrototypeSortingField = PrototypeSortingField.CREATED_AT,
        sorting_direction: SortingDirection = SortingDirection.DESC,
    ) -> PrototypeList:
        filter_ = PrototypeFilter(
            page=page,
            per_page=per_page,
            tenant_id=tenant_id,
            ids=ids,
            name=name,
            engines=engines,
            languages=languages,
            start_date=start_date,
            end_date=end_date,
            sorting_field=sorting_field,
            sorting_direction=sorting_direction,
        )
        prototypes = self._prototype_repository.find_by_filter(filter_=filter_)
        total = self._prototype_repository.get_total_count_by_filter(filter_=filter_)
        meta = {"size": len(prototypes), "total": total}

        return prototypes, meta

    def update_prototype(
        self,
        id_: str,
        tenant_id: str,
        engine: str | None = None,
        language: str | None = None,
        description: str | None = None,
    ) -> Prototype:
        if prototype := self._prototype_repository.prototype_of_id(id_=id_, tenant_id=tenant_id):
            prototype.update_info(engine=engine, language=language, description=description)
            self._prototype_repository.save(prototype)
            self._publish_events(prototype)

            return prototype

        raise PrototypeNotFound(id_)

    def find_prototype(self, id_: str, tenant_id: str) -> tuple[Prototype, list[Mapping]]:
        if prototype := self._prototype_repository.prototype_of_id(id_=id_, tenant_id=tenant_id):
            mappings = self._mapping_repository.mappings_of_prototype(prototype.id())

            return prototype, mappings

        raise PrototypeNotFound(id_)

    def delete_prototype(self, id_: str, tenant_id: str) -> None:
        if prototype := self._prototype_repository.prototype_of_id(id_=id_, tenant_id=tenant_id):
            self._check_prototypes_have_documents([id_])

            self._prototype_repository.delete(prototype)
            self._publish_events(prototype)

    def delete_prototypes(self, ids: list[str], tenant_id: str) -> None:
        if prototypes := self._prototype_repository.find_by_filter(PrototypeFilter(ids=ids, tenant_id=tenant_id)):
            self._check_prototypes_have_documents(ids)

            self._prototype_repository.delete_all(prototypes)
            for prototype in prototypes:
                self._publish_events(prototype)

    def _check_prototypes_have_documents(self, prototype_ids: list[str]) -> None:
        if prototype_ids_with_documents := self._document_proxy.get_prototype_ids_with_documents(prototype_ids):
            raise PrototypeHasDocument(
                f"Cannot delete prototypes. Reason: prototypes `{prototype_ids_with_documents}` have documents",
            )

    def _publish_events(self, prototype: Prototype) -> None:
        self._domain_event_publisher.publish(
            PROTOTYPE_AGGREGATE_TYPE,
            prototype.id(),
            prototype.events,
        )
