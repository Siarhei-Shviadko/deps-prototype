from dataclasses import dataclass
from typing import Any, Generator

from .page import KeyValuePair, Page
from .parsing_feature import ParsingFeature

__all__ = ["DocumentLayout"]


@dataclass
class DocumentLayout:
    document_layout_id: str
    parsing_features: list[ParsingFeature]
    pages: list[Page]

    @property
    def key_value_pairs(self) -> Generator[KeyValuePair, Any, None]:
        return (kvp for page in self.pages for kvp in page.key_value_pairs)

    @classmethod
    def from_dict(cls, document_layout: dict[str, Any]) -> "DocumentLayout":
        return cls(
            document_layout_id=document_layout["documentLayoutId"],
            parsing_features=document_layout["parsingFeatures"],
            pages=[Page.from_dict(page) for page in document_layout["pages"]],
        )
