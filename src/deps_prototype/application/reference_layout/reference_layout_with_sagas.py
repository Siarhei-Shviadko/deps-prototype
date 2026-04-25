import logging
from pathlib import Path
from typing import TYPE_CHECKING

from deps_message_flow.sagas.orchestration import Saga, SagaInstanceFactory

from deps_prototype.domain.exceptions import (
    PrototypeNotFound,
    ReferenceLayoutCreationFailed,
    ReferenceLayoutNotFound,
)
from deps_prototype.domain.model import (
    CanRestartSpecification,
    IPrototypeRepository,
    IReferenceLayoutRepository,
    LayoutState,
    ParsingFeature,
    Prototype,
    ReferenceLayout,
)
from deps_prototype.messaging.sagas import ReferenceLayoutProcessingSaga
from deps_prototype.messaging.sagas_data import ReferenceLayoutProcessingSagaData

if TYPE_CHECKING:
    from deps_prototype.infrastructure import FileStorageProxy

__all__ = ["ReferenceLayoutServiceWithSagas"]


class ReferenceLayoutServiceWithSagas:
    PARSING_FEATURES = {ParsingFeature.KEY_VALUE_PAIRS, ParsingFeature.TABLES}

    def __init__(
        self,
        reference_layout_repository: IReferenceLayoutRepository,
        prototype_repository: IPrototypeRepository,
        file_storage_proxy: "FileStorageProxy",
        saga_instance_factory: SagaInstanceFactory,
        sagas: list[Saga],
    ) -> None:
        self._reference_layout_repository = reference_layout_repository
        self._prototype_repository = prototype_repository
        self._file_storage_proxy = file_storage_proxy
        self._sagas = {saga.__class__: saga for saga in sagas}
        self._saga_instance_factory = saga_instance_factory
        self._logger = logging.getLogger(self.__class__.__name__)

    def create_layout(
        self,
        prototype_id: str,
        tenant_id: str,
        file_name: str,
        file: bytes,
    ) -> str:
        prototype = self.find_prototype(prototype_id=prototype_id, tenant_id=tenant_id)
        blob_name = self._file_storage_proxy.upload_content(file_path=file_name, content=file)
        reference_layout = self.save_layout(prototype=prototype, blob_name=blob_name, title=Path(file_name).stem)

        self._start_reference_layout_saga(
            id_=reference_layout.id(),
            prototype_id=prototype.id(),
            engine=prototype.engine,
            language=prototype.language,
            tenant_id=tenant_id,
            files=[reference_layout.blob_name],
        )

        return reference_layout.id()

    def restart_layout_processing(self, layout_id: str, prototype_id: str, tenant_id: str) -> None:
        prototype, reference_layout = self._get_prototype_and_reference_layout(
            prototype_id=prototype_id,
            layout_id=layout_id,
            tenant_id=tenant_id,
        )

        CanRestartSpecification(reference_layout).check()

        self._start_reference_layout_saga(
            id_=layout_id,
            prototype_id=prototype_id,
            tenant_id=tenant_id,
            engine=prototype.engine,
            language=prototype.language,
            files=[reference_layout.blob_name],
        )

    def find_prototype(self, prototype_id: str, tenant_id: str) -> Prototype:
        prototype = self._prototype_repository.prototype_of_id(id_=prototype_id, tenant_id=tenant_id)

        if prototype is None:
            raise PrototypeNotFound(prototype_id)

        return prototype

    def find_reference_layout(self, id_: str, prototype_id: str) -> ReferenceLayout:
        if layout := self._reference_layout_repository.reference_layout_of_id(id_=id_, prototype_id=prototype_id):
            return layout

        raise ReferenceLayoutNotFound(id_)

    def save_layout(self, prototype: Prototype, blob_name: str, title: str) -> ReferenceLayout | None:
        try:
            reference_layout = prototype.add_reference_layout(
                blob_name=blob_name,
                state=LayoutState.NEW,
                title=title,
            )
            self._reference_layout_repository.save(reference_layout)
            return reference_layout
        except Exception:
            self._file_storage_proxy.delete_file(blob_name)

            raise ReferenceLayoutCreationFailed()

    def _start_reference_layout_saga(
        self,
        id_: str,
        prototype_id: str,
        tenant_id: str,
        engine: str,
        language: str,
        files: list[str],
    ) -> None:
        reference_layout_saga_data = ReferenceLayoutProcessingSagaData(
            id_=id_,
            prototype_id=prototype_id,
            tenant_id=tenant_id,
            engine=engine,
            language=language,
            files=files,
            parsing_features=self.PARSING_FEATURES,
        )

        si = self._saga_instance_factory.create(
            self._sagas[ReferenceLayoutProcessingSaga],
            reference_layout_saga_data,
        )

        self._logger.info("Saga %s for reference_layout is created", si.saga_id)

    def _get_prototype_and_reference_layout(
        self,
        prototype_id: str,
        layout_id: str,
        tenant_id: str,
    ) -> tuple[Prototype, ReferenceLayout]:
        return self.find_prototype(prototype_id=prototype_id, tenant_id=tenant_id), self.find_reference_layout(
            id_=layout_id,
            prototype_id=prototype_id,
        )
