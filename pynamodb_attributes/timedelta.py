from datetime import timedelta
from typing import Any
from typing import Optional

import pynamodb
from pynamodb.attributes import Attribute


class TimedeltaAttribute(Attribute[timedelta]):
    """
    Stores a timedelta as a number of seconds (truncated).

    >>> class MyModel(Model):
    >>>   delta = TimedeltaAttribute(default=lambda: timedelta(seconds=5))
    >>>   delta_ms = TimedeltaMsAttribute(default=lambda: timedelta(milliseconds=500))
    """

    attr_type = pynamodb.constants.NUMBER
    _multiplier = 1.0

    def deserialize(self, value: str) -> timedelta:
        return timedelta(microseconds=float(value) * (1000000.0 / self._multiplier))

    def serialize(self, td: timedelta) -> str:
        return str(int(td.total_seconds() * self._multiplier))

    def __set__(self, instance: Any, value: Optional[Any]) -> None:
        if value is not None and not isinstance(value, timedelta):
            raise TypeError(
                f"value has invalid type '{type(value)}'; Optional[timedelta] expected",
            )
        return super().__set__(instance, value)


class TimedeltaMsAttribute(TimedeltaAttribute):
    """
    Stores a timedelta as a number of milliseconds AKA ms (truncated).
    """

    _multiplier = 1000.0


class TimedeltaUsAttribute(TimedeltaAttribute):
    """
    Stores a timedelta as a number of microseconds AKA μs (truncated).
    """

    _multiplier = 1000000.0
