"""UTILS
Misc general utils/helpers
"""

import datetime
from uuid import uuid4
from time import time


def get_time(float_precision: bool = False):
    """Return current time as Unix/Epoch timestamp, seconds precision (unless float_precision is True)"""
    return time() if float_precision else int(time())


def get_datetime_now_utc():
    return datetime.datetime.now(tz=datetime.timezone.utc)


def get_uuid():
    """Return an unique UUID4"""
    return str(uuid4())
