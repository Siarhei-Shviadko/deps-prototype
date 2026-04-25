from copy import deepcopy

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_prototype.domain.model import (
    IReferenceLayoutRepository,
    LayoutState,
    ParsingFeature,
    Prototype,
    ReferenceLayout,
)
from deps_prototype.messaging.commands import (
    PerformParsing,
    PerformParsingReply,
    PerformUnification,
    PerformUnificationReply,
)
from deps_prototype.messaging.error_type import ErrorType
from deps_prototype.messaging.sagas import ReferenceLayoutProcessingSaga
from deps_prototype.messaging.sagas_data import (
    Destination,
    ReferenceLayoutProcessingSagaData,
    ReferenceLayoutProcessingSteps,
)


@pytest.mark.no_doc_type_processing
def test_reference_layout_processing__success(
    prototype: Prototype,
    tenant_id: str,
    reference_layout: ReferenceLayout,
    fake_reference_layout_repository: IReferenceLayoutRepository,
    reference_layout_processing_steps: ReferenceLayoutProcessingSteps,
):
    reference_layout_to_process = deepcopy(reference_layout)
    fake_reference_layout_repository.save(reference_layout_to_process)

    sd = ReferenceLayoutProcessingSagaData(
        id_=reference_layout_to_process.id(),
        prototype_id=prototype.id(),
        engine=prototype.engine,
        language=prototype.language,
        tenant_id=tenant_id,
        files=[reference_layout_to_process.blob_name],
        parsing_features={ParsingFeature.IMAGES},
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            ReferenceLayoutProcessingSaga(steps=reference_layout_processing_steps),
            sd,
        )
        .expect()
        .command(
            PerformUnification(
                document_id=sd.reference_layout_id,
                document_type_id=sd.prototype_id,
                files=sd.files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=sd.tenant_id,
                document_id=sd.reference_layout_id,
                files=sd.files,
                engine=sd.engine,
                features=list(sd.parsing_features) if sd.parsing_features else None,
                language=sd.language,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert LayoutState.READY == LayoutState(saga_data["state"])


@pytest.mark.no_doc_type_processing
def test_reference_layout_processing_unification_failed(
    prototype: Prototype,
    tenant_id: str,
    reference_layout: ReferenceLayout,
    fake_reference_layout_repository: IReferenceLayoutRepository,
    reference_layout_processing_steps: ReferenceLayoutProcessingSteps,
):
    reference_layout_to_process = deepcopy(reference_layout)
    fake_reference_layout_repository.save(reference_layout_to_process)

    sd = ReferenceLayoutProcessingSagaData(
        id_=reference_layout_to_process.id(),
        prototype_id=prototype.id(),
        engine=prototype.engine,
        language=prototype.language,
        tenant_id=tenant_id,
        files=[reference_layout_to_process.blob_name],
        parsing_features={ParsingFeature.IMAGES},
    )
    error_message = "Unification service on vacation."

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            ReferenceLayoutProcessingSaga(steps=reference_layout_processing_steps),
            sd,
        )
        .expect()
        .command(
            PerformUnification(
                document_id=sd.reference_layout_id,
                document_type_id=sd.prototype_id,
                files=sd.files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply(PerformUnificationReply(ErrorType.SYSTEM.value, error_message))
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert LayoutState.FAILED == LayoutState(saga_data["state"])


@pytest.mark.no_doc_type_processing
def test_reference_layout_processing_parsing_failed(
    prototype: Prototype,
    tenant_id: str,
    reference_layout: ReferenceLayout,
    fake_reference_layout_repository: IReferenceLayoutRepository,
    reference_layout_processing_steps: ReferenceLayoutProcessingSteps,
):
    reference_layout_to_process = deepcopy(reference_layout)
    fake_reference_layout_repository.save(reference_layout_to_process)

    sd = ReferenceLayoutProcessingSagaData(
        id_=reference_layout_to_process.id(),
        prototype_id=prototype.id(),
        engine=prototype.engine,
        language=prototype.language,
        tenant_id=tenant_id,
        files=[reference_layout_to_process.blob_name],
        parsing_features={ParsingFeature.IMAGES},
    )
    error_message = "Parsing business error"

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            ReferenceLayoutProcessingSaga(steps=reference_layout_processing_steps),
            sd,
        )
        .expect()
        .command(
            PerformUnification(
                document_id=sd.reference_layout_id,
                document_type_id=sd.prototype_id,
                files=sd.files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=sd.tenant_id,
                document_id=sd.reference_layout_id,
                files=sd.files,
                engine=sd.engine,
                features=list(sd.parsing_features) if sd.parsing_features else None,
                language=sd.language,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply(ErrorType.BUSINESS.value, error_message))
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert LayoutState.FAILED == LayoutState(saga_data["state"])
