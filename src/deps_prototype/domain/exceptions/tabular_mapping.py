from .base import NotFoundError

__all__ = ["TabularMappingNotFound"]


class TabularMappingNotFound(NotFoundError):
    code = "tabular_mapping_not_found"

    def __init__(self, tabular_mapping_code: str) -> None:
        super().__init__(f"Tabular mapping with code: `{tabular_mapping_code}` not found")
