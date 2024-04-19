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

TimeoutExceptions = (TimeoutError, httpx.TimeoutException)


@contextlib.contextmanager
def manage_stop_exceptions(stop_id: int):
    # noinspection PyBroadException
    try:
        yield

    except TimeoutExceptions:
        raise GetterTimedOut()

    except httpx.HTTPError as ex:
        # noinspection PyUnresolvedReferences
        response: httpx.Response = ex.response
        if response.status_code == 404 and "Stop not exists" in response.text:
            raise StopNotExist(stop_id)
        else:
            raise GetterAPIException(ex)

    except Exception as ex:
        raise GetterInternalException(ex)
