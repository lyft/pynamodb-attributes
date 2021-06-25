# flake8: noqa E501
"""
Note: The expected error strings may change in a future version of mypy.
      Please update as needed.
"""
import pytest

pytest.register_assert_rewrite("tests.mypy_helpers")
from tests.mypy_helpers import assert_mypy_output  # noqa


def test_integer_attribute():
    assert_mypy_output(
        """
    from pynamodb.models import Model
    from pynamodb_attributes import IntegerAttribute

    class MyModel(Model):
        my_attr = IntegerAttribute()

    reveal_type(MyModel.my_attr)  # E: Revealed type is "pynamodb_attributes.integer.IntegerAttribute"
    reveal_type(MyModel().my_attr)  # E: Revealed type is "builtins.int*"
    """,
    )


def test_integer_date_attribute():
    assert_mypy_output(
        """
    from pynamodb.models import Model
    from pynamodb_attributes import IntegerDateAttribute

    class MyModel(Model):
        my_attr = IntegerDateAttribute()

    reveal_type(MyModel.my_attr)  # E: Revealed type is "pynamodb_attributes.integer_date.IntegerDateAttribute"
    reveal_type(MyModel().my_attr)  # E: Revealed type is "datetime.date*"
    """,
    )


def test_unicode_delimited_tuple_attribute():
    assert_mypy_output(
        """
    from typing import NamedTuple
    from pynamodb.models import Model
    from pynamodb_attributes import UnicodeDelimitedTupleAttribute

    class MyTuple(NamedTuple):
        foo: str
        bar: str

    class MyModel(Model):
        my_attr = UnicodeDelimitedTupleAttribute(MyTuple)

    reveal_type(MyModel.my_attr)  # E: Revealed type is "pynamodb_attributes.unicode_delimited_tuple.UnicodeDelimitedTupleAttribute[Tuple[builtins.str, builtins.str, fallback=__main__.MyTuple]]"
    reveal_type(MyModel().my_attr)  # E: Revealed type is "Tuple[builtins.str, builtins.str, fallback=__main__.MyTuple]"
    reveal_type(MyModel().my_attr.foo)  # E: Revealed type is "builtins.str"
    """,
    )


def test_unicode_enum_attribute():
    assert_mypy_output(
        """
    from enum import Enum
    from pynamodb.models import Model
    from pynamodb_attributes import UnicodeEnumAttribute

    class MyEnum(Enum):
        foo = "foo"
        bar = "bar"

    class MyModel(Model):
        my_attr = UnicodeEnumAttribute(MyEnum)

    reveal_type(MyModel.my_attr)  # E: Revealed type is "pynamodb_attributes.unicode_enum.UnicodeEnumAttribute[__main__.MyEnum]"
    reveal_type(MyModel().my_attr)  # E: Revealed type is "__main__.MyEnum*"
    """,
    )


def test_timedelta_attribute():
    assert_mypy_output(
        """
    from datetime import timedelta
    from pynamodb.models import Model
    from pynamodb_attributes import TimedeltaAttribute
    from pynamodb_attributes import TimedeltaMsAttribute
    from pynamodb_attributes import TimedeltaUsAttribute

    class MyModel(Model):
        td = TimedeltaAttribute()
        td_ms = TimedeltaMsAttribute()
        td_us = TimedeltaUsAttribute()

    m = MyModel()
    reveal_type(m.td)  # E: Revealed type is "datetime.timedelta*"
    reveal_type(m.td_ms)  # E: Revealed type is "datetime.timedelta*"
    reveal_type(m.td_us)  # E: Revealed type is "datetime.timedelta*"

    m.save(condition=MyModel.td == timedelta(seconds=5))
    """,
    )


def test_timestamp_attribute():
    assert_mypy_output(
        """
    from datetime import datetime
    from pynamodb.models import Model
    from pynamodb_attributes import TimestampAttribute
    from pynamodb_attributes import TimestampMsAttribute
    from pynamodb_attributes import TimestampUsAttribute

    class MyModel(Model):
        ts = TimestampAttribute()
        ts_ms = TimestampMsAttribute()
        ts_us = TimestampUsAttribute()

    m = MyModel()
    reveal_type(m.ts)  # E: Revealed type is "datetime.datetime*"
    reveal_type(m.ts_ms)  # E: Revealed type is "datetime.datetime*"
    reveal_type(m.ts_us)  # E: Revealed type is "datetime.datetime*"

    m.save(condition=MyModel.ts == datetime.now())
    """,
    )


def test_uuid_attribute():
    assert_mypy_output(
        """
    from pynamodb.models import Model
    from pynamodb_attributes import UUIDAttribute

    class MyModel(Model):
        my_attr = UUIDAttribute()

    reveal_type(MyModel.my_attr)  # E: Revealed type is "pynamodb_attributes.uuid.UUIDAttribute"
    reveal_type(MyModel().my_attr)  # E: Revealed type is "uuid.UUID*"
    """,
    )
