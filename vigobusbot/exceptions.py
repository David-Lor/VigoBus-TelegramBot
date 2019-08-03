"""EXCEPTIONS
Custom and imported exceptions used over all the project.
"""

# # Installed # #
from pybusent import StopNotExist

__all__ = ("GetterException", "GetterInternalException", "GetterAPIException", "GetterTimedOut", "StopNotExist")


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
