"""MONGO SERVICE
Low level utils for Mongo interaction
"""

# # Native # #
import asyncio

# # Installed # #
from motor import motor_asyncio
from pymongo.collection import Collection

# # Project # #
from vigobusbot.settings_handler import mongo_settings

__all__ = ("get_collection", "get_logs_collection")


def get_collection(collection: str, loop: asyncio.AbstractEventLoop) -> Collection:
    client = motor_asyncio.AsyncIOMotorClient(mongo_settings.uri, io_loop=loop)
    return client[mongo_settings.database][collection]


def get_logs_collection(loop: asyncio.AbstractEventLoop) -> Collection:
    return get_collection(mongo_settings.collection_logs, loop)
