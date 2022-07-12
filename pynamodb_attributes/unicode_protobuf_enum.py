from typing import Any
from typing import Optional
from typing import Protocol
from typing import Type
from typing import TypeVar

import pynamodb.constants
from pynamodb.attributes import Attribute

_T_co = TypeVar("_T_co", covariant=True)
_TProtobufEnum = TypeVar("_TProtobufEnum", bound="_ProtobufEnum[Any]")


# TODO: replace with built-in str.removeprefix once we're >=py3.9
def _removeprefix(self: str, prefix: str) -> str:  # pragma: no cover
    if self.startswith(prefix):
        return self[len(prefix) :]
    else:
        return self[:]


# What we expect of mypy-protobuf's enum "classes"
class _ProtobufEnum(Protocol[_T_co]):
    @classmethod
    def Name(cls, number: int) -> str:
        ...

    @classmethod
    def Value(cls: Type[_T_co], name: str) -> _T_co:
        ...


_fail: Any = object()


class UnicodeProtobufEnumAttribute(Attribute[_TProtobufEnum]):
    """
    Stores Protobuf enumeration values as DynamoDB strings.

    >>> from diner_pb2 import ShakeFlavor
    >>>
    >>> class Shake(Model):
    >>>   flavor = UnicodeProtobufEnumAttribute(ShakeFlavor, prefix='SHAKE_FLAVOR_ ')
    """

    attr_type = pynamodb.constants.STRING

    def __init__(
        self,
        enum_type: Type[_TProtobufEnum],
        *,
        unknown_value: Optional[_TProtobufEnum] = _fail,
        prefix: str,
        lower: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        :param enum_type: the type of the enumeration
        :param unknown_value: the value to return if the persisted value is unknown
        :param prefix: prefix to strip from the persisted value
        :param lower: whether to persist as lowercase
        """
        super().__init__(**kwargs)
        self.enum_type = enum_type
        self.unknown_value = unknown_value
        self.prefix = prefix
        self.lower = lower
        self._kwargs = kwargs

    # Attributes need to be copiable :|
    def __deepcopy__(self, memo: Any) -> Any:
        return self.__class__(
            self.enum_type,
            unknown_value=self.unknown_value,
            prefix=self.prefix,
            lower=self.lower,
            **self._kwargs,
        )

    def deserialize(self, value: str) -> Optional[_TProtobufEnum]:
        try:
            return self.enum_type.Value(self.prefix + value.upper())
        except ValueError:
            if self.unknown_value is _fail:
                raise
            return self.unknown_value

    def serialize(self, value: _TProtobufEnum) -> str:
        if not isinstance(value, int):
            raise TypeError(
                f"value has invalid type '{type(value)}'; expected an integer",
            )
        name = self.enum_type.Name(value)
        name = _removeprefix(name, self.prefix)
        if self.lower:
            name = name.lower()
        return name
