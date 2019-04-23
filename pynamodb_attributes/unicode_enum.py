import pynamodb.constants

from pynamodb_attributes.enum import EnumAttribute


class UnicodeEnumAttribute(EnumAttribute):
    """
    Stores string enumerations (Enums whose values are strings) as DynamoDB strings.

    >>> from enum import Enum
    >>>
    >>> from pynamodb.models import Model
    >>>
    >>> class ShakeFlavor(Enum):
    >>>   VANILLA = 'vanilla'
    >>>   CHOCOLATE = 'chocolate'
    >>>   COOKIES = 'cookies'
    >>>   MINT = 'mint'
    >>>
    >>> class Shake(Model):
    >>>   flavor = UnicodeEnumAttribute(ShakeFlavor)
    """
    attr_type = pynamodb.constants.STRING
