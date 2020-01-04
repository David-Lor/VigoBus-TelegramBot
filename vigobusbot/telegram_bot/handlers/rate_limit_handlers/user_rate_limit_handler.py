"""USER RATE LIMIT HANDLER
Limits the amount of requests that a user can perform on a time window
"""

# # Installed # #
import cachetools

# # Project # #
from ....settings_handler import telegram_settings as settings
from ....exceptions import *
from ....logger import *

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
    # TODO Set as part of a context manager to handle the rate limit, create the logging Context ID, ...
    try:
        requests = _user_requests[user_id]
    except KeyError:
        requests = 0

    requests += 1

    if requests > settings.user_rate_limit_amount:
        logger.debug(f"User {user_id} exceeded rate limit with {requests} requests")
        raise UserRateLimit()
    else:
        logger.debug(f"User {user_id} performed a request (current rate: {requests}/{settings.user_rate_limit_amount})")
        _user_requests[user_id] = requests
