from typing import Any
from typing import cast
from typing import Dict
from typing import Optional
from unittest.mock import ANY

import pytest
from pynamodb.attributes import MapAttribute
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from typing_extensions import assert_type

from pynamodb_attributes.unicode_protobuf_enum import UnicodeProtobufEnumAttribute
from tests.connection import _connection
from tests.meta import dynamodb_table_meta


# Something that mypy-protobuf would generate...
class diner_pb2:
    class ShakeFlavor(int):
        @classmethod
        def Name(cls, number: int) -> str:
            mapping = {
                v: k
                for k, v in vars(diner_pb2).items()
                if k.startswith("SHAKE_FLAVOR_")
            }
            if name := mapping.get(number):
                return name
            else:
                if not isinstance(number, int):
                    raise TypeError(
                        f"Enum value for {cls.__name__} must be an int, but got {type(number)} {number!r}.",
                    )
                else:
                    raise ValueError(
                        f"Enum {cls.__name__} has no name defined for value {number!r}",
                    )

        @classmethod
        def Value(cls, name: str) -> "diner_pb2.ShakeFlavor":
            mapping = {
                k: v
                for k, v in vars(diner_pb2).items()
                if k.startswith("SHAKE_FLAVOR_")
            }
            if (value := mapping.get(name)) is not None:
                return cast("diner_pb2.ShakeFlavor", value)
            else:
                raise ValueError(
                    f"Enum {cls.__name__} has no value defined for name {name!r}",
                )

    SHAKE_FLAVOR_UNKNOWN = cast(ShakeFlavor, 0)
    SHAKE_FLAVOR_VANILLA = cast(ShakeFlavor, 1)
    SHAKE_FLAVOR_CHOCOLATE = cast(ShakeFlavor, 2)


class MyMapAttr(MapAttribute[Any, Any]):
    value = UnicodeProtobufEnumAttribute(
        diner_pb2.ShakeFlavor,
        prefix="SHAKE_FLAVOR_",
        null=True,
    )


class MyModel(Model):
    Meta = dynamodb_table_meta(__name__)

    key = UnicodeAttribute(hash_key=True)
    value = UnicodeProtobufEnumAttribute(
        diner_pb2.ShakeFlavor,
        prefix="SHAKE_FLAVOR_",
        null=True,
    )
    value_upper = UnicodeProtobufEnumAttribute(
        diner_pb2.ShakeFlavor,
        prefix="SHAKE_FLAVOR_",
        null=True,
        lower=False,
    )
    value_with_unknown = UnicodeProtobufEnumAttribute(
        diner_pb2.ShakeFlavor,
        unknown_value=diner_pb2.SHAKE_FLAVOR_UNKNOWN,
        prefix="SHAKE_FLAVOR_",
        null=True,
    )
    map_attr = MyMapAttr(null=True)


assert_type(MyModel().value, diner_pb2.ShakeFlavor)


@pytest.fixture(scope="module", autouse=True)
def create_table():
    MyModel.create_table()


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
    with pytest.raises(
        ValueError,
        match="no value defined for name 'SHAKE_FLAVOR_NONEXISTENT_VALUE'",
    ):
        MyModel.get(uuid_key)


def test_serialization_unknown_value_success(uuid_key):
    _connection(MyModel).put_item(
        uuid_key,
        attributes={
            "value_with_unknown": {"S": "nonexistent_value"},
        },
    )
    model = MyModel.get(uuid_key)
    assert model.value_with_unknown == diner_pb2.SHAKE_FLAVOR_UNKNOWN


@pytest.mark.parametrize(
    ["value", "expected_attributes"],
    [
        (None, {}),
        (
            diner_pb2.SHAKE_FLAVOR_VANILLA,
            {
                "value": {"S": "vanilla"},
                "value_upper": {"S": "VANILLA"},
                "value_with_unknown": {"S": "vanilla"},
            },
        ),
        (
            diner_pb2.SHAKE_FLAVOR_CHOCOLATE,
            {
                "value": {"S": "chocolate"},
                "value_upper": {"S": "CHOCOLATE"},
                "value_with_unknown": {"S": "chocolate"},
            },
        ),
    ],
)
def test_serialization(
    value: Optional[diner_pb2.ShakeFlavor],
    expected_attributes: Dict[str, Any],
    uuid_key: str,
) -> None:
    model = MyModel()
    model.key = uuid_key
    model.value = value
    model.value_upper = value
    model.value_with_unknown = value
    model.save()

    # verify underlying storage
    item = _connection(MyModel).get_item(uuid_key)
    assert item["Item"] == {"key": ANY, **expected_attributes}

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.value == value
    assert model.value_upper == value
    assert model.value_with_unknown == value


def test_map_attribute(  # exercises the __deepcopy__ method
    uuid_key: str,
) -> None:
    model = MyModel()
    model.key = uuid_key
    model.map_attr = MyMapAttr(value=diner_pb2.SHAKE_FLAVOR_VANILLA)
    model.save()

    # verify deserialization
    model = MyModel.get(uuid_key)
    assert model.map_attr.value == diner_pb2.SHAKE_FLAVOR_VANILLA
