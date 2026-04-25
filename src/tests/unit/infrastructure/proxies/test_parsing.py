import pytest

from deps_prototype.domain.model import DocumentLayout, ParsingFeature
from deps_prototype.infrastructure import ParsingProxyRequestError


def test_get_document_layout__ok(parsing_requests_ok_mock, parsing_proxy, parsing_type, document_id, language):
    res = parsing_proxy.get_document_layout(
        document_id=document_id,
        parsing_type=parsing_type,
        language=language,
        parsing_features=(
            ParsingFeature.TABLES,
            ParsingFeature.KEY_VALUE_PAIRS,
        ),
    )

    assert isinstance(res, DocumentLayout)


def test_get_document_layout__error(parsing_proxy, parsing_requests_error_mock, document_id, parsing_type, language):
    with pytest.raises(ParsingProxyRequestError):
        parsing_proxy.get_document_layout(
            document_id=document_id,
            parsing_type=parsing_type,
            language=language,
            parsing_features=(
                ParsingFeature.TABLES,
                ParsingFeature.KEY_VALUE_PAIRS,
            ),
        )
