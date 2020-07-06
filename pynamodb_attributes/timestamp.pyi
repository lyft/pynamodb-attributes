from datetime import datetime
from typing import Any

from ._typing import Attribute


class TimestampAttribute(Attribute[datetime]):
    ...


class TimestampMsAttribute(TimestampAttribute):
    ...


class TimestampUsAttribute(TimestampAttribute):
    ...
