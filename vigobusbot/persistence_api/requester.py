"""REQUESTER
Helpers to request the HTTP Persistence API
"""

# # Native # #
import asyncio
import urllib.parse

# # Installed # #
import requests_async as requests

# # Project # #
from ..settings_handler import persistence_settings as settings

__all__ = ("http_request", "GET", "POST", "DELETE")


GET = requests.get
POST = requests.post
DELETE = requests.delete


async def http_request(method, endpoint, query_params=None, body=None, timeout=settings.timeout) -> requests.Response:
    result: requests.Response = await asyncio.wait_for(
        method(
            url=urllib.parse.urljoin(settings.url, endpoint),
            params=query_params,
            json=body
        ),
        timeout=timeout
    )
    result.raise_for_status()
    result.encoding = "utf-8"
    return result
