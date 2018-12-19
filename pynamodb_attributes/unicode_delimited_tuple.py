from typing import Any
from typing import Generic
from typing import Tuple
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar

import pynamodb.constants
from pynamodb.attributes import Attribute

T = TypeVar('T', bound=tuple)
_DEFAULT_FIELD_DELIMITER = '::'


class UnicodeDelimitedTupleAttribute(Attribute, Generic[T]):
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
            return self.tuple_type(**{f: field_types[f](v) for f, v in zip(fields, values)})  # type: ignore
        else:
            return self.tuple_type(value.split(self.delimiter))  # type: ignore

    def serialize(self, value: T) -> str:
        if not isinstance(value, self.tuple_type):
            raise TypeError(f"value has invalid type '{type(value)}'; expected '{self.tuple_type}'")
        values = [e for e in value]
        while values and values[-1] is None:
            del values[-1]
        strings = [str(e) for e in values]
        if any(self.delimiter in s for s in strings):
            raise ValueError(f"Tuple elements may not contain delimiter '{self.delimiter}'")
        return self.delimiter.join(strings)

    if TYPE_CHECKING:
        def __get__(self, instance: Any, owner: Any) -> T:
            ...
