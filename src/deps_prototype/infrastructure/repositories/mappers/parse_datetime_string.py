import re
from datetime import datetime

__all__ = ["parse_datetime_string"]


def parse_datetime_string(datetime_string: str) -> datetime:
    # In python 3.9 only 6 digit microsecond value is a valid iso format string

    try:
        return datetime.fromisoformat(datetime_string)
    except ValueError:
        if "." in datetime_string:
            main_part, fractional_part = datetime_string.split(".", 1)

            if "+" in fractional_part or "-" in fractional_part:
                microseconds, sign, timezone = re.split(r"([+\-])", fractional_part)
                timezone = sign + timezone
            else:
                microseconds, timezone = fractional_part, ""

            datetime_string = f"{main_part}.{microseconds.ljust(6, '0')[:6]}{timezone}"

        return datetime.fromisoformat(datetime_string)
