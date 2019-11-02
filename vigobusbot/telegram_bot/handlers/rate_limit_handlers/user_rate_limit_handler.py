"""USER RATE LIMIT HANDLER
Limits the amount of requests that a user can perform on a time window
"""

# # Installed # #
import cachetools

# # Project # #
from ....settings_handler import telegram_settings as settings
from ....exceptions import *

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
        requests = _user_requests[user_id]
    except KeyError:
        requests = 0

    requests += 1

    if requests > settings.user_rate_limit_amount:
        raise UserRateLimit()
    else:
        _user_requests[user_id] = requests
