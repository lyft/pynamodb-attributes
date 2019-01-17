import json
from datetime import date

from pynamodb.attributes import Attribute

from pynamodb_attributes import IntegerAttribute


class IntegerDateAttribute(Attribute):
    """Represents a date as an integer (e.g. 2015_12_31 for December 31st, 2015)."""
    attr_type = IntegerAttribute.attr_type

    def serialize(self, value: date) -> str:
        return json.dumps(value.year * 1_00_00 + value.month * 1_00 + value.day)

    def deserialize(self, value: str) -> date:
        n = json.loads(value)
        return date(n // 1_00_00, n // 1_00 % 1_00, n % 1_00)
