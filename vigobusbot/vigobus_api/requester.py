"""REQUESTER
Helpers to request HTTP sources
"""

# # Native # #
import urllib.parse

# # Installed # #
import httpx

# # Project # #
from ..settings_handler import api_settings as settings
from ..logger import *

__all__ = ("http_get",)


async def http_get(
        endpoint, query_params=None, timeout=settings.timeout, retries=settings.retries
) -> httpx.AsyncResponse:
    last_ex = None
    url = urllib.parse.urljoin(settings.url, endpoint)

    for retry_count in range(retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                result = await client.get(url=url, params=query_params)

            result.raise_for_status()
            result.encoding = "utf-8"
            return result

        except httpx.Timeout as ex:
            logger.warning(f"Request on {url} timed out (retries: {retry_count+1}/{retries})")
            last_ex = ex

        except Exception as ex:
            logger.warning(f"Request on {url} failed: {ex}")
            raise ex

    raise last_ex
