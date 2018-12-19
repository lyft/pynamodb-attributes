from datetime import date

import pytest
from pynamodb.models import Model

from pynamodb_attributes import IntegerAttribute
from pynamodb_attributes.integer_date import IntegerDateAttribute
from tests.meta import dynamodb_table_meta


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    id = IntegerAttribute(hash_key=True)  # noqa: A003
    value = IntegerDateAttribute(null=True)


@pytest.fixture(scope='module', autouse=True)
def create_table():
    MyModel.create_table()


def test_serialization_non_null():
    model = MyModel()
    model.id = 123
    model.value = date(2015, 12, 31)
    model.save()

    # verify underlying storage
    item = MyModel._get_connection().get_item('123')
    assert item == {'Item': {'id': {'N': '123'}, 'value': {'N': '20151231'}}}

    # verify deserialization
    model = MyModel.get(123)
    assert model.value.year == 2015
    assert model.value.month == 12
    assert model.value.day == 31


def test_serialization_null():
    model = MyModel()
    model.id = 123
    model.value = None
    model.save()

    # verify underlying storage
    item = MyModel._get_connection().get_item('123')
    assert item == {'Item': {'id': {'N': '123'}}}

    # verify deserialization
    model = MyModel.get(123)
    assert model.value is None
