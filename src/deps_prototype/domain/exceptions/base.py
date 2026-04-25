__all__ = [
    "PrototypeException",
    "NotFoundError",
    "DocumentTypeAlreadyExistsException",
    "RestClientError",
    "BusinessException",
    "InvariantViolation",
]


class PrototypeException(Exception):
    code = "prototype_exception"


class BusinessException(PrototypeException):
    code = "business_exception"


class NotFoundError(BusinessException):
    code = "not_found_error"


class DocumentTypeAlreadyExistsException(BusinessException):
    code = "document_type_already_exists"


class InvariantViolation(BusinessException):
    code = "invariant_violation"


class RestClientError(PrototypeException):
    code = "rest_client_error"
