This Python 3 library contains compound and high-level PynamoDB attributes:

- `FloatAttribute` – same as `NumberAttribute` but whose value is typed as `float`
- `IntegerAttribute` – same as `NumberAttribute` but whose value is typed as `int` (rather than `float`)
- `IntegerSetAttribute` – same as `NumberSetAttribute` but whose value is typed as `int` (rather than `float`)
- `UnicodeDelimitedTupleAttribute` - a delimiter-separated value, useful for storing composite keys
- `UnicodeEnumAttribute` - serializes a string-valued `Enum` into a Unicode (`S`-typed) attribute
- `UnicodeProtobufEnumAttribute` - serializes a Protobuf enum into a Unicode (`S`-typed) attribute
- `IntegerEnumAttribute` - serializes a int-valued `Enum` into a number (`N`-typed) attribute
- `TimedeltaAttribute`, `TimedeltaMsAttribute`, `TimedeltaUsAttribute` – serializes `timedelta`s as integer seconds, milliseconds (ms) or microseconds (µs)
- `TimestampAttribute`, `TimestampMsAttribute`, `TimestampUsAttribute` – serializes `datetime`s as Unix epoch seconds, milliseconds (ms) or microseconds (µs)
- `IntegerDateAttribute` - serializes `date` as an integer representing the Gregorian date (_e.g._ `20181231`)
- `UUIDAttribute` - serializes a `UUID` Python object as a `S` type attribute (_e.g._ `'a8098c1a-f86e-11da-bd1a-00112444be1e'`)
- `UnicodeDatetimeAttribute` - ISO8601 datetime strings with offset information

## Testing

The tests in this repository use an in-memory implementation of [`dynamodb`](https://aws.amazon.com/dynamodb). To run the tests locally, make sure [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) is running. It is available as a standalone binary, through package managers (e.g. [Homebrew](https://formulae.brew.sh/cask/dynamodb-local)) or as a Docker container:
```shell
docker run -d -p 8000:8000 amazon/dynamodb-local
```

Afterwards, run tests as usual:
```shell
pytest tests
```
