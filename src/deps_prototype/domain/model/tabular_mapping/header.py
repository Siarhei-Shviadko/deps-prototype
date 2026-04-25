from typing import Any

from deps_prototype.domain.model import CollectionLengthCheck, Guard, ImmutableCheck

__all__ = ["Header"]


class Header:
    name = Guard[str](str, ImmutableCheck())
    aliases = Guard[set[str]](set, CollectionLengthCheck(min_length=1))

    def __init__(
        self,
        name: str,
        aliases: set[str],
    ) -> None:
        self.name = name
        self.aliases = aliases

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.name == other.name and self.aliases == other.aliases

    def __repr__(self) -> str:
        return f"<class '{self.__class__.__name__}': {self.name = }"

    def dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "aliases": list(self.aliases),
        }
