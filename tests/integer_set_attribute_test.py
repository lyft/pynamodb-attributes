from typing import Set

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from typing_extensions import assert_type

from pynamodb_attributes import IntegerSetAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = IntegerSetAttribute(null=True)


assert_type(MyModel.value, IntegerSetAttribute)
assert_type(MyModel().value, Set[int])


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


def test_serialization_non_null(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = {456, 789}
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert item["Item"]["value"] == {"NS": ["456", "789"]}

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value == {456, 789}


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
