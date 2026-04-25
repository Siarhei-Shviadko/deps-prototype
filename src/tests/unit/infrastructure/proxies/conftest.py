from http import HTTPStatus
from urllib import parse
from uuid import uuid4

import pytest

from deps_prototype.domain.model import ParsingFeature


@pytest.fixture
def parsing_type():
    return uuid4().hex


@pytest.fixture
def extraction_proxy_config(config):
    return config.extraction


@pytest.fixture
def parsing_proxy_config(config):
    return config.parsing


@pytest.fixture
def document_proxy_config(config):
    return config.document


@pytest.fixture
def parsing_requests_ok_mock(
    parsing_proxy_config,
    document_layout_dict,
    requests_mock,
    parsing_type,
    document_id,
    language,
):
    base_url = parsing_proxy_config.url()
    params = {
        "features": [ParsingFeature.TABLES.value, ParsingFeature.KEY_VALUE_PAIRS.value],
        "parsingType": parsing_type,
        "language": language,
    }
    url = f"{base_url}/api/parsing/v1/document-layout/{document_id}?{parse.urlencode(params, doseq=True)}"

    requests_mock.register_uri("GET", url, status_code=HTTPStatus.OK, json=document_layout_dict)

    yield requests_mock


@pytest.fixture
def parsing_requests_error_mock(requests_mock, parsing_proxy_config, document_id, parsing_type, language):
    base_url = parsing_proxy_config.url()
    params = {
        "features": [ParsingFeature.TABLES.value, ParsingFeature.KEY_VALUE_PAIRS.value],
        "parsingType": parsing_type,
        "language": language,
    }
    url = f"{base_url}/api/parsing/v1/document-layout/{document_id}?{parse.urlencode(params, doseq=True)}"

    requests_mock.register_uri("GET", url, status_code=HTTPStatus.BAD_REQUEST)

    yield requests_mock


@pytest.fixture
def get_prototype_ids_with_documents_ok_mock(document_proxy_config, requests_mock, prototype_id):
    base_url = document_proxy_config.url()
    query = "&".join((f'types=["{prototype_id}"]',))
    url = f"{base_url}/api/document/v1/documents?{query}"

    requests_mock.register_uri("GET", url, status_code=HTTPStatus.OK, json={"result": [{"documentType": prototype_id}]})

    yield requests_mock


@pytest.fixture
def get_prototype_ids_with_documents_error_mock(document_proxy_config, requests_mock, prototype_id):
    base_url = document_proxy_config.url()
    query = "&".join((f'types=["{prototype_id}"]',))
    url = f"{base_url}/api/document/v1/documents?{query}"

    requests_mock.register_uri("GET", url, status_code=HTTPStatus.BAD_REQUEST)

    yield requests_mock
