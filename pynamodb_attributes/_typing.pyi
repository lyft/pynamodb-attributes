from typing import overload, Any, TypeVar

import pynamodb.attributes

_A = TypeVar('_A', bound=pynamodb.attributes.Attribute)
_T = TypeVar('_T')


class Attribute(pynamodb.attributes.Attribute[_T]):
    @overload
    def __get__(self: _A, instance: None, owner: Any) -> _A: ...
    @overload
    def __get__(self, instance: Any, owner: Any) -> _T: ...
