import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

from pynamodb_attributes import FloatAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = FloatAttribute(null=True)


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


def test_serialization_non_null(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = 45.6
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert item["Item"]["value"] == {"N": "45.6"}

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value == 45.6


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
