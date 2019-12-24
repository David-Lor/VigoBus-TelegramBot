"""STOP GETTER
Get Stop information using the API
"""

# # Native # #
import json
import asyncio
from typing import Union

# # Package # #
from .requester import http_get
from .exceptions import manage_exceptions

# # Project # #
from ..entities import *

__all__ = ("get_stop", "get_multiple_stops")


async def get_stop(stop_id: int) -> Stop:
    with manage_exceptions(stop_id):
        result = await http_get(endpoint=f"/stop/{stop_id}")
        data = json.loads(result.text)
        stop = Stop(**data)
        return stop


async def get_multiple_stops(*stops_ids: int, return_dict: bool = False) -> Union[Stops, StopsDict]:
    result: Stops = await asyncio.gather(
        *[get_stop(stop_id) for stop_id in stops_ids]
    )

    if return_dict:
        return {stop.stop_id: stop for stop in result}
    else:
        return result
