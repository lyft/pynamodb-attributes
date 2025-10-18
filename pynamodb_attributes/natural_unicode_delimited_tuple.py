from datetime import datetime
from typing import List, get_type_hints

from pynamodb_attributes.unicode_delimited_tuple import (
    T,
    UnicodeDelimitedTupleAttribute,
)


class NaturalUnicodeDelimitedTupleAttribute(UnicodeDelimitedTupleAttribute):
    """This class extends the UnicodeDelimitedTupleAttribute by checking if there are
    any numeric types being stored within the tuple and zero fills them to ensure
    natural sorting of those numbers in DynamoDB query results. This also adds datetime
    object handling.
    """

    def __init__(self, *args, zero_fill=4, **kwargs):
        """Set the amount of zero fill to add to numbers when converted to strings."""
        super().__init__(*args, **kwargs)
        self.zero_fill = zero_fill

    def deserialize(self, value: str) -> T:
        """This overrides the superclass deserialize so that datetimes are properly
        deserialized.
        """
        field_types = get_type_hints(self.tuple_type)

        if field_types:
            values = value.split(self.delimiter, maxsplit=len(field_types))

            tuple_args = {}
            for (field_name, field_type), field_value in zip(
                field_types.items(), values
            ):
                if issubclass(field_type, datetime):
                    tuple_args[field_name] = field_type.fromisoformat(field_value)
                else:
                    tuple_args[field_name] = field_type(field_value)

            return self.tuple_type(**tuple_args)

        return self.tuple_type(value.split(self.delimiter))

    def serialize(self, value: T) -> str:
        """This overrides the superclass serialize so that int or float values are
        left padded to the specified width with 0s. This also adds proper serialization
        of datetimes to isoformat.
        """
        if not isinstance(value, self.tuple_type):
            raise TypeError(
                f"value has invalid type '{type(value)}'; expected '{self.tuple_type}'"
            )

        values: List[T] = list(value)
        while values and values[-1] is None:
            del values[-1]

        strings = []
        for e in values:
            if isinstance(e, (int, float)):
                strings.append(str(e).zfill(self.zero_fill))
            elif isinstance(e, datetime):
                strings.append(e.isoformat())
            else:
                strings.append(str(e))

        if any(self.delimiter in s for s in strings):
            raise ValueError(
                f"Tuple elements may not contain delimiter '{self.delimiter}'"
            )

        return self.delimiter.join(strings)
