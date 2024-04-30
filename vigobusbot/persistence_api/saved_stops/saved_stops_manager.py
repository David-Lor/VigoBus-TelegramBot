"""SAVED STOPS MANAGER
Functions to interact with the Persistence API and read, save or delete Saved Stops.
The persisted stop data is encoded/decoded as following:
- User ID encoded using encode_user_id() -> str
- Stop ID saved as raw -> int
- Stop Name encoded/decoded on encode_stop()/decode_stop()
"""

from typing import Optional, List

from vigobusbot.persistence import SavedUserStopsRepository
from vigobusbot.models import SavedUserStop
from vigobusbot.logger import logger

__all__ = ("get_user_saved_stops", "get_stop", "save_stop", "delete_stop", "is_stop_saved", "delete_all_stops")


# TODO Migrate methods to other service


async def get_user_saved_stops(user_id: int) -> List[SavedUserStop]:
    return await SavedUserStopsRepository.get_repository().get_user_all_stops(user_id)


async def get_stop(user_id: int, stop_id: int) -> Optional[SavedUserStop]:
    return await SavedUserStopsRepository.get_repository().get_user_single_stop(user_id, stop_id)


async def is_stop_saved(user_id: int, stop_id: int) -> bool:
    return await SavedUserStopsRepository.get_repository().get_user_single_stop(user_id=user_id, stop_id=stop_id, return_existence=True)


async def save_stop(user_id: int, stop_id: int, stop_name: Optional[str] = None):
    stop = SavedUserStop(
        stop_id=stop_id,
        user_id=user_id,
        stop_name=stop_name,
    )
    await SavedUserStopsRepository.get_repository().save_user_stop(stop)


async def delete_stop(user_id: int, stop_id: int):
    await SavedUserStopsRepository.get_repository().delete_user_single_stop(user_id=user_id, stop_id=stop_id)


async def delete_all_stops(user_id: int):
    await SavedUserStopsRepository.get_repository().delete_user_all_stops(user_id)
