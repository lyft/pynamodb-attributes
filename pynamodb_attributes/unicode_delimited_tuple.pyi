from typing import Any
from typing import Type
from typing import TypeVar

from ._typing import Attribute

_T = TypeVar('_T', bound=tuple)


class UnicodeDelimitedTupleAttribute(Attribute[_T]):
    def __init__(self, tuple_type: Type[_T], delimiter: str = ..., **kwargs: Any) -> None:
        ...
