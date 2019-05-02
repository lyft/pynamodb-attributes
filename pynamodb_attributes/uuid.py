from typing import TYPE_CHECKING, Any
from uuid import UUID

import pynamodb.constants
from pynamodb.attributes import Attribute


class UUIDAttribute(Attribute):
    """
    PynamoDB attribute to for UUIDs. These are backed by DynamoDB unicode (`S`) types.
    """

    attr_type = pynamodb.constants.STRING

    def __init__(self, remove_dashes: bool = False, **kwargs: Any) -> None:
        """
        Initializes a UUIDAttribute object.

        :param remove_dashes: will remove the dashes in the string
                              representation if True. Defaults to False.
        :param kwargs: Extra kwargs passed to base Attribute object.
        """
        super().__init__(**kwargs)
        self._remove_dashes = remove_dashes

    def serialize(self, value: UUID) -> str:
        result = str(value)

        if self._remove_dashes:
            result = result.replace('-', '')

        return result

    def deserialize(self, value: str) -> UUID:
        return UUID(value)

    if TYPE_CHECKING:
        def __get__(self, instance: Any, owner: Any) -> UUID:
            ...
