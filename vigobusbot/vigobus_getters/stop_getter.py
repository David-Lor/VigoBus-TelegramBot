"""STOP GETTER
Get Stop information using the API
"""

# # Native # #
import json

# # Package # #
from .requester import http_get
from .exceptions import manage_exceptions

# # Project # #
from ..entities import Stop

__all__ = ("get_stop",)


async def get_stop(stop_id: int) -> Stop:
    with manage_exceptions():
        result = await http_get(endpoint=f"/stop/{stop_id}")
        data = json.loads(result.text)
        stop = Stop(**data)
        return stop
