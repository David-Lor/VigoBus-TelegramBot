"""UTILS
Misc general utils/helpers
"""

import datetime
from uuid import uuid4
from time import time
from typing import Type, TypeVar

T = TypeVar('T')


def get_time(float_precision: bool = False):
    """Return current time as Unix/Epoch timestamp, seconds precision (unless float_precision is True)"""
    return time() if float_precision else int(time())


def get_datetime_now_utc():
    return datetime.datetime.now(tz=datetime.timezone.utc)


def get_uuid():
    """Return an unique UUID4"""
    return str(uuid4())


class Singleton:
    _instance: T = None

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        # noinspection PyUnresolvedReferences
        return cls._instance

    @classmethod
    def set_instance(cls: Type[T], instance: T):
        cls._instance = instance

    def set_current_as_singleton(self: T) -> T:
        self.__class__.set_instance(self)
        return self.get_instance()
