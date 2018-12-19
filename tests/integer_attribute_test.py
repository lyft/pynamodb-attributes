import pytest
from pynamodb.models import Model

from pynamodb_attributes import IntegerAttribute
from tests.meta import dynamodb_table_meta


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    id = IntegerAttribute(hash_key=True)  # noqa: A003
    value = IntegerAttribute(null=True)


@pytest.fixture(scope='module', autouse=True)
def create_table():
    MyModel.create_table()


def test_serialization_non_null():
    model = MyModel()
    model.id = 123
    model.value = 456
    model.save()

    # verify underlying storage
    item = MyModel._get_connection().get_item('123')
    assert item == {'Item': {'id': {'N': '123'}, 'value': {'N': '456'}}}

    # verify deserialization
    model = MyModel.get(123)
    assert model.value == 456


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
