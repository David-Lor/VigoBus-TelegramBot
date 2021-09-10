"""REQUESTER
Helpers to request the HTTP Persistence API
"""

# # Native # #
import urllib.parse
from typing import Optional

# # Project # #
from vigobusbot.services.http import http_request as _http_request
from vigobusbot.services.http import Methods, Response
from vigobusbot.settings_handler import persistence_settings as settings

__all__ = ("http_request", "Methods")


async def http_request(
        method, endpoint,
        query_params: Optional[dict] = None, body: Optional[dict] = None,
        timeout=settings.timeout, retries=settings.retries
) -> Response:
    url = urllib.parse.urljoin(settings.url, endpoint)
    return await _http_request(
        method=method, url=url, query_params=query_params, body=body, timeout=timeout, retries=retries
    )
