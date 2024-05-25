"""UTILS
Misc general utils/helpers
"""

import json
import datetime
import asyncio
from uuid import uuid4
from time import time
from typing import Type, TypeVar, Generic, Optional

import pydantic

__all__ = [
    "json", "get_time", "get_datetime", "get_uuid", "jsonable_dict", "async_noop", "async_gather_limited",
    "Singleton", "SingletonHold", "SetupTeardown",
    "Type", "TypeVar", "T"
]

T = TypeVar('T')


def get_time(float_precision: bool = False):
    """Return current time as Unix/Epoch timestamp, UTC, seconds precision (unless float_precision is True)"""
    return time() if float_precision else int(time())


def get_datetime():
    """Return current time as datetime object UTC"""
    return datetime.datetime.now(tz=datetime.timezone.utc)


def get_uuid():
    """Return an unique UUID4"""
    return str(uuid4())


def jsonable_dict(obj: pydantic.BaseModel, **kwargs):
    """Convert a pydantic object to dict, but using native JSON data types."""
    # TODO Use ujson lib, or other way of converting (iterating dict and converting values? if faster)
    d = obj.json(**kwargs)
    return json.loads(d)


# noinspection PyUnusedLocal
async def async_noop(*args, **kwargs):
    """Async function that does nothing on purpose.
    """
    pass


async def async_gather_limited(*coros, limit: int):
    """Similar to asyncio.gather, but limiting concurrency to `limit` parallel coroutines.
    """
    semaphore = asyncio.Semaphore(limit)

    async def sem_coro(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coros))


class Singleton:
    """Inheritable class that holds a single variable (an instance of the same class),
    intended to be accessed as a singleton without initialization."""
    _instance: T = None

    @classmethod
    def get_instance(cls: Type[T], initialize: bool = False) -> T:
        if initialize and not cls._instance:
            return cls().set_current_as_singleton()

        # noinspection PyUnresolvedReferences
        return cls._instance

    @classmethod
    def set_instance(cls: Type[T], instance: T):
        cls._instance = instance

    def set_current_as_singleton(self: T) -> T:
        self.__class__.set_instance(self)
        return self.get_instance()

    @classmethod
    def get_class_name(cls):
        return cls.__name__


class SingletonHold(Generic[T]):
    """Object that holds a single variable, intended to be initialized on a global context
    and accessed as a singleton.
    """
    _instance = None

    def set_value(self, value: T):
        self._instance = value

    def get_value(self) -> Optional[T]:
        return self._instance


class SetupTeardown:
    """Base class with two async methods, setup & teardown.
    """

    async def setup(self):
        pass

    async def teardown(self):
        pass
