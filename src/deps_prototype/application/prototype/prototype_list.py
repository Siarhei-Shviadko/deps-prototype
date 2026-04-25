from deps_prototype.domain.model import Prototype

__all__ = ["PrototypeList"]

PrototypeList = tuple[list[Prototype], dict[str, int]]
