"""RUNNER
Start Telegram bot using Polling/Webhook methods depending on the settings
"""

# # Package # #
from .logger import *
from .settings_handler import telegram_settings as settings
from .static_handler import load_static_files
from . import telegram_bot as bot

__all__ = ("run",)


def run():
    load_static_files()

    if settings.method == "webhook":
        logger.debug("Starting the bot with the Webhook method...")
        pass
    else:
        logger.debug("Starting the bot with the Polling method...")
        bot.start_polling()

    logger.debug("Bye!")


if __name__ == '__main__':
    run()
