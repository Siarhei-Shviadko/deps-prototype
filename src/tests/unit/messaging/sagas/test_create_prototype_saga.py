from unittest import mock

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_prototype.messaging.sagas import PrototypeCreationSaga
from deps_prototype.messaging.sagas_data import PrototypeCreationSagaData


@pytest.mark.prototype_creation_saga
def test_prototype_creation_saga(
    prototype_id,
    tenant_id,
    language,
    name,
    engine,
    description,
    prototype_creation_steps,
):
    prototype_saga_data = PrototypeCreationSagaData(
        name=name,
        language=language,
        engine=engine,
        tenant_id=tenant_id,
        description=description,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            PrototypeCreationSaga(steps=prototype_creation_steps),
            prototype_saga_data,
        )
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert saga_data["tenant_id"] == tenant_id
    assert saga_data["language"] == language
    assert saga_data["engine"] == engine
    assert saga_data["description"] == description


@pytest.mark.prototype_creation_saga
def test_prototype_creation_saga_failed(
    prototype_id,
    tenant_id,
    language,
    name,
    engine,
    description,
    prototype_creation_steps,
    fake_document_type_service,
):
    prototype_saga_data = PrototypeCreationSagaData(
        name=name,
        language=language,
        engine=engine,
        tenant_id=tenant_id,
        description=description,
    )
    prototype_creation_steps.create_prototype = mock.Mock(side_effect=RuntimeError())
    fake_document_type_service.delete_document_type = mock.Mock()

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            PrototypeCreationSaga(steps=prototype_creation_steps),
            prototype_saga_data,
        )
        .expect_rolled_back()
    )

    fake_document_type_service.delete_document_type.assert_called_once_with(suts.saga_data["entity_id"])
