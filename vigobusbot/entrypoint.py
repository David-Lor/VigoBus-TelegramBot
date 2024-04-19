"""ENTRYPOINT
Start Telegram bot using Polling/Webhook methods depending on the settings
"""

# # Native # #
import asyncio

# # Project # #
from vigobusbot.telegram_bot import get_bot, start_polling
from vigobusbot.static_handler import load_static_files
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.logger import logger


def run():
    load_static_files()
    bot = get_bot()
    asyncio.get_event_loop().run_until_complete(bot.set_commands())
    asyncio.get_event_loop().run_until_complete(bot.start_background_services())

    if settings.method == "webhook":
        logger.debug("Starting the bot with the Webhook method...")
        raise Exception("Webhook method not yet implemented")
    else:
        logger.debug("Starting the bot with the Polling method...")
        start_polling(bot)

    logger.debug("Bye!")


if __name__ == '__main__':
    run()
