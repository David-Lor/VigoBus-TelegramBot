"""REQUESTER
Helpers to request the HTTP Persistence API
"""

# # Native # #
import urllib.parse

# # Installed # #
import httpx

# # Project # #
from ..settings_handler import persistence_settings as settings
from ..logger import *

__all__ = ("http_request", "GET", "POST", "DELETE")


GET = "GET"
POST = "POST"
DELETE = "DELETE"


async def http_request(
        method, endpoint, query_params=None, body=None, timeout=settings.timeout, retries=settings.retries
) -> httpx.AsyncResponse:
    last_ex = None
    url = urllib.parse.urljoin(settings.url, endpoint)

    for retry_count in range(retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
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
            logger.warning(f"Request on {method} {url} timed out (retries: {retry_count+1}/{retries})")
            last_ex = ex

        except Exception as ex:
            logger.warning(f"Request on {method} {url} failed: {ex}")
            raise ex

    raise last_ex
