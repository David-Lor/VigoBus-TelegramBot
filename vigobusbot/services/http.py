"""HTTP SERVICE
Perform HTTP requests with logging, error handling & retries support
"""

# # Native # #
import time
from typing import Optional

# # Installed # #
import httpx
from httpx import Response

# # Project # #
from vigobusbot.logger import logger

__all__ = ("http_request", "Methods", "Response")


class Methods:
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


async def http_request(
        method: str, url: str,
        timeout: float, retries: int,
        query_params: Optional[dict] = None, body: Optional[dict] = None,
        raise_status: bool = True
) -> httpx.Response:
    last_error = None

    for retry_count in range(retries):
        with logger.contextualize(
            request_method=method,
            request_url=url,
            request_timeout=timeout,
            request_attempt=retry_count+1,
            request_max_attempts=retries,
            request_params=query_params,
            request_body=body
        ):
            logger.debug("Requesting URL")
            result: httpx.Response

            try:
                start_time = time.time()
                async with httpx.AsyncClient(timeout=timeout) as client:
                    if method == Methods.GET:
                        result = await client.get(url=url, params=query_params)
                    elif method == Methods.POST:
                        result = await client.post(url=url, params=query_params, json=body)
                    elif method == Methods.DELETE:
                        result = await client.delete(url=url, params=query_params)

                response_time = round(time.time() - start_time, 4)
                logger.bind(
                    response_elapsed_time=response_time,
                    response_status_code=result.status_code,
                    response_body=result.text
                ).debug("Response received")

                if raise_status:
                    result.raise_for_status()
                return result

            except httpx.TimeoutException as error:
                logger.warning("Request timed out")
                last_error = error

            except httpx.HTTPStatusError as error:
                logger.bind(
                    response_status_code=error.response.status_code,
                    response_body=error.response.text
                ).warning("Request failed with bad status code")
                raise error

            except Exception as error:
                logger.opt(exception=True).warning("Request failed")
                raise error

    raise last_error
