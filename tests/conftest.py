import pytest


@pytest.fixture
def uuid_key():
    from uuid import uuid4

    return str(uuid4())
