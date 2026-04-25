from deps_prototype.domain.exceptions import BusinessException

__all__ = ["IllegalArgumentError"]


class IllegalArgumentError(BusinessException):
    code = "illegal_argument"
