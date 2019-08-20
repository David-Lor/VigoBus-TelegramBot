"""REQUESTER
Helpers to request HTTP sources
"""

# # Native # #
import asyncio
import urllib.parse

# # Installed # #
import requests_async as requests

# # Project # #
from ..settings_handler import api_settings as settings

__all__ = ("http_get",)


async def http_get(endpoint, query_params=None, body=None, timeout=settings.timeout) -> requests.Response:
    result: requests.Response = await asyncio.wait_for(
        requests.get(
            url=urllib.parse.urljoin(settings.url, endpoint),
            params=query_params,
            json=body
        ),
        timeout=timeout
    )
    result.raise_for_status()
    result.encoding = "utf-8"
    return result
