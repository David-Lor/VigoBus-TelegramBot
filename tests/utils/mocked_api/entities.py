"""TESTS - UTILS - MOCKED API - ENTITIES
Entities used by the Mocked API
"""

# # Native # #
from typing import Union, Optional

# # Installed # #
from requests_async import Response, HTTPError

# # Project # #
from vigobusbot.entities import *

__all__ = (
    "StopOrException", "BusesOrException", "FakeResponse",
    "Response", "Stop", "Buses", "BusesAPIResponse", "HTTPError"
)

StopOrException = Union[Stop, Exception]
BusesOrException = Union[Buses, Exception]


class FakeResponse(Response):
    """Faked requests.Response class"""
    _text: str
    _status_code: int

    def __init__(self, text=None, status_code=None):
        super().__init__()
        if text is not None:
            self.text = text
        if status_code is not None:
            self.status_code = status_code
        else:
            self.status_code = 200

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @staticmethod
    def not_found(reason: Optional[str]) -> Response:
        response = FakeResponse()
        response.status_code = 404
        response.text = str({
            "detail": reason if reason else FakeResponse.NotFoundReasons.Generic
        })
        return response

    class NotFoundReasons:
        StopNotExist = "Stop not exists"
        Generic = "Not Found"


class BusesAPIResponse(BusesResponse):
    more_buses_available: int = 0
