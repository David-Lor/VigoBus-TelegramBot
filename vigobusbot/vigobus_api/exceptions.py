"""EXCEPTIONS
Exception manager for Bus and Stop getters, returning PyBusEnt exceptions depending on the response returned by the API.
"""

# # Native # #
import contextlib
import asyncio

# # Installed # #
import requests_async as requests

# # Project # #
from ..exceptions import *

__all__ = ("manage_exceptions", "TimeoutExceptions")

TimeoutExceptions = (TimeoutError, requests.Timeout, asyncio.TimeoutError)


@contextlib.contextmanager
def manage_exceptions(stop_id: int):
    # noinspection PyBroadException
    try:
        yield

    except TimeoutExceptions:
        raise GetterTimedOut()

    except requests.HTTPError as ex:
        response: requests.Response = ex.response
        code = response.status_code
        if code == 404:
            raise StopNotExist(stop_id)
        else:
            raise GetterAPIException(ex)

    except Exception as ex:
        raise GetterInternalException(ex)
