from typing import Set

from pynamodb.attributes import Attribute
from pynamodb.attributes import NumberSetAttribute


class IntegerSetAttribute(Attribute[Set[int]]):
    """
    Unlike NumberSetAttribute, this attribute has its type hinted as 'Set[int]'.
    """

    attr_type = NumberSetAttribute.attr_type
    null = NumberSetAttribute.null
    serialize = NumberSetAttribute.serialize  # type: ignore
    deserialize = NumberSetAttribute.deserialize  # type: ignore
