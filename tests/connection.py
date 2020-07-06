from typing import Type

from pynamodb.connection.table import TableConnection
from pynamodb.models import Model


def _connection(model: Type[Model]) -> TableConnection:
    # pynamodb typestubs don't have private attrs
    return model._get_connection()  # type: ignore
