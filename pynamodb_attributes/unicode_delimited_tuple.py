from typing import Any
from typing import Tuple
from typing import Type
from typing import TypeVar

import pynamodb.constants

from ._typing import Attribute

T = TypeVar('T', bound=tuple)
_DEFAULT_FIELD_DELIMITER = '::'


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

    def __init__(self, tuple_type: Type[T], delimiter: str = _DEFAULT_FIELD_DELIMITER, **kwargs: Any) -> None:
        """
        :param tuple_type: The type of the tuple -- may be a named or plain tuple
        :param delimiter: The delimiter to separate the tuple elements
        """
        super().__init__(**kwargs)
        self.tuple_type: Type[Tuple] = tuple_type
        self.delimiter = delimiter

    def deserialize(self, value: str) -> T:
        fields = getattr(self.tuple_type, '_fields', None)
        field_types = getattr(self.tuple_type, '_field_types', None)
        if fields and field_types:
            values = value.split(self.delimiter, maxsplit=len(fields))
        tuple_vals = {}
        for f, v in zip(fields, values):
            if field_types[f].__module__ == 'builtins':
                tuple_vals[f] = field_types[f](v)
            elif field_types[f].__module__ == 'typing' and field_types[f].__origin__ == typing.Union:
                for arg_type in field_types[f].__args__:
                    try:
                        tuple_vals[f] = arg_type(v)
                        break
                    except Exception:
                        continue

            return self.tuple_type(**tuple_vals)  # type: ignore
        else:
            return self.tuple_type(value.split(self.delimiter))  # type: ignore

    def serialize(self, value: T) -> str:
        if not isinstance(value, self.tuple_type):
            raise TypeError(f"value has invalid type '{type(value)}'; expected '{self.tuple_type}'")
        values = list(value)
        while values and values[-1] is None:
            del values[-1]
        strings = [str(e) for e in values]
        if any(self.delimiter in s for s in strings):
            raise ValueError(f"Tuple elements may not contain delimiter '{self.delimiter}'")
        return self.delimiter.join(strings)
