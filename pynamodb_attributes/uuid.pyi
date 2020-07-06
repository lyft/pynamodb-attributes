from typing import Any
from uuid import UUID

from ._typing import Attribute


class UUIDAttribute(Attribute[UUID]):
    def __init__(self, remove_dashes: bool = ..., **kwargs: Any) -> None:
        ...
