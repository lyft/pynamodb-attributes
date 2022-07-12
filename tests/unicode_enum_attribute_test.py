from enum import Enum
from unittest.mock import ANY

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from typing_extensions import assert_type

from pynamodb_attributes import UnicodeEnumAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


class MyEnum(Enum):
    foo_key = "foo_value"
    bar_key = "bar_value"
    unknown_key = "unknown_value"


class MyEnumWithMissing(Enum):
    foo_key = "foo_value"
    bar_key = "bar_value"
    missing_key = "missing_value"

    @classmethod
    def _missing_(cls, key):
        return cls.missing_key


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = UnicodeEnumAttribute(MyEnum, null=True)
    value_with_unknown = UnicodeEnumAttribute(
        MyEnum,
        unknown_value=MyEnum.unknown_key,
        null=True,
    )
    value_with_missing = UnicodeEnumAttribute(MyEnumWithMissing, null=True)


assert_type(MyModel.value, UnicodeEnumAttribute[MyEnum])
assert_type(MyModel().value, MyEnum)


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


def test_invalid_enum():
    class IntEnum(Enum):
        foo_key = "foo_value"
        bar_key = 2

    with pytest.raises(TypeError, match="values must be all strings"):
        UnicodeEnumAttribute(IntEnum)


def test_serialization_invalid_type(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = "invalid"  # type: ignore

    with pytest.raises(TypeError, match="value has invalid type"):
        model.save()


def test_serialization_unknown_value_fail(uuid_key):
    _connection(MyModel).put_item(
        uuid_key,
        attributes={
            "value": {"S": "nonexistent_value"},
        },
    )
    with pytest.raises(ValueError, match="'nonexistent_value' is not a valid MyEnum"):
        MyModel.get(uuid_key)


def test_serialization_unknown_value_success(uuid_key):
    _connection(MyModel).put_item(
        uuid_key,
        attributes={
            "value_with_unknown": {"S": "nonexistent_value"},
        },
    )
    model = MyModel.get(uuid_key)
    assert model.value_with_unknown == MyEnum.unknown_key


def test_serialization_missing_value_success(uuid_key):
    _connection(MyModel).put_item(
        uuid_key,
        attributes={
            "value_with_missing": {"S": "nonexistent_value"},
        },
    )
    model = MyModel.get(uuid_key)
    assert model.value_with_missing == MyEnumWithMissing.missing_key


@pytest.mark.parametrize(
    ["value", "expected_attributes"],
    [
        (None, {}),
        (MyEnum.foo_key, {"value": {"S": "foo_value"}}),
        (MyEnum.bar_key, {"value": {"S": "bar_value"}}),
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
