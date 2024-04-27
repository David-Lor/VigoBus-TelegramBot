"""UTILS
Misc general utils/helpers
"""

import datetime
from uuid import uuid4
from time import time
from typing import Type, TypeVar, Generic, Optional

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
