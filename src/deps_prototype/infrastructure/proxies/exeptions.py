from deps_prototype.domain.exceptions import RestClientError

__all__ = [
    "ExtractionProxyRequestError",
    "UnifierProxyRequestError",
    "ParsingProxyRequestError",
    "DocumentProxyRequestError",
]


class ExtractionProxyRequestError(RestClientError):
    pass


class UnifierProxyRequestError(RestClientError):
    pass


class ParsingProxyRequestError(RestClientError):
    pass


class DocumentProxyRequestError(RestClientError):
    pass
