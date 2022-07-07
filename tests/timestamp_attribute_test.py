from datetime import datetime
from datetime import timezone

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from typing_extensions import assert_type

from pynamodb_attributes import TimestampAttribute
from pynamodb_attributes import TimestampMsAttribute
from pynamodb_attributes import TimestampUsAttribute
from tests.meta import dynamodb_table_meta


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = TimestampAttribute()
    value_ms = TimestampMsAttribute()
    value_us = TimestampUsAttribute()

    null_value = TimestampAttribute(null=True)


assert_type(MyModel().value, datetime)
assert_type(MyModel().value_ms, datetime)
assert_type(MyModel().value_us, datetime)


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


def test_serialization(uuid_key):
    now = datetime.now(tz=timezone.utc)
    model = MyModel()
    model.key = uuid_key
    model.value = now
    model.value_ms = now
    model.value_us = now
    model.save()

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value == now.replace(microsecond=0)
    assert model.value_ms == now.replace(microsecond=now.microsecond // 1_000 * 1_000)
    assert model.value_us == now
    assert model.null_value is None


def test_set_invalid_type():
    model = MyModel()
    with pytest.raises(TypeError, match="invalid type"):
        model.value = 42


def test_set_naive_datetime():
    model = MyModel()
    with pytest.raises(TypeError, match="aware datetime expected"):
        model.value = datetime.utcnow()


def test_set_none_succeeds_on_nullable():
    model = MyModel()
    model.null_value = None
    assert model.null_value is None


def test_set_timestame_succeeds_on_nullable():
    model = MyModel()
    now = datetime.now(tz=timezone.utc)
    model.null_value = now
    assert model.null_value == now


def test_set_get():
    model = MyModel()
    now = datetime.now(tz=timezone.utc)
    model.value = now
    assert model.value == now, "data lost before serialization"


def test_set_get_nullable():
    model = MyModel()
    now = datetime.now(tz=timezone.utc)
    model.null_value = now
    assert model.null_value == now, "data lost before serialization"
