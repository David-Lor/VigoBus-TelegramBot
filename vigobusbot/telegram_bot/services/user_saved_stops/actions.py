"""USER SAVED STOPS - Actions
Frontend for actions to interact with user saved stops
"""

# # Native # #
import asyncio
from typing import Optional

# # Project # #
from vigobusbot.services import mongo
from vigobusbot import vigobus_api

# # Packaged # #
from .models import *

__all__ = ("get_all_stops", "get_stop", "is_stop_saved", "save_stop", "delete_stop", "delete_all_stops")


async def get_all_stops(user_id: int) -> UserStopsRead:
    with mongo.user_stops() as collection:
        # noinspection PyTypeChecker
        documents = list(await collection.find(UserStopFilter(user_id=user_id)))
        real_stops = await asyncio.gather(*[vigobus_api.get_stop(stop_id=doc["stop_id"]) for doc in documents])
        return [
            UserStopRead(**{
                **document,
                "stop_original_name": real_stop.name
            })
            for document, real_stop in zip(documents, real_stops)
        ]


async def get_stop(user_id: int, stop_id: int) -> UserStopRead:
    with mongo.user_stops() as collection:
        # noinspection PyTypeChecker
        document, real_stop = await asyncio.gather(
            collection.find_one(UserStopFilter(user_id=user_id, stop_id=stop_id).filter()),
            vigobus_api.get_stop(stop_id=stop_id)
        )
        return UserStopRead(**{
            **document,
            "stop_original_name": real_stop.name
        })


async def is_stop_saved(user_id: int, stop_id: int):
    # TODO custom query
    saved_stop = await get_stop(user_id=user_id, stop_id=stop_id)
    return bool(saved_stop)


async def save_stop(user_id: int, stop_id: int, stop_name: Optional[str] = None):
    # noinspection PyTypeChecker
    create = UserStopCreate(
        stop_id=stop_id,
        user_id=user_id,
        stop_custom_name=stop_name
    )
    with mongo.user_stops() as collection:
        await collection.insert_one(create.dict())


async def delete_stop(user_id: int, stop_id: int):
    with mongo.user_stops() as collection:
        # noinspection PyTypeChecker
        result = await collection.delete_one(UserStopFilter(user_id=user_id, stop_id=stop_id).filter())


async def delete_all_stops(user_id: int):
    with mongo.user_stops() as collection:
        # noinspection PyTypeChecker
        result = await collection.delete_many(UserStopFilter(user_id=user_id).filter())
        read_stops = await get_all_stops(user_id=user_id)
        assert not read_stops
