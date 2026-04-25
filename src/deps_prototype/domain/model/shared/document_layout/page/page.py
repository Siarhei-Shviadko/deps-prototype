from dataclasses import dataclass
from typing import Any

from .key_value_pair import KeyValuePair
from .table import Table

__all__ = ["Page"]


@dataclass
class Page:
    id: str
    page_number: int
    languages: list[str]
    tables: list[Table]
    key_value_pairs: list[KeyValuePair]

    @classmethod
    def from_dict(cls, page: dict[str, Any]) -> "Page":
        page_id = page["id"]

        paragraphs_mapping: dict[str, dict[str, Any]] = {
            raw_paragraph["id"]: raw_paragraph for raw_paragraph in page["paragraphs"]
        }

        return cls(
            id=page_id,
            page_number=page["pageNumber"],
            languages=page["languages"],
            tables=[
                Table.from_dict(
                    page_id=page_id,
                    table=table,
                    paragraphs_store=paragraphs_mapping,
                )
                for table in page["tables"]
            ],
            key_value_pairs=[KeyValuePair.from_dict(kvp, page_id) for kvp in page["keyValuePairs"]],
        )
