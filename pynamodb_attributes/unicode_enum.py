from enum import Enum
from typing import Any
from typing import Generic
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar

import pynamodb.constants
from pynamodb.attributes import Attribute

T = TypeVar('T', bound=Enum)


class UnicodeEnumAttribute(Attribute, Generic[T]):
    """
    Stores string enumerations (Enums whose values are strings) as DynamoDB strings.

    >>> from enum import Enum
    >>>
    >>> from pynamodb.models import Model
    >>>
    >>> class ShakeFlavor(Enum):
    >>>   VANILLA = 'vanilla'
    >>>   CHOCOLATE = 'chocolate'
    >>>   COOKIES = 'cookies'
    >>>   MINT = 'mint'
    >>>
    >>> class Shake(Model):
    >>>   flavor = UnicodeEnumAttribute(ShakeFlavor)
    """
    attr_type = pynamodb.constants.STRING

    def __init__(self, enum_type: Type[T], **kwargs: Any) -> None:
        """
        :param enum_type: The type of the enum
        """
        super().__init__(**kwargs)
        self.enum_type = enum_type
        if not all(isinstance(e.value, str) for e in self.enum_type):
            raise TypeError(f"Enumeration '{self.enum_type}' values must be all strings")

    def deserialize(self, value: str) -> T:
        return self.enum_type(super().deserialize(value))

    def serialize(self, value: T) -> str:
        if not isinstance(value, self.enum_type):
            raise TypeError(f"value has invalid type '{type(value)}'; expected '{self.enum_type}'")
        return value.value

    if TYPE_CHECKING:
        def __get__(self, instance: Any, owner: Any) -> T:
            ...
