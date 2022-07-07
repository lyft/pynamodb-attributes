from datetime import timedelta

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from typing_extensions import assert_type

from pynamodb_attributes import TimedeltaAttribute
from pynamodb_attributes import TimedeltaMsAttribute
from pynamodb_attributes import TimedeltaUsAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = TimedeltaAttribute(null=True)
    value_ms = TimedeltaMsAttribute(null=True)
    value_us = TimedeltaUsAttribute(null=True)


assert_type(MyModel().value, timedelta)
assert_type(MyModel().value_ms, timedelta)
assert_type(MyModel().value_us, timedelta)


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


def test_serialization_non_null(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = model.value_ms = model.value_us = timedelta(
        seconds=456,
        microseconds=123456,
    )
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert item["Item"]["value"] == {"N": "456"}
    assert item["Item"]["value_ms"] == {"N": "456123"}
    assert item["Item"]["value_us"] == {"N": "456123456"}

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value == timedelta(seconds=456)
    assert model.value_ms == timedelta(seconds=456, microseconds=123000)
    assert model.value_us == timedelta(seconds=456, microseconds=123456)


def test_serialization_null(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = None
    model.value_ms = None
    model.value_us = None
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert "value" not in item["Item"]
    assert "value_ms" not in item["Item"]
    assert "value_us" not in item["Item"]

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value is None
    assert model.value_ms is None
    assert model.value_us is None


def test_set_invalid_type():
    model = MyModel()
    with pytest.raises(TypeError, match="invalid type"):
        model.value = 42
