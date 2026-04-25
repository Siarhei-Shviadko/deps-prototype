import re
from inspect import currentframe, getouterframes
from typing import Any, Iterable, Protocol, Sized, TypeVar, Union, get_args

from .attribute_name import AttributeName
from .exceptions import IllegalArgumentError

__all__ = [
    "Check",
    "NoneCheck",
    "TypeCheck",
    "ImmutableCheck",
    "FrameImmutableCheck",
    "FormatCheck",
    "RangeCheck",
    "CollectionItemFormatCheck",
    "TrimmedCollectionItemFormatCheck",
    "CollectionLengthCheck",
]

T = TypeVar("T", contravariant=True)


class Check(Protocol[T]):
    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        ...  # noqa: WPS428


class NoneCheck(Check):
    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        if value is None:
            raise IllegalArgumentError(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object should be provided.",
            )


class TypeCheck(Check):
    def __init__(self, type_: Any) -> None:
        if hasattr(type_, "__constraints__"):
            self._types = type_.__constraints__
            self._type_name = type_.__name__
        elif "typing" not in str(type_):
            self._types = (type_,)
            self._type_name = type_.__name__
        else:
            self._types = get_args(type_)
            self._type_name = str(type_)

    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        if not isinstance(value, self._types):
            raise IllegalArgumentError(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} "
                f"object should be {self._type_name}.",
            )


class ImmutableCheck(Check):
    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        if hasattr(domain_obj, attribute_name.private) and getattr(domain_obj, attribute_name.private) is not None:
            raise IllegalArgumentError(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object cannot be changed.",
            )


class FrameImmutableCheck(Check):
    def __init__(self, filename: str, function: str):
        self._filename = filename
        self._function = function

    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:  # noqa: WPS231
        if hasattr(domain_obj, attribute_name.private) and getattr(domain_obj, attribute_name.private) is not None:
            for frame_info in getouterframes(currentframe()):
                if frame_info.filename == self._filename and frame_info.function == self._function:
                    break
            else:
                raise IllegalArgumentError(
                    f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object cannot be changed.",
                )


class FormatCheck(Check):
    def __init__(self, pattern: str) -> None:
        self._pattern = pattern

    def is_correct(self, domain_obj: Any, value: str, attribute_name: AttributeName) -> None:
        if not re.fullmatch(self._pattern, value):
            raise IllegalArgumentError(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} "
                "object should not contain special symbols.",
            )


class CollectionItemFormatCheck(Check):
    def __init__(self, pattern: str) -> None:
        self._pattern = pattern

    def is_correct(self, domain_obj: Any, values: Iterable[str], attribute_name: AttributeName) -> None:
        for value in values:
            if not re.fullmatch(self._pattern, value):
                raise IllegalArgumentError(
                    f"Attribute item of {attribute_name.public} for {domain_obj.__class__.__name__} "
                    "object should not contain special symbols.",
                )


class TrimmedCollectionItemFormatCheck(CollectionItemFormatCheck):
    def is_correct(self, domain_obj: Any, values: Iterable[str], attribute_name: AttributeName) -> None:
        if isinstance(values, list):
            for i, val in enumerate(values):
                if isinstance(val, str):
                    values[i] = val.strip()

        super().is_correct(domain_obj, values, attribute_name)


class RangeCheck(Check):
    def __init__(
        self,
        min_value: Union[int, float] | None = None,
        max_value: Union[int, float] | None = None,
    ) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def is_correct(self, domain_obj: Any, value: Union[int, float], attribute_name: AttributeName) -> None:
        if self._min_value is not None and value < self._min_value:
            raise IllegalArgumentError(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} "
                f"object should be large than {self._min_value}.",
            )
        if self._max_value is not None and value > self._max_value:
            raise IllegalArgumentError(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} "
                f"object should be smaller than {self._max_value}.",
            )


class CollectionLengthCheck(Check):
    def __init__(self, min_length: int | None = None, max_length: int | None = None) -> None:
        self._min_length = min_length
        self._max_length = max_length

    def is_correct(self, domain_obj: Any, value: Sized, attribute_name: AttributeName) -> None:
        length = len(value)
        if self._min_length is not None and length < self._min_length:
            raise IllegalArgumentError(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} "
                f"object should have at least {self._min_length} items.",
            )
        if self._max_length is not None and length > self._max_length:
            raise IllegalArgumentError(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} "
                f"object should have at most {self._max_length} items.",
            )
