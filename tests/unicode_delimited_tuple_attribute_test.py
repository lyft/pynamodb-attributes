from typing import NamedTuple

import pytest
from pynamodb.attributes import NumberAttribute
from pynamodb.models import Model

from pynamodb_attributes import UnicodeDelimitedTupleAttribute
from tests.meta import dynamodb_table_meta


class MyTuple(NamedTuple):
    country: str
    city: str
    zip_code: int = None


@pytest.fixture(scope='module', autouse=True)
def create_table():
    MyModel.create_table()


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    id = NumberAttribute(hash_key=True)  # noqa: A003
    default_delimiter = UnicodeDelimitedTupleAttribute(MyTuple, null=True)
    custom_delimiter = UnicodeDelimitedTupleAttribute(MyTuple, delimiter='.', null=True)
    untyped = UnicodeDelimitedTupleAttribute(tuple, null=True)


def test_serialization_containing_delimiter():
    model = MyModel()
    model.id = 123
    model.default_delimiter = MyTuple(country="U::S", city="San Francisco")

    with pytest.raises(ValueError):
        model.save()


def test_serialization_containing_custom_delimiter():
    model = MyModel()
    model.id = 123
    model.custom_delimiter = MyTuple(country="U.S.", city="San Francisco")

    with pytest.raises(ValueError):
        model.save()

    model.custom_delimiter = MyTuple(country="U::S", city="San Francisco")
    model.save()


def test_serialization_invalid_type():
    model = MyModel()
    model.id = 123
    model.default_delimiter = (1, 2, 3)

    with pytest.raises(TypeError):
        model.save()


def test_serialization_typing():
    model = MyModel()
    model.id = 123
    model.default_delimiter = MyTuple('US', 'San Francisco', 94107)
    model.save()

    model = MyModel.get(123)
    assert model.default_delimiter.country == 'US'
    assert model.default_delimiter.city == 'San Francisco'
    assert model.default_delimiter.zip_code == 94107  # note the type


@pytest.mark.parametrize(
    ['value', 'expected_attributes'], [
        (None, {}),
        (
            MyTuple(country='US', city='San Francisco', zip_code=94107),
            {
                'default_delimiter': {'S': 'US::San Francisco::94107'},
                'custom_delimiter': {'S': 'US.San Francisco.94107'},
            },
        ),
        (
            MyTuple(country='US', city='San Francisco'),
            {
                'default_delimiter': {'S': 'US::San Francisco'},
                'custom_delimiter': {'S': 'US.San Francisco'},
            },
        ),
    ],
)
def test_serialization(expected_attributes, value):
    model = MyModel()
    model.id = 123
    model.default_delimiter = value
    model.custom_delimiter = value
    model.save()

    # verify underlying storage
    item = MyModel._get_connection().get_item('123')
    assert item == {'Item': {'id': {'N': '123'}, **expected_attributes}}

    # verify deserialization
    model = MyModel.get(123)
    assert model.default_delimiter == value
    assert model.custom_delimiter == value


@pytest.mark.parametrize(
    ['value', 'expected_attributes'], [
        (None, {}),
        (
            ('US', 'San Francisco', '94107'),
            {
                'untyped': {'S': 'US::San Francisco::94107'},
            },
        ),
        (
            ('US', 'San Francisco'),
            {
                'untyped': {'S': 'US::San Francisco'},
            },
        ),
    ],
)
def test_serialization_untyped(expected_attributes, value):
    model = MyModel()
    model.id = 456
    model.untyped = value
    model.save()

    # verify underlying storage
    item = MyModel._get_connection().get_item('456')
    assert item == {'Item': {'id': {'N': '456'}, **expected_attributes}}

    # verify deserialization
    model = MyModel.get(456)
    assert model.untyped == value
