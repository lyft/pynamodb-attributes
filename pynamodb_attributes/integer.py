from pynamodb.attributes import Attribute
from pynamodb.attributes import NumberAttribute


class IntegerAttribute(Attribute[int]):
    """
    Unlike NumberAttribute, this attribute has its type hinted as 'int'.
    """

    attr_type = NumberAttribute.attr_type
    serialize = NumberAttribute.serialize  # type: ignore
    deserialize = NumberAttribute.deserialize  # type: ignore

class LongIntegerAttribute(IntegerAttribute):
    """
    Unlike NumberAttribute, this attribute has its type hinted as 'long'.
    """

    attr_type = NumberAttribute.attr_type
    serialize = NumberAttribute.serialize
    deserialize = NumberAttribute.deserialize

class UnsignedIntegerAttribute(IntegerAttribute):
    """
    Unlike NumberAttribute, this attribute has its type hinted as 'unsigned'.
    """

    attr_type = NumberAttribute.attr_type
    serialize = NumberAttribute.serialize
    deserialize = NumberAttribute.deserialize

class UnsignedLongIntegerAttribute(IntegerAttribute):
    """
    Unlike NumberAttribute, this attribute has its type hinted as 'unsigned long'.
    """

    attr_type = NumberAttribute.attr_type
    serialize = NumberAttribute.serialize
    deserialize = NumberAttribute.deserialize
