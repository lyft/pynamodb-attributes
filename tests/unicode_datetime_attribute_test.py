from datetime import datetime
from unittest.mock import ANY

import pytest
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from typing_extensions import assert_type

from pynamodb_attributes import UnicodeDatetimeAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


CUSTOM_FORMAT = "%m/%d/%Y, %H:%M:%S"
CUSTOM_FORMAT_DATE = "11/22/2020, 11:22:33"
TEST_ISO_DATE_NO_OFFSET = "2020-11-22T11:22:33.444444"
TEST_ISO_DATE_UTC = "2020-11-22T11:22:33.444444+00:00"
TEST_ISO_DATE_PST = "2020-11-22T03:22:33.444444-08:00"


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    default = UnicodeDatetimeAttribute(null=True)
    no_force_tz = UnicodeDatetimeAttribute(force_tz=False, null=True)
    force_utc = UnicodeDatetimeAttribute(force_utc=True, null=True)
    force_utc_no_force_tz = UnicodeDatetimeAttribute(
        force_utc=True,
        force_tz=False,
        null=True,
    )
    custom_format = UnicodeDatetimeAttribute(fmt=CUSTOM_FORMAT, null=True)


assert_type(MyModel.default, UnicodeDatetimeAttribute)
assert_type(MyModel().default, datetime)


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


@pytest.mark.parametrize(
    ["value", "expected_str", "expected_value"],
    [
        (
            datetime.fromisoformat(TEST_ISO_DATE_NO_OFFSET),
            TEST_ISO_DATE_UTC,
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
        ),
        (
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
            TEST_ISO_DATE_UTC,
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
        ),
        (
            datetime.fromisoformat(TEST_ISO_DATE_PST),
            TEST_ISO_DATE_PST,
            datetime.fromisoformat(TEST_ISO_DATE_PST),
        ),
    ],
)
def test_default_serialization(value, expected_str, expected_value, uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.default = value

    model.save()

    actual = MyModel.get(hash_key=uuid_key)
    assert actual.default == expected_value

    item = _connection(MyModel).get_item(uuid_key)
    assert item["Item"] == {"key": ANY, "default": {"S": expected_str}}


@pytest.mark.parametrize(
    ["value", "expected_str", "expected_value"],
    [
        (
            datetime.fromisoformat(TEST_ISO_DATE_NO_OFFSET),
            TEST_ISO_DATE_NO_OFFSET,
            datetime.fromisoformat(TEST_ISO_DATE_NO_OFFSET),
        ),
        (
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
            TEST_ISO_DATE_UTC,
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
        ),
        (
            datetime.fromisoformat(TEST_ISO_DATE_PST),
            TEST_ISO_DATE_PST,
            datetime.fromisoformat(TEST_ISO_DATE_PST),
        ),
    ],
)
def test_no_force_tz_serialization(value, expected_str, expected_value, uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.no_force_tz = value

    model.save()

    actual = MyModel.get(hash_key=uuid_key)
    item = _connection(MyModel).get_item(uuid_key)

    assert item["Item"] == {"key": ANY, "no_force_tz": {"S": expected_str}}

    assert actual.no_force_tz == expected_value


@pytest.mark.parametrize(
    ["value", "expected_str", "expected_value"],
    [
        (
            datetime.fromisoformat(TEST_ISO_DATE_NO_OFFSET),
            TEST_ISO_DATE_UTC,
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
        ),
        (
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
            TEST_ISO_DATE_UTC,
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
        ),
        (
            datetime.fromisoformat(TEST_ISO_DATE_PST),
            TEST_ISO_DATE_UTC,
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
        ),
    ],
)
def test_force_utc_serialization(value, expected_str, expected_value, uuid_key):
    model = MyModel()
    model.key = uuid_key
    model.force_utc = value

    model.save()

    actual = MyModel.get(hash_key=uuid_key)
    item = _connection(MyModel).get_item(uuid_key)

    assert item["Item"] == {"key": ANY, "force_utc": {"S": expected_str}}

    assert actual.force_utc == expected_value


@pytest.mark.parametrize(
    ["value", "expected_str", "expected_value"],
    [
        (
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
            TEST_ISO_DATE_UTC,
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
        ),
        (
            datetime.fromisoformat(TEST_ISO_DATE_PST),
            TEST_ISO_DATE_UTC,
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
        ),
    ],
)
def test_force_utc_no_force_tz_serialization(
    value,
    expected_str,
    expected_value,
    uuid_key,
):
    model = MyModel()
    model.key = uuid_key
    model.force_utc_no_force_tz = value

    model.save()

    actual = MyModel.get(hash_key=uuid_key)
    item = _connection(MyModel).get_item(uuid_key)

    assert item["Item"] == {"key": ANY, "force_utc_no_force_tz": {"S": expected_str}}

    assert actual.force_utc_no_force_tz == expected_value


@pytest.mark.parametrize(
    ["value", "expected_str", "expected_value"],
    [
        (
            datetime.fromisoformat(TEST_ISO_DATE_UTC),
            CUSTOM_FORMAT_DATE,
            datetime(2020, 11, 22, 11, 22, 33),
        ),
    ],
)
def test_custom_format_force_tz_serialization(
    value,
    expected_str,
    expected_value,
    uuid_key,
):
    model = MyModel()
    model.key = uuid_key
    model.custom_format = value

    model.save()

    actual = MyModel.get(hash_key=uuid_key)
    item = _connection(MyModel).get_item(uuid_key)

    assert item["Item"] == {"key": ANY, "custom_format": {"S": expected_str}}

    assert actual.custom_format == expected_value
