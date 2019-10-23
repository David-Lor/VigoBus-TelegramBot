"""EXCEPTIONS
Exception manager for Bus and Stop getters, returning PyBusEnt exceptions depending on the response returned by the API.
"""

# # Native # #
import contextlib

# # Installed # #
import httpx

# # Project # #
from ..exceptions import *

__all__ = ("manage_exceptions", "TimeoutExceptions")

TimeoutExceptions = (TimeoutError, httpx.Timeout)


@contextlib.contextmanager
def manage_exceptions():
    # noinspection PyBroadException
    try:
        yield
    except TimeoutExceptions:
        raise GetterTimedOut()
    except httpx.HTTPError as ex:
        response: httpx.AsyncResponse = ex.response
        code = response.status_code
        if code == 404:
            raise StopNotExist()
        else:
            raise GetterAPIException()
    except Exception:
        raise GetterInternalException()
