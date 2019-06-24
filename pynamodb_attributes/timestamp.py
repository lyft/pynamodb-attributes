from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Optional

import pynamodb.constants
from pynamodb.attributes import Attribute


class TimestampAttribute(Attribute):
    """"
    Stores time as a Unix epoch timestamp (in seconds) in a DynamoDB number.

    >>> class MyModel(Model):
    >>>   created_at_seconds = TimestampAttribute(default=lambda: datetime.now(tz=timezone.utc))
    >>>   created_at_ms = TimestampMsAttribute(default=lambda: datetime.now(tz=timezone.utc))
    """
    attr_type = pynamodb.constants.NUMBER
    _multiplier = 1.0

    def deserialize(self, value: str) -> datetime:
        return datetime.fromtimestamp(int(value) / self._multiplier, tz=timezone.utc)

    def serialize(self, value: datetime) -> str:
        return str(int(value.timestamp() * self._multiplier))

    def __set__(self, instance: Any, value: Optional[Any]) -> None:
        if not isinstance(value, datetime):
            raise TypeError(f"value has invalid type '{type(value)}'; datetime expected")
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise TypeError("aware datetime expected")
        return super().__set__(instance, value)


class TimestampMsAttribute(TimestampAttribute):
    """"
    Stores time as a Unix epoch timestamp in milliseconds (ms) in a DynamoDB number.
    """
    _multiplier = 1000.0


class TimestampUsAttribute(TimestampAttribute):
    """"
    Stores times as a Unix epoch timestamp in microseconds (μs) in a DynamoDB number.
    """
    _multiplier = 1000000.0
