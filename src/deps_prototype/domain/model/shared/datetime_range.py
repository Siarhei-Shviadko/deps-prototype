from dataclasses import dataclass
from datetime import datetime

__all__ = ["DatetimeRange"]


@dataclass
class DatetimeRange:
    start: datetime | None = None
    end: datetime | None = None
