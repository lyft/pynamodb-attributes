from pynamodb.attributes import NumberAttribute

from ._typing import Attribute


class IntegerAttribute(Attribute):
    """
    Unlike NumberAttribute, this attribute has its type hinted as 'int'.
    """
    attr_type = NumberAttribute.attr_type
    serialize = NumberAttribute.serialize
    deserialize = NumberAttribute.deserialize
