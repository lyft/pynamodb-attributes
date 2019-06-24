from datetime import datetime, timezone

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

from pynamodb_attributes import (
    TimestampAttribute,
    TimestampMsAttribute,
    TimestampUsAttribute,
    TimestampNsAttribute,
)
from tests.meta import dynamodb_table_meta


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = TimestampAttribute()
    value_ms = TimestampMsAttribute()
    value_us = TimestampUsAttribute()
    value_ns = TimestampNsAttribute()


@pytest.fixture(scope='module', autouse=True)
def create_table():
    MyModel.create_table()


def test_serialization(uuid_key):
    now = datetime.now(tz=timezone.utc)
    model = MyModel()
    model.key = uuid_key
    model.value = now
    model.value_ms = now
    model.value_us = now
    model.value_ns = now
    model.save()

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value == now.replace(microsecond=0)
    assert model.value_ms == now.replace(microsecond=now.microsecond // 1_000 * 1_000)
    assert model.value_us == now
    assert model.value_ns == now  # datetime has only microsecond precision


def test_set_invalid_type():
    model = MyModel()
    with pytest.raises(TypeError, match='invalid type'):
        model.value = 42


def test_set_naive_datetime():
    model = MyModel()
    with pytest.raises(TypeError, match='aware datetime expected'):
        model.value = datetime.utcnow()


def test_set_get():
    model = MyModel()
    now = datetime.now(tz=timezone.utc)
    model.value = now
    assert model.value == now  # assert no data loss (before serialization)
