from pynamodb.constants import NUMBER

from pynamodb_attributes.enum import EnumAttribute


class IntegerEnum(EnumAttribute):

    attr_type = NUMBER
