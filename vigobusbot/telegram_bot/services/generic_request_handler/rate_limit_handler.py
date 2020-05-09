"""SERVICES - GENERIC REQUEST HANDLER - RATE LIMIT HANDLER
Handle the request rate limits for incoming user requests
"""

# # Installed # #
import cachetools

# # Project # #
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.exceptions import UserRateLimit
from vigobusbot.logger import logger

__all__ = ("handle_user_rate_limit",)

_user_requests = cachetools.TTLCache(maxsize=float("inf"), ttl=settings.user_rate_limit_time)
"""Storage for Users and their amount of requests.
Key=user_id
Value=amount of requests
"""


def handle_user_rate_limit(user_id: int):
    """Add +1 to the requests counter of the user (or create the counter if not exists or expired).
    :raises: UserRateLimit if limit exceeded
    """
    try:
        requests = _user_requests[user_id] + 1
    except KeyError:
        requests = 1

    with logger.contextualize(current_user_requests=requests, user_requests_limit=settings.user_rate_limit_amount):
        if requests > settings.user_rate_limit_amount:
            logger.debug("User exceeded rate limit")
            raise UserRateLimit()
        else:
            logger.debug(f"Request counter for the user")
            _user_requests[user_id] = requests
