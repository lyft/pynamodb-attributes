from uuid import UUID

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from typing_extensions import assert_type

from pynamodb_attributes import UUIDAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = UUIDAttribute(null=True)


assert_type(MyModel.value, UUIDAttribute)
assert_type(MyModel().value, UUID)


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


def test_deserialization_no_dashes():
    uuid_attribute = UUIDAttribute(remove_dashes=True)
    uuid_str_no_dashes = "19c4f2515e364cc0bfeb983dd5d2bacd"

    assert UUID("19c4f251-5e36-4cc0-bfeb-983dd5d2bacd") == uuid_attribute.deserialize(
        uuid_str_no_dashes,
    )


def test_serialization_no_dashes():
    uuid_attribute = UUIDAttribute(remove_dashes=True)
    uuid_value = UUID("19c4f251-5e36-4cc0-bfeb-983dd5d2bacd")

    assert "19c4f2515e364cc0bfeb983dd5d2bacd" == uuid_attribute.serialize(uuid_value)


def test_serialization_non_null(uuid_key):
    model = MyModel()
    model.key = uuid_key
    uuid_str = "19c4f251-5e36-4cc0-bfeb-983dd5d2bacd"
    uuid_value = UUID(uuid_str)
    model.value = uuid_value
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert item["Item"]["value"] == {"S": uuid_str}

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value == uuid_value


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
