"""EXCEPTIONS
Exception manager for Bus and Stop getters, returning custom exceptions depending on the response returned by the API.
"""

# # Native # #
import contextlib

# # Installed # #
import httpx

# # Project # #
from vigobusbot.exceptions import StopNotExist, GetterAPIException, GetterInternalException, GetterTimedOut

__all__ = ("manage_stop_exceptions", "TimeoutExceptions")

TimeoutExceptions = (TimeoutError, httpx.Timeout)


@contextlib.contextmanager
def manage_stop_exceptions(stop_id: int):
    # noinspection PyBroadException
    try:
        yield

    except TimeoutExceptions:
        raise GetterTimedOut()

    except httpx.HTTPError as ex:
        response = ex.response
        code = response.status_code
        if code == 404:
            raise StopNotExist(stop_id)
        else:
            raise GetterAPIException(ex)

    except Exception as ex:
        raise GetterInternalException(ex)
