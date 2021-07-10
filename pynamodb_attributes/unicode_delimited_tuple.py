from typing import Any
from typing import get_type_hints
from typing import List
from typing import Tuple
from typing import Type
from typing import TypeVar

import pynamodb.constants
from pynamodb.attributes import Attribute

T = TypeVar("T", bound=Tuple[Any, ...])
_DEFAULT_FIELD_DELIMITER = "::"


class UnicodeDelimitedTupleAttribute(Attribute[T]):
    """
    Stores a tuple of strings as a string. The tuple's members will be joined with a delimiter.

    >>> from typing import NamedTuple
    >>>
    >>> from pynamodb.models import Model
    >>>
    >>> class LatLng(NamedTuple):
    >>>   lat: int
    >>>   lng: int
    >>>
    >>> class Employee(Model):
    >>>   location = UnicodeDelimitedTupleAttribute(LatLng)
    """

    attr_type = pynamodb.constants.STRING

    def __init__(
        self,
        tuple_type: Type[T],
        delimiter: str = _DEFAULT_FIELD_DELIMITER,
        **kwargs: Any,
    ) -> None:
        """
        :param tuple_type: The type of the tuple -- may be a named or plain tuple
        :param delimiter: The delimiter to separate the tuple elements
        """
        super().__init__(**kwargs)
        self.tuple_type: Type[T] = tuple_type
        self.delimiter = delimiter

    def deserialize(self, value: str) -> T:
        field_types = get_type_hints(self.tuple_type)

        if field_types:
            values = value.split(self.delimiter, maxsplit=len(field_types))
            return self.tuple_type(
                **{
                    field_name: self._parse_value(value, field_type)
                    for (field_name, field_type), value in zip(
                        field_types.items(),
                        values,
                    )
                }
            )
        else:
            return self.tuple_type(value.split(self.delimiter))

    def serialize(self, value: T) -> str:
        if not isinstance(value, self.tuple_type):
            raise TypeError(
                f"value has invalid type '{type(value)}'; expected '{self.tuple_type}'",
            )
        values: List[T] = list(value)
        while values and values[-1] is None:
            del values[-1]
        strings = [str(e) for e in values]
        if any(self.delimiter in s for s in strings):
            raise ValueError(
                f"Tuple elements may not contain delimiter '{self.delimiter}'",
            )
        return self.delimiter.join(strings)

    def _parse_value(self, str_value: str, type_: Type[Any]) -> Any:
        if hasattr(type_, "__args__"):
            for t in type_.__args__:
                if isinstance(None, t):
                    continue
                try:
                    return t(str_value)
                except ValueError:
                    pass
            list_of_types = ", ".join(t.__name__ for t in type_.__args__)
            raise ValueError(
                f"Unable to parse value: '{str_value}' for any of the "
                f"following types: '[{list_of_types}]'",
            )
        else:
            return type_(str_value)
