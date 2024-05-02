"""STOP GETTER
Get Stop information using the API
"""

import asyncio
from typing import Union, List

from vigobusbot.persistence import StopsRepository
from vigobusbot.models import SavedUserStop, Stop, StopsDict
from vigobusbot.exceptions import StopNotExist

__all__ = ("get_stop", "get_multiple_stops", "search_stops_by_name", "fill_saved_stops_info")


async def get_stop(stop_id: int) -> Stop:
    stop = await StopsRepository.get_repository().get_stop_by_id(stop_id)
    if not stop:
        raise StopNotExist
    return stop


async def get_multiple_stops(*stops_ids: int, return_dict: bool = False) -> Union[List[Stop], StopsDict]:
    # noinspection PyTypeChecker
    stops: List[Stop] = await asyncio.gather(
        *[get_stop(stop_id) for stop_id in stops_ids]
    )

    # Remove None values
    stops = [stop for stop in stops if stop]

    if return_dict:
        return {stop.id: stop for stop in stops}
    else:
        return stops


async def search_stops_by_name(search_term: str) -> List[Stop]:
    # TODO ...
    return []


async def fill_saved_stops_info(saved_stops: List[SavedUserStop]):
    """Given multiple SavedStops read from database, modify these SavedStops in-place with the remaining stop info
    (the original stop name) that is not persisted on DB, but on the Bus API.
    """
    real_stops: StopsDict = await get_multiple_stops(*[stop.stop_id for stop in saved_stops], return_dict=True)

    for saved_stop in saved_stops:
        real_stop = real_stops[saved_stop.stop_id]
        saved_stop.stop = real_stop
