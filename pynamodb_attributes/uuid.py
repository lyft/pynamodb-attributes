from typing import Any
from uuid import UUID

import pynamodb.constants
from pynamodb.attributes import Attribute


class UUIDAttribute(Attribute[UUID]):
    """
    PynamoDB attribute to for UUIDs. These are backed by DynamoDB unicode (`S`) types.
    """

    attr_type = pynamodb.constants.STRING

    def __init__(self, remove_dashes: bool = False, **kwargs: Any) -> None:
        """
        Initializes a UUIDAttribute object.

        :param remove_dashes: if set, the string serialization will be without dashes.
                              Defaults to False.
        """
        super().__init__(**kwargs)
        self._remove_dashes = remove_dashes

    def serialize(self, value: UUID) -> str:
        result = str(value)

        if self._remove_dashes:
            result = result.replace("-", "")

        return result

    def deserialize(self, value: str) -> UUID:
        return UUID(value)
