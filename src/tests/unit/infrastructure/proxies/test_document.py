import pytest

from deps_prototype.infrastructure.proxies.exeptions import DocumentProxyRequestError


@pytest.mark.prototype
def test_get_prototype_ids_with_documents__ok(document_proxy, get_prototype_ids_with_documents_ok_mock, prototype_id):
    res = document_proxy.get_prototype_ids_with_documents([prototype_id])

    assert res == [prototype_id]


@pytest.mark.prototype
def test_get_prototype_ids_with_documents__error(
    document_proxy,
    get_prototype_ids_with_documents_error_mock,
    prototype_id,
):
    with pytest.raises(DocumentProxyRequestError):
        document_proxy.get_prototype_ids_with_documents([prototype_id])
