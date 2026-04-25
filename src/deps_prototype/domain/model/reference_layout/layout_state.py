from enum import Enum

__all__ = ["LayoutState"]


class LayoutState(str, Enum):
    NEW = "New"
    UNIFICATION = "Unification"
    PARSING = "Parsing"
    READY = "Ready"
    FAILED = "Failed"
