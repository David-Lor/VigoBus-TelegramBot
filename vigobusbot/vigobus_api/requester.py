"""REQUESTER
Helpers to request HTTP sources
"""

# # Native # #
import urllib.parse

# # Installed # #
import httpx

# # Project # #
from ..settings_handler import api_settings as settings

__all__ = ("http_get",)


async def http_get(
        endpoint, query_params=None, timeout=settings.timeout, retries=settings.retries
) -> httpx.AsyncResponse:
    last_ex = None

    for _ in range(retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                result = await client.get(
                    url=urllib.parse.urljoin(settings.url, endpoint),
                    params=query_params
                )

            result.raise_for_status()
            result.encoding = "utf-8"
            return result

        except httpx.Timeout as ex:
            last_ex = ex

    raise last_ex
