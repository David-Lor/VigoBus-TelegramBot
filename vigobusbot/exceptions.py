"""EXCEPTIONS
Custom and imported exceptions used over all the project.
"""

# # Installed # #
from aiogram.utils.exceptions import *

__all__ = (
    "GetterException", "GetterInternalException", "GetterAPIException", "GetterTimedOut", "StopNotExist",
    "MessageNotModified", "UserRateLimit"
)


class StopNotExist(Exception):
    """A Stop does not exist in reality, as specified by the API"""
    pass


class GetterException(Exception):
    """A Stop/Bus Getter failed (base Getter Exception)"""
    pass


class GetterInternalException(GetterException):
    """A Stop/Bus Getter failed by an unspecified reason"""
    pass


class GetterAPIException(GetterInternalException):
    """A Stop/Bus API endpoint returned an Internal exception"""
    pass


class GetterTimedOut(TimeoutError, GetterException):
    """A Stop/Bus Getter failed due to a timeout"""
    pass


class UserRateLimit(Exception):
    """A user exceeded the request rate limit of the bot"""
    pass
