from .base import BusinessException, NotFoundError

__all__ = ["MappingNotFound", "MappingAlreadyExists", "TabularMappingAlreadyExists"]


class MappingNotFound(NotFoundError):
    code = "mapping_not_found"

    def __init__(self, mapping_code: str) -> None:
        super().__init__(f"Mapping with code: `{mapping_code}` not found")


class MappingAlreadyExists(BusinessException):
    code = "mapping_already_exists"

    def __init__(self, mapping_code: str) -> None:
        super().__init__(f"Mapping with code: `{mapping_code}` already exists")


class TabularMappingAlreadyExists(BusinessException):
    code = "tabular_mapping_already_exists"

    def __init__(self, tabular_mapping_code: str) -> None:
        super().__init__(f"Tabular mapping with code: `{tabular_mapping_code}` already exists")
