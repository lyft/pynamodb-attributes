from typing import Any
from typing import NamedTuple
from typing import Tuple
from unittest.mock import ANY

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from typing_extensions import assert_type

from pynamodb_attributes import UnicodeDelimitedTupleAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


class MyTuple(NamedTuple):
    country: str
    city: str
    # should be Optional[int] but deserialization does not support it
    zip_code: int = None  # type: ignore


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    default_delimiter = UnicodeDelimitedTupleAttribute(MyTuple, null=True)
    custom_delimiter = UnicodeDelimitedTupleAttribute(MyTuple, delimiter=".", null=True)
    untyped = UnicodeDelimitedTupleAttribute(tuple, null=True)


assert_type(MyModel.default_delimiter, UnicodeDelimitedTupleAttribute[MyTuple])
assert_type(MyModel.untyped, UnicodeDelimitedTupleAttribute[Tuple[Any, ...]])


def test_serialization_containing_delimiter(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.default_delimiter = MyTuple(country="U::S", city="San Francisco")

    assert_type(model.default_delimiter, MyTuple)
    assert_type(model.default_delimiter.country, str)

    with pytest.raises(ValueError):
        model.save()


def test_serialization_containing_custom_delimiter(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.custom_delimiter = MyTuple(country="U.S.", city="San Francisco")

    with pytest.raises(ValueError):
        model.save()

    model.custom_delimiter = MyTuple(country="U::S", city="San Francisco")
    model.save()


def test_serialization_invalid_type(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.default_delimiter = (1, 2, 3)  # type: ignore

    with pytest.raises(TypeError):
        model.save()


def test_serialization_typing(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.default_delimiter = MyTuple("US", "San Francisco", 94107)
    model.save()

    model = MyModel.get(uuid_key)
    assert model.default_delimiter.country == "US"
    assert model.default_delimiter.city == "San Francisco"
    assert model.default_delimiter.zip_code == 94107  # note the type


@pytest.mark.parametrize(
    ["value", "expected_attributes"],
    [
        (None, {}),
        (
            MyTuple(country="US", city="San Francisco", zip_code=94107),
            {
                "default_delimiter": {"S": "US::San Francisco::94107"},
                "custom_delimiter": {"S": "US.San Francisco.94107"},
            },
        ),
        (
            MyTuple(country="US", city="San Francisco"),
            {
                "default_delimiter": {"S": "US::San Francisco"},
                "custom_delimiter": {"S": "US.San Francisco"},
            },
        ),
    ],
)
def test_serialization(expected_attributes, value, uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.default_delimiter = value
    model.custom_delimiter = value
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert item["Item"] == {"key": ANY, **expected_attributes}

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.default_delimiter == value
    assert model.custom_delimiter == value


@pytest.mark.parametrize(
    ["value", "expected_attributes"],
    [
        (None, {}),
        (
            ("US", "San Francisco", "94107"),
            {
                "untyped": {"S": "US::San Francisco::94107"},
            },
        ),
        (
            ("US", "San Francisco"),
            {
                "untyped": {"S": "US::San Francisco"},
            },
        ),
    ],
)
def test_serialization_untyped(expected_attributes, value, uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.untyped = value
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert item["Item"] == {"key": ANY, **expected_attributes}

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.untyped == value

    assert_type(MyModel.untyped, UnicodeDelimitedTupleAttribute[Tuple[Any, ...]])
