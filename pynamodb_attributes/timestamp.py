from datetime import datetime, timezone

import pynamodb.constants
from pynamodb.attributes import Attribute


class TimestampAttribute(Attribute):
    """"
    Stores times as Unix epoch timestamps in a DynamoDB number.

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

    def __set__(self, instance, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError(f"value has invalid type '{type(value)}; datetime expected")
        if value.tzinfo is None:
            raise TypeError("offset-aware datetime expected")
        return super().__set__(instance, value)


class TimestampMsAttribute(TimestampAttribute):
    """"
    Stores times as Unix epoch timestamps in milliseconds in a DynamoDB number.
    """
    _multiplier = 1_000.0


class TimestampNsAttribute(TimestampAttribute):
    """"
    Stores times as Unix epoch timestamps in nanoseconds in a DynamoDB number.
    """
    _multiplier = 1_000_000.0
