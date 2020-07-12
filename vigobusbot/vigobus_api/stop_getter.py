"""STOP GETTER
Get Stop information using the API
"""

# # Native # #
import json
import asyncio
from typing import Union

# # Package # #
from .requester import http_get
from .exceptions import manage_stop_exceptions

# # Project # #
from vigobusbot.entities import Stop, Stops, StopsDict
from ..persistence_api.saved_stops.entities import *

__all__ = ("get_stop", "get_multiple_stops", "search_stops_by_name", "fill_saved_stops_info")


async def get_stop(stop_id: int) -> Stop:
    with manage_stop_exceptions(stop_id):
        result = await http_get(endpoint=f"/stop/{stop_id}")
        stop = Stop(**result.json())
        return stop


async def get_multiple_stops(*stops_ids: int, return_dict: bool = False) -> Union[Stops, StopsDict]:
    result: Stops = await asyncio.gather(
        *[get_stop(stop_id) for stop_id in stops_ids]
    )

    if return_dict:
        return {stop.stop_id: stop for stop in result}
    else:
        return result


async def search_stops_by_name(search_term: str) -> Stops:
    result = await http_get(endpoint="/stops", query_params={"stop_name": search_term, "limit": 50})
    return [Stop(**single_result) for single_result in result.json()]


async def fill_saved_stops_info(saved_stops: SavedStops) -> SavedStops:
    """Given multiple SavedStops read from database, modify these SavedStops in-place with the remaining stop info
    (the original stop name) that is not persisted on DB, but on the Bus API.
    """
    real_stops: StopsDict = await get_multiple_stops(*[stop.stop_id for stop in saved_stops], return_dict=True)

    for saved_stop in saved_stops:
        real_stop = real_stops[saved_stop.stop_id]
        saved_stop.stop_original_name = real_stop.name

    return saved_stops
