from datetime import datetime

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

from pynamodb_attributes import DateTimeAttribute
from tests.meta import dynamodb_table_meta


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = DateTimeAttribute(null=True)


@pytest.fixture(scope='module', autouse=True)
def create_table():
    MyModel.create_table()





def test_serialization_non_null(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = datetime.strptime('2019-03-19T01:27:35.139000+0000', '%Y-%m-%dT%H:%M:%S.%f%z')
    model.save()

    # verify underlying storage
    item = MyModel._get_connection().get_item(uuid_key)
    assert item['Item']['value'] == {'S': '2019-03-19T01:27:35.139000+0000'}

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value == datetime.strptime('2019-03-19T01:27:35.139000+0000', '%Y-%m-%dT%H:%M:%S.%f%z')


def test_serialization_null(uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.value = None
    model.save()

    # verify underlying storage
    item = MyModel._get_connection().get_item(uuid_key)
    assert 'value' not in item['Item']

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value is None
