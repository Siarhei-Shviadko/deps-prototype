from typing import TypedDict

__all__ = ["RawHeader"]


class RawHeader(TypedDict):
    name: str
    aliases: set[str]
