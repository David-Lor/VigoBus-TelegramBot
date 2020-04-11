"""POLLING
Telegram bot executor using the Polling method
"""

# # Installed # #
import aiogram

# # Package # #
from .bot import get_bot

# # Project # #
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.logger import logger


def start_polling():
    """Start the Telegram bot with the Polling method. Creates a new Bot instance if not exists.
    This is a blocking function (bot runs on foreground until shutdown).
    """
    bot = get_bot()
    logger.debug("Bot polling starting now!")
    aiogram.executor.start_polling(
        bot.dispatcher,
        skip_updates=settings.skip_prev_updates,
        timeout=settings.polling_timeout,
        fast=settings.polling_fast
    )
    logger.debug("Bot polling finished!")
