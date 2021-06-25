from typing import NamedTuple
from typing import Optional
from typing import Union
from unittest.mock import ANY

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

from pynamodb_attributes import UnicodeDelimitedTupleAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


class MyTuple(NamedTuple):
    country: str
    city: str
    zip_code: Optional[int] = None


class MyUnionTuple(NamedTuple):
    str_or_int_or_none: Union[None, str, int]
    int_or_str: Union[int, str]


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    default_delimiter = UnicodeDelimitedTupleAttribute(MyTuple, null=True)
    custom_delimiter = UnicodeDelimitedTupleAttribute(MyTuple, delimiter=".", null=True)
    untyped = UnicodeDelimitedTupleAttribute(tuple, null=True)
    union_type = UnicodeDelimitedTupleAttribute(MyUnionTuple, null=True)


def test_serialization_containing_delimiter(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.default_delimiter = MyTuple(country="U::S", city="San Francisco")

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


@pytest.mark.parametrize(
    ["raw_input", "expected"],
    [
        ({"union_type": {"S": "string::42"}}, MyUnionTuple("string", 42)),
        (
            {"union_type": {"S": "string::another_string"}},
            MyUnionTuple("string", "another_string"),
        ),
    ],
)
def test_serialization_union_type(raw_input, expected, uuid_key):
    _connection(MyModel).put_item(
        hash_key=uuid_key,
        attributes={"union_type": {"S": "string::42"}},
    )

    model = MyModel.get(hash_key=uuid_key)
    assert model.union_type == MyUnionTuple("string", 42)


def test_serialization_unparsable_raises(uuid_key):
    _connection(MyModel).put_item(
        hash_key=uuid_key,
        attributes={"default_delimiter": {"S": "US::San Francisco::NOT_A_ZIP_CODE"}},
    )
    with pytest.raises(
        ValueError,
        match=r"Unable to parse value: 'NOT_A_ZIP_CODE' for any of the following "
        r"types: '\[int, NoneType\]",
    ):
        MyModel.get(hash_key=uuid_key)
