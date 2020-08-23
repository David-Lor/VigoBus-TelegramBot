"""REQUESTER
Helpers to request HTTP sources
"""

# # Native # #
import urllib.parse

# # Project # #
from vigobusbot.services.http import http_request, Methods, AsyncResponse
from vigobusbot.settings_handler import api_settings as settings

__all__ = ("http_get",)


async def http_get(
        endpoint, query_params=None, timeout=settings.timeout, retries=settings.retries
) -> AsyncResponse:
    url = urllib.parse.urljoin(settings.url, endpoint)
    return await http_request(method=Methods.GET, url=url, query_params=query_params, timeout=timeout, retries=retries)
