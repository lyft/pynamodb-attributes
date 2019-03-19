from pynamodb.attributes import Attribute
from pynamodb.attributes import UTCDateTimeAttribute


class DateTimeAttribute(Attribute):
    """
    Unlike UTCDateTimeAttribute, this attribute has its type hinted as 'datetime'.
    """
    attr_type = UTCDateTimeAttribute.attr_type
    serialize = UTCDateTimeAttribute.serialize
    deserialize = UTCDateTimeAttribute.deserialize
