from pynamodb.attributes import Attribute
from pynamodb.attributes import NumberAttribute


class FloatAttribute(Attribute):
    """
    Unlike NumberAttribute, this attribute has its type hinted as 'float'.
    """
    attr_type = NumberAttribute.attr_type
    serialize = NumberAttribute.serialize
    deserialize = NumberAttribute.deserialize
