"""RUNNER
Start Telegram bot using Polling/Webhook methods depending on the settings
"""

# # Project # #
from vigobusbot.telegram_bot import start_polling
from vigobusbot.static_handler import load_static_files
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.logger import logger

__all__ = ("run",)


def run():
    load_static_files()

    if settings.method == "webhook":
        logger.debug("Starting the bot with the Webhook method...")
        pass
    else:
        logger.debug("Starting the bot with the Polling method...")
        start_polling()

    logger.debug("Bye!")


if __name__ == '__main__':
    run()
