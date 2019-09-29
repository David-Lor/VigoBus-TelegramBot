"""TESTS - UTILS - TELEGRAM CLIENT
Start and stop the Telegram client for testing using tgintegration (and pyrogram behind)
"""

# # Native # #
from typing import Optional

# # Installed # #
from tgintegration import BotIntegrationClient

# # Package # #
from .settings import settings

__all__ = ("start_client", "stop_client", "BotIntegrationClient")

__client: Optional[BotIntegrationClient] = None


def start_client() -> BotIntegrationClient:
    global __client
    if __client is None:
        __client = BotIntegrationClient(
            bot_under_test=settings.bot_name,
            session_name=settings.telegram_session_filename,
            api_id=settings.api_id,
            api_hash=settings.api_hash,

        )

    __client.start()
    __client.clear_chat()
    return __client


def stop_client():
    global __client
    if __client and __client.is_started:
        __client.stop()
        __client = None
