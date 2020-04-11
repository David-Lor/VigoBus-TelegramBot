"""HTTP SERVICE
Perform HTTP requests with logging, error handling & retries support
"""

# # Native # #
from typing import Optional

# # Installed # #
import httpx
from httpx import AsyncResponse

# # Project # #
from vigobusbot.logger import logger

__all__ = ("http_request", "Methods", "AsyncResponse")


class Methods:
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


async def http_request(
        method: str, url: str,
        timeout: float, retries: int,
        query_params: Optional[dict] = None, body: Optional[dict] = None
) -> httpx.AsyncResponse:
    last_error = None

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

        except httpx.Timeout as error:
            logger.warning(f"Request on {method} {url} timed out (retries: {retry_count+1}/{retries})")
            last_error = error

        except httpx.HTTPError as error:
            with logger.contextualize(response=error.response):
                logger.warning(f"Request on {method} {url} failed with code {error.response.status_code}")
            raise error

        except Exception as error:
            logger.warning(f"Request on {method} {url} failed: {error}")
            raise error

    raise last_error
