"""UTILS
Misc general utils/helpers
"""

# # Native # #
from uuid import uuid4
from time import time

__all__ = ("get_time", "get_uuid")


def get_time(float_precision: bool = False):
    """Return current time as Unix/Epoch timestamp, seconds precision (unless float_precision is True)"""
    return time() if float_precision else int(time())


def get_uuid():
    """Return an unique UUID4"""
    return str(uuid4())
