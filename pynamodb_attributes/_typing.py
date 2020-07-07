from typing import Any
from typing import Generic
from typing import overload
from typing import TYPE_CHECKING
from typing import TypeVar

import pynamodb.attributes

_T = TypeVar('_T')

# TODO: derive from pynamodb.attributes.Attribute directly when pynamodb>=5
if TYPE_CHECKING:
    _A = TypeVar('_A', bound=pynamodb.attributes.Attribute)

    class Attribute(Generic[_T], pynamodb.attributes.Attribute[_T]):
        @overload
        def __get__(self: _A, instance: None, owner: Any) -> _A:
            ...

        @overload
        def __get__(self, instance: Any, owner: Any) -> _T:
            ...

        def __get__(self, instance: Any, owner: Any) -> Any:
            ...
else:
    class Attribute(Generic[_T], pynamodb.attributes.Attribute):
        pass
