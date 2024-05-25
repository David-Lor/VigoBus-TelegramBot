"""STOP GETTER
Get Stop information using the API
"""

import asyncio
from typing import Union, List, Optional

from vigobusbot.persistence import StopsRepository
from vigobusbot.models import SavedUserStop, Stop, StopsDict
from vigobusbot.exceptions import StopNotExist

__all__ = ("get_stop", "get_multiple_stops", "search_stops_by_name", "fill_saved_stops_info")


async def get_stop(stop_id: int, raise_if_not_found: bool = True) -> Optional[Stop]:
    """Get a single stop by id. When the stop is not found: if raise_if_not_found=True raise StopNotExist;
    if raise_if_not_found=False return None.
    """
    stop = await StopsRepository.get_repository().get_stop_by_id(stop_id)
    if not stop and raise_if_not_found:
        raise StopNotExist
    return stop


async def get_multiple_stops(*stops_ids: int, return_dict: bool = False) -> Union[List[Stop], StopsDict]:
    # noinspection PyTypeChecker
    stops: List[Stop] = await asyncio.gather(
        *[get_stop(stop_id, raise_if_not_found=False) for stop_id in stops_ids]
    )

    # Remove None values
    stops = [stop for stop in stops if stop]

    if return_dict:
        return {stop.id: stop for stop in stops}
    else:
        return stops


async def search_stops_by_name(search_term: str) -> List[Stop]:
    return await StopsRepository.get_repository().search_stops_by_name(search_term)


async def fill_saved_stops_info(saved_stops: List[SavedUserStop]):
    """Given multiple SavedStops read from database, modify these SavedStops in-place with the remaining stop info
    (the original stop name) that is not persisted on DB, but on the Bus API.
    If a stop is not found, remove it from the list.
    """
    real_stops: StopsDict = await get_multiple_stops(*[stop.stop_id for stop in saved_stops], return_dict=True)

    for saved_stop in list(saved_stops):
        real_stop = real_stops.get(saved_stop.stop_id)
        if real_stop:
            saved_stop.stop = real_stop
        else:
            saved_stops.remove(saved_stop)
