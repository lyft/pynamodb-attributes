from enum import Enum
from typing import Any
from typing import Optional
from typing import Type
from typing import TypeVar

from ._typing import Attribute

_T = TypeVar('_T', bound=Enum)


class UnicodeEnumAttribute(Attribute[_T]):
    def __init__(self, enum_type: Type[_T], unknown_value: Optional[_T] = ..., **kwargs: Any) -> None:
        ...
