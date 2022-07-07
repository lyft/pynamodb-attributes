from datetime import date
from unittest.mock import ANY

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from typing_extensions import assert_type

from pynamodb_attributes.integer_date import IntegerDateAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = IntegerDateAttribute(null=True)


assert_type(MyModel.value, IntegerDateAttribute)
assert_type(MyModel().value, date)


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


def test_serialization_non_null(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = date(2015, 12, 31)
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert item["Item"] == {"key": ANY, "value": {"N": "20151231"}}

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value.year == 2015
    assert model.value.month == 12
    assert model.value.day == 31


def test_serialization_null(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = None
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert "value" not in item["Item"]

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value is None
