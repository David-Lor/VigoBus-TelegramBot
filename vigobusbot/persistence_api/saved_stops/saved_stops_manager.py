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

__all__ = ("get_user_saved_stops", "save_stop", "delete_stop")


async def get_user_saved_stops(user_id: int) -> SavedStops:
    result = await http_request(
        method=GET,
        # endpoint=f"/stops/{generate_user_hash(user_id)}"
        endpoint=f"/stops/{user_id}"
    )
    stops_json = json.loads(result.text)
    # return [SavedStopEncoded(**stop_json).decode(user_id) for stop_json in stops_json]
    return [SavedStopDecoded(**stop_json) for stop_json in stops_json]


async def save_stop(user_id: int, stop_id: int, stop_name: Optional[str] = None):
    stop = SavedStopDecoded(
        user_id=user_id,
        stop_id=stop_id,
        stop_name=stop_name
    )
    await http_request(
        method=POST,
        endpoint="/stops",
        # body=dict(stop.encode())
        body=dict(stop)
    )


async def delete_stop(user_id: int, stop_id: int):
    await http_request(
        method=DELETE,
        endpoint=f"/stops/{user_id}/{stop_id}"
    )
