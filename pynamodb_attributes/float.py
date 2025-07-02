from pynamodb.attributes import Attribute
from pynamodb.attributes import NumberAttribute


class FloatAttribute(Attribute[float]):
    """
    Unlike NumberAttribute, this attribute has its type hinted as 'float'.
    """

    attr_type = NumberAttribute.attr_type
    serialize = NumberAttribute.serialize  # type: ignore
    deserialize = NumberAttribute.deserialize  # type: ignore

class DoubleAttribute(FloatAttribute):
    """
    Unlike NumberAttribute, this attribute has its type hinted as 'double'.
    """
    attr_type = NumberAttribute.attr_type
    serialize = NumberAttribute.serialize
    deserialize = NumberAttribute.deserialize
    