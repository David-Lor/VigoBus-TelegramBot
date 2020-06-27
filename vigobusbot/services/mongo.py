"""MONGO SERVICE
Low level utils for Mongo interaction
"""

# # Native # #
import asyncio
from contextlib import asynccontextmanager
from typing import ContextManager

# # Installed # #
from motor import motor_asyncio
from pymongo.collection import Collection, Cursor

# # Project # #
from vigobusbot.settings_handler import mongo_settings

__all__ = (
    "get_collection", "get_logs_collection", "get_user_saved_stops_collection", "user_stops",
    "Collection", "Cursor"
)


def get_collection(collection: str, loop: asyncio.AbstractEventLoop) -> Collection:
    client = motor_asyncio.AsyncIOMotorClient(mongo_settings.uri, io_loop=loop)
    return client[mongo_settings.database][collection]


def get_logs_collection(loop: asyncio.AbstractEventLoop) -> Collection:
    return get_collection(mongo_settings.collection_logs, loop)


def get_user_saved_stops_collection(loop: asyncio.AbstractEventLoop) -> Collection:
    return get_collection(mongo_settings.collection_user_stops, loop)


@asynccontextmanager
async def collection_context(collection: str) -> ContextManager[Collection]:
    yield get_collection(collection=collection, loop=asyncio.get_event_loop())


user_stops = lambda: collection_context(mongo_settings.collection_user_stops)
