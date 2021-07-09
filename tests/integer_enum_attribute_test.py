from enum import Enum
from unittest.mock import ANY

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

from pynamodb_attributes.integer_enum import IntegerEnumAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


class MyEnum(Enum):
    foo_key = 1
    bar_key = 2
    unknown_key = 0


class MyEnumWithMissing(Enum):
    foo_key = 1
    bar_key = 2
    missing_key = 0

    @classmethod
    def _missing_(cls, key):
        return cls.missing_key


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = IntegerEnumAttribute(MyEnum, null=True)
    value_with_unknown = IntegerEnumAttribute(
        MyEnum,
        unknown_value=MyEnum.unknown_key,
        null=True,
    )
    value_with_missing = IntegerEnumAttribute(MyEnumWithMissing, null=True)


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


def test_invalid_enum():
    class StringEnum(Enum):
        foo_key = "foo_value"
        bar_key = 2

    with pytest.raises(TypeError, match="values must be all ints"):
        IntegerEnumAttribute(StringEnum)


def test_serialization_invalid_type(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = 999  # type: ignore

    with pytest.raises(TypeError, match="value has invalid type"):
        model.save()


def test_serialization_unknown_value_fail(uuid_key):
    _connection(MyModel).put_item(
        uuid_key,
        attributes={
            "value": {"N": "9001"},
        },
    )
    with pytest.raises(ValueError, match="9001 is not a valid MyEnum"):
        MyModel.get(uuid_key)


def test_serialization_unknown_value_success(uuid_key):
    _connection(MyModel).put_item(
        uuid_key,
        attributes={
            "value_with_unknown": {"N": "9001"},
        },
    )
    model = MyModel.get(uuid_key)
    assert model.value_with_unknown == MyEnum.unknown_key


def test_serialization_missing_value_success(uuid_key):
    _connection(MyModel).put_item(
        uuid_key,
        attributes={
            "value_with_missing": {"N": "9001"},
        },
    )
    model = MyModel.get(uuid_key)
    assert model.value_with_missing == MyEnumWithMissing.missing_key


@pytest.mark.parametrize(
    ["value", "expected_attributes"],
    [
        (None, {}),
        (MyEnum.foo_key, {"value": {"N": "1"}}),
        (MyEnum.bar_key, {"value": {"N": "2"}}),
    ],
)
def test_serialization(value, expected_attributes, uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = value
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert item["Item"] == {"key": ANY, **expected_attributes}

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value == value
