"""SAVED STOPS MANAGER
Functions to interact with the Persistence API and read, save or delete Saved Stops
"""

# # Native # #
import json
from typing import Optional

# # Package # #
from .entities import *
# from .key_generator import *
from ..requester import *

# # Project # #
from ...logger import *

__all__ = ("get_user_saved_stops", "get_stop", "save_stop", "delete_stop", "is_stop_saved")


async def get_user_saved_stops(user_id: int) -> SavedStops:
    result = await http_request(
        method=GET,
        # endpoint=f"/stops/{generate_user_hash(user_id)}"
        endpoint=f"/stops/{user_id}"
    )
    stops_json = json.loads(result.text)
    logger.debug(f"Read {len(stops_json)} Saved Stops of user {user_id}")
    return [SavedStopDecoded(**stop_json) for stop_json in stops_json]


async def get_stop(user_id: int, stop_id: int) -> Optional[SavedStopBase]:
    saved_stops = await get_user_saved_stops(user_id)
    try:
        return next(saved_stop for saved_stop in saved_stops if saved_stop.stop_id == stop_id)
    except StopIteration:
        return None


async def is_stop_saved(user_id: int, stop_id: int) -> bool:
    saved_stop = await get_stop(user_id=user_id, stop_id=stop_id)
    return bool(saved_stop)


async def save_stop(user_id: int, stop_id: int, stop_name: Optional[str] = None):
    stop = SavedStopDecoded(
        user_id=user_id,
        stop_id=stop_id,
        stop_name=stop_name
    )
    await http_request(
        method=POST,
        endpoint="/stops",
        body=dict(stop)
    )
    logger.debug(f"Saved/Updated Stop for user {user_id}")


async def delete_stop(user_id: int, stop_id: int):
    await http_request(
        method=DELETE,
        endpoint=f"/stops/{user_id}/{stop_id}"
    )
    logger.debug(f"Deleted Stop for user {user_id}")
