import logging

from deps_message_flow.events.publisher import DomainEventPublisher

from deps_prototype.application import IDocumentTypeProxy, IExtractionProxy
from deps_prototype.constants import PROTOTYPE_AGGREGATE_TYPE
from deps_prototype.domain.exceptions import PrototypeException
from deps_prototype.domain.model import IPrototypeRepository, PrototypeFactory

from .prototype_creation_data import PrototypeCreationSagaData

__all__ = ["PrototypeCreationSteps"]


class PrototypeCreationSteps:
    PROTOTYPE_EXTRACTOR_TYPE: str = "prototype"

    def __init__(
        self,
        document_type_service: IDocumentTypeProxy,
        extraction_service: IExtractionProxy,
        prototype_repository: IPrototypeRepository,
        domain_event_publisher: DomainEventPublisher,
    ):
        self._document_type_service = document_type_service
        self._extraction_service = extraction_service
        self._prototype_repository = prototype_repository
        self._domain_event_publisher = domain_event_publisher
        self._logger = logging.getLogger(self.__class__.__name__)

    def create_document_type(self, data: PrototypeCreationSagaData) -> None:
        try:
            document_type_id = self._extraction_service.create_document_type(
                name=data.name,
                language=data.language,
                engine=data.engine,
                description=data.description,
                extractor_type=self.PROTOTYPE_EXTRACTOR_TYPE,
            )
        except PrototypeException as exc:
            self._logger.error(f"Document type creation error. {str(exc)}", exc_info=True)
            raise
        except Exception as exc:
            self._logger.error(f"Unhandled error. {str(exc)}", exc_info=True)
            raise RuntimeError(str(exc))
        else:
            data.prototype_id = document_type_id

    def delete_document_type(self, data: PrototypeCreationSagaData) -> None:
        self._document_type_service.delete_document_type(data.prototype_id)

    def create_prototype(self, data: PrototypeCreationSagaData) -> None:
        try:
            prototype = PrototypeFactory.make(
                id_=data.prototype_id,
                tenant_id=data.tenant_id,
                name=data.name,
                engine=data.engine,
                language=data.language,
                description=data.description,
            )
            self._prototype_repository.save(prototype)
            self._domain_event_publisher.publish(
                PROTOTYPE_AGGREGATE_TYPE,
                prototype.id(),
                prototype.events,
            )
        except Exception as exc:
            self._logger.error(f"Prototype creation error. {str(exc)}")
            raise RuntimeError(str(exc))
