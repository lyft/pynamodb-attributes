from enum import Enum

import pytest
from pynamodb.attributes import NumberAttribute
from pynamodb.models import Model

from pynamodb_attributes import UnicodeEnumAttribute
from tests.meta import dynamodb_table_meta


class MyEnum(Enum):
    foo_key = 'foo_value'
    bar_key = 'bar_value'


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    id = NumberAttribute(hash_key=True)  # noqa: A003
    value = UnicodeEnumAttribute(MyEnum, null=True)


@pytest.fixture(scope='module', autouse=True)
def create_table():
    MyModel.create_table()


def test_invalid_enum():
    class IntEnum(Enum):
        foo_key = 'foo_value'
        bar_key = 2

    with pytest.raises(TypeError):
        UnicodeEnumAttribute(IntEnum)


def test_serialization_invalid_type():
    model = MyModel()
    model.id = 123
    model.value = "invalid"

    with pytest.raises(TypeError):
        model.save()


@pytest.mark.parametrize(
    ['value', 'expected_attributes'], [
        (None, {}),
        (MyEnum.foo_key, {'value': {'S': 'foo_value'}}),
        (MyEnum.bar_key, {'value': {'S': 'bar_value'}}),
    ],
)
def test_serialization(value, expected_attributes):
    MyModel.create_table()

    model = MyModel()
    model.id = 123
    model.value = value
    model.save()

    # verify underlying storage
    item = MyModel._get_connection().get_item('123')
    assert item == {'Item': {'id': {'N': '123'}, **expected_attributes}}

    # verify deserialization
    model = MyModel.get(123)
    assert model.value == value
