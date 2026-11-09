"""SERVICES - GENERIC REQUEST HANDLER - RATE LIMIT HANDLER
Handle the request rate limits for incoming user requests
"""

import cachetools

from vigobusbot.settings import TelegramSettings, SettingsLoadedSignal
from vigobusbot.exceptions import UserRateLimit
from vigobusbot.logger import logger
from vigobusbot.utils import SingletonHold

__all__ = ("handle_user_rate_limit",)

_user_requests: SingletonHold[cachetools.Cache[int, float]] = SingletonHold()
"""Storage for Users and their amount of requests.
Key=user_id
Value=amount of requests
"""


@SettingsLoadedSignal.connect
def _on_settings_loaded(*_, **__):
    cache = cachetools.TTLCache(maxsize=float("inf"), ttl=TelegramSettings.get().user_rate_limit_time)
    _user_requests.set_value(cache)
    logger.bind(cache_ttl=cache.ttl).debug("Initialized RateLimiter-UserRequests cache")


def handle_user_rate_limit(user_id: int, weight: float):
    """Add +1 to the requests counter of the user (or create the counter if not exists or expired).
    :raises: UserRateLimit if limit exceeded
    """
    if (cache := _user_requests.get_value()) is None:
        return

    try:
        requests = cache[user_id] + weight
    except KeyError:
        requests = weight

    with logger.contextualize(
            current_user_requests=requests,
            user_requests_limit=TelegramSettings.get().user_rate_limit_amount,
            user_request_weight=weight
    ):
        if requests > TelegramSettings.get().user_rate_limit_amount:
            logger.debug("User exceeded rate limit")
            raise UserRateLimit()
        else:
            logger.debug(f"Request counter for the user")
            cache[user_id] = requests
