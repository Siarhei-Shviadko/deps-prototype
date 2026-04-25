from dataclasses import dataclass
from typing import Any

from .polygon import Polygon

__all__ = ["KeyValuePairElement", "KeyValuePair"]


@dataclass
class KeyValuePairElement:
    content: str
    polygon: Polygon

    @classmethod
    def from_dict(cls, element: dict[str, Any]) -> "KeyValuePairElement":
        content = element["content"].strip()

        return cls(content=content, polygon=Polygon.from_dict(element["polygon"]))


@dataclass
class KeyValuePair:
    page_id: str
    key: KeyValuePairElement
    confidence: float
    value: KeyValuePairElement | None = None

    @property
    def key_content(self) -> str:
        return self.key.content

    @property
    def value_content(self) -> str | None:
        return self.value.content if self.value else None

    @property
    def value_polygon(self) -> Polygon | None:
        return self.value.polygon if self.value else None

    @classmethod
    def from_dict(cls, key_value_pair: dict[str, Any], page_id: str) -> "KeyValuePair":
        value = KeyValuePairElement.from_dict(key_value_pair["value"]) if key_value_pair.get("value") else None

        return cls(
            page_id=page_id,
            key=KeyValuePairElement.from_dict(key_value_pair["key"]),
            value=value,
            confidence=key_value_pair["confidence"],
        )
