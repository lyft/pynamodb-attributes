from enum import Enum
from typing import Any
from typing import Generic
from typing import Optional
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar

import pynamodb.constants
from pynamodb.attributes import Attribute

T = TypeVar('T', bound=Enum)
_fail: Any = object()


class IntegerEnumAttribute(Attribute, Generic[T]):
    """
    Stores integer enumerations (Enums whose values are integers) as DynamoDB numbers.

    >>> from enum import Enum
    >>>
    >>> from pynamodb.models import Model
    >>>
    >>> class ShakeFlavor(Enum):
    >>>   VANILLA = 1
    >>>   CHOCOLATE = 2
    >>>   COOKIES = 3
    >>>   MINT = 4
    >>>
    >>> class Shake(Model):
    >>>   flavor = IntegerEnumAttribute(ShakeFlavor)
    """
    attr_type = pynamodb.constants.NUMBER

    def __init__(self, enum_type: Type[T], unknown_value: Optional[T] = _fail, **kwargs: Any) -> None:
        """
        :param enum_type: The type of the enum
        """
        super().__init__(**kwargs)
        self.enum_type = enum_type
        self.unknown_value = unknown_value
        if not all(isinstance(e.value, int) for e in self.enum_type):
            raise TypeError(f"Enumeration '{self.enum_type}' values must be all ints")

    def deserialize(self, value: str) -> Optional[T]:
        try:
            return self.enum_type(int(value))
        except ValueError:
            if self.unknown_value is _fail:
                raise
            return self.unknown_value

    def serialize(self, value: T) -> str:
        if not isinstance(value, self.enum_type):
            raise TypeError(f"value has invalid type '{type(value)}'; expected '{self.enum_type}'")
        return str(value.value)

    if TYPE_CHECKING:
        def __get__(self, instance: Any, owner: Any) -> T:
            ...
