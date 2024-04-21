"""UTILS
Misc general utils/helpers
"""

from uuid import uuid4
from time import time
from typing import Type, TypeVar, Generic, Optional

T = TypeVar('T')


def get_time(float_precision: bool = False):
    """Return current time as Unix/Epoch timestamp, seconds precision (unless float_precision is True)"""
    return time() if float_precision else int(time())


def get_uuid():
    """Return an unique UUID4"""
    return str(uuid4())


class Singleton:
    """Inheritable class that holds a single variable (an instance of the same class),
    intended to be accessed as a singleton without initialization."""
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


class SingletonHold(Generic[T]):
    """Object that holds a single variable, intended to be initialized on a global context
    and accessed as a singleton.
    """
    _instance = None

    def set_value(self, value: T):
        self._instance = value

    def get_value(self) -> Optional[T]:
        return self._instance
