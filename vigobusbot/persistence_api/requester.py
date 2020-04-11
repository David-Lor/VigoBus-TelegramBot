"""REQUESTER
Helpers to request the HTTP Persistence API
"""

# # Native # #
import urllib.parse
from typing import Optional

# # Installed # #
import httpx

# # Project # #
from vigobusbot.settings_handler import persistence_settings as settings
from vigobusbot.logger import logger

__all__ = ("http_request", "Methods")


class Methods:
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


async def http_request(
        method, endpoint,
        query_params: Optional[dict] = None, body: Optional[dict] = None,
        timeout=settings.timeout, retries=settings.retries
) -> httpx.AsyncResponse:
    last_ex = None
    url = urllib.parse.urljoin(settings.url, endpoint)

    for retry_count in range(retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method == Methods.GET:
                    result = await client.get(url=url, params=query_params)
                elif method == Methods.POST:
                    result = await client.post(url=url, params=query_params, json=body)
                elif method == Methods.DELETE:
                    result = await client.delete(url=url, params=query_params)

            result.raise_for_status()
            result.encoding = "utf-8"
            return result

        except httpx.Timeout as ex:
            logger.warning(f"Request on {method} {url} timed out (retries: {retry_count+1}/{retries})")
            last_ex = ex

        except httpx.HTTPError as ex:
            body_log = f" - Body: \n{ex.response.content.decode()}" if ex.response.content else ""
            logger.warning(f"Request on {method} {url} failed with code {ex.response.status_code}{body_log}")
            raise ex

        except Exception as ex:
            logger.warning(f"Request on {method} {url} failed: {ex}")
            raise ex

    raise last_ex
