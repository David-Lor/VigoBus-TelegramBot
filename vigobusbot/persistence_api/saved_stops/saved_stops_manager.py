"""SAVED STOPS MANAGER
Functions to interact with the Persistence API and read, save or delete Saved Stops.
The persisted stop data is encoded/decoded as following:
- User ID encoded using encode_user_id() -> str
- Stop ID saved as raw -> int
- Stop Name encoded/decoded on encode_stop()/decode_stop()
"""

# # Native # #
import json
import contextlib
from typing import Optional

# # Package # #
from vigobusbot.persistence_api.saved_stops.entities import SavedStop, SavedStops, SavedStopEncoded
from vigobusbot.persistence_api.saved_stops.services import *

# # Project # #
from vigobusbot.persistence_api.requester import http_request, Methods
from vigobusbot.logger import logger

__all__ = ("get_user_saved_stops", "get_stop", "save_stop", "delete_stop", "is_stop_saved", "delete_all_stops")


async def get_user_saved_stops(user_id: int) -> SavedStops:
    encoded_user_id = encode_user_id(user_id)

    result = await http_request(
        method=Methods.GET,
        endpoint=f"/stops/{encoded_user_id}"
    )
    stops_json = json.loads(result.text)
    logger.debug(f"Read {len(stops_json)} Saved Stops of user {user_id}")

    return [
        decode_stop(encoded_stop=SavedStopEncoded(**stop_json, user_id=str(user_id)), user_id=user_id)
        for stop_json in stops_json
    ]


async def get_stop(user_id: int, stop_id: int) -> Optional[SavedStop]:
    saved_stops = await get_user_saved_stops(user_id)
    with contextlib.suppress(StopIteration):
        return next(saved_stop for saved_stop in saved_stops if saved_stop.stop_id == stop_id)


async def is_stop_saved(user_id: int, stop_id: int) -> bool:
    saved_stop = await get_stop(user_id=user_id, stop_id=stop_id)
    return bool(saved_stop)


async def save_stop(user_id: int, stop_id: int, stop_name: Optional[str] = None):
    stop = SavedStop(
        user_id=user_id,
        stop_id=stop_id,
        stop_name=stop_name
    )
    stop_encoded = encode_stop(raw_stop=stop, user_id=user_id)

    await http_request(
        method=Methods.POST,
        endpoint="/stops",
        body=stop_encoded.dict()
    )
    logger.debug(f"Saved/Updated Stop for user {user_id}")


async def delete_stop(user_id: int, stop_id: int):
    encoded_user_id = encode_user_id(user_id)

    await http_request(
        method=Methods.DELETE,
        endpoint=f"/stops/{encoded_user_id}/{stop_id}"
    )
    logger.debug(f"Deleted Stop for user {user_id}")


async def delete_all_stops(user_id: int):
    encoded_user_id = encode_user_id(user_id)

    await http_request(
        method=Methods.DELETE,
        endpoint=f"/stops/{encoded_user_id}"
    )
    logger.debug(f"Deleted ALL Stops for user {user_id}")
