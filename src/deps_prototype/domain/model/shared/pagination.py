from dataclasses import dataclass

__all__ = ["Pagination"]


DEFAULT_PAGE_NUMBER = 1
DEFAULT_PER_PAGE_NUMBER = 10


@dataclass
class Pagination:
    page: int = DEFAULT_PAGE_NUMBER
    per_page: int = DEFAULT_PER_PAGE_NUMBER
