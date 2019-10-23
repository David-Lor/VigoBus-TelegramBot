"""REQUESTER
Helpers to request the HTTP Persistence API
"""

# # Native # #
import urllib.parse

# # Installed # #
import httpx

# # Project # #
from ..settings_handler import persistence_settings as settings

__all__ = ("http_request", "GET", "POST", "DELETE")


GET = 0
POST = 1
DELETE = 2


async def http_request(
        method, endpoint, query_params=None, body=None, timeout=settings.timeout, retries=settings.retries
) -> httpx.AsyncResponse:
    last_ex = None

    for _ in range(retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                url = urllib.parse.urljoin(settings.url, endpoint)
                if method == GET:
                    result = await client.get(url=url, params=query_params)
                elif method == POST:
                    result = await client.post(url=url, params=query_params, json=body)
                elif method == DELETE:
                    result = await client.delete(url=url, params=query_params)

            result.raise_for_status()
            result.encoding = "utf-8"
            return result

        except httpx.Timeout as ex:
            last_ex = ex

    raise last_ex
