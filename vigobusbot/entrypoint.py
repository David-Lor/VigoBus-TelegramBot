"""ENTRYPOINT
Start Telegram bot using Polling/Webhook methods depending on the settings
"""

import asyncio
import atexit

from vigobusbot.telegram_bot import Bot, start_polling
from vigobusbot.services.couchdb import CouchDB
from vigobusbot.static_handler import load_static_files
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.logger import logger


async def initialize():
    bot = Bot().set_current_as_singleton()
    couchdb = CouchDB().set_current_as_singleton()
    await asyncio.gather(
        bot.set_commands(),
        bot.start_background_services(),
        couchdb.initialize(),
    )


async def teardown():
    logger.debug("Closing the app...")
    if couchdb := CouchDB.get_instance():
        await couchdb.close()

    logger.info("Teardown completed")


def run():
    load_static_files()
    asyncio.get_event_loop().run_until_complete(initialize())
    atexit.register(lambda: asyncio.get_event_loop().run_until_complete(teardown()))

    if settings.method == "webhook":
        logger.debug("Starting the bot with the Webhook method...")
        raise Exception("Webhook method not yet implemented")
    else:
        logger.debug("Starting the bot with the Polling method...")
        start_polling()


if __name__ == '__main__':
    run()
