from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Optional

import pynamodb.attributes
from pynamodb.attributes import Attribute


class UnicodeDatetimeAttribute(Attribute[datetime]):
    """
    Stores a 'datetime.datetime' object as an ISO8601 formatted string

    This is useful for wanting database readable datetime objects that also sort.

    >>> class MyModel(Model):
    >>>   created_at = UnicodeDatetimeAttribute()
    """

    attr_type = pynamodb.attributes.STRING

    def __init__(
        self,
        *,
        force_tz: bool = True,
        force_utc: bool = False,
        fmt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        :param force_tz: If set it will add timezone info to the `datetime` value if no `tzinfo` is currently
            set before serializing, defaults to `True`
        :param force_utc: If set it will normalize the `datetime` to UTC before serializing the value
        :param fmt: If set this value will be used to format the `datetime` object for serialization
            and deserialization
        """

        super().__init__(**kwargs)
        self._force_tz = force_tz
        self._force_utc = force_utc
        self._fmt = fmt

    def deserialize(self, value: str) -> datetime:
        return (
            datetime.fromisoformat(value)
            if self._fmt is None
            else datetime.strptime(value, self._fmt)
        )

    def serialize(self, value: datetime) -> str:
        if self._force_tz and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        if self._force_utc:
            value = value.astimezone(tz=timezone.utc)
        return value.isoformat() if self._fmt is None else value.strftime(self._fmt)
