"""ENTRYPOINT
Start Telegram bot using Polling/Webhook methods depending on the settings
"""

import asyncio
import atexit

from contexttimer import Timer

from vigobusbot.telegram_bot import Bot, start_polling
from vigobusbot.telegram_bot.services.stop_messages_deprecation_reminder import StopMessagesDeprecationReminder
from vigobusbot.services.couchdb import CouchDB
from vigobusbot.static_handler import load_static_files
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.logger import logger


async def initialize():
    logger.debug("Initializing the app...")
    with Timer() as timer:
        await asyncio.gather(
            Bot.get_instance(initialize=True).setup(),
            StopMessagesDeprecationReminder.get_instance(initialize=True).setup(),
            CouchDB.get_instance(initialize=True).setup(),
        )

    logger.bind(elapsed=timer.elapsed).info("Initialization completed")


async def teardown():
    logger.debug("Closing the app...")
    with Timer() as timer:
        # TODO async.gather & loop services
        if couchdb := CouchDB.get_instance():
            await couchdb.teardown()
        if reminder := StopMessagesDeprecationReminder.get_instance():
            await reminder.teardown()
        if bot := Bot.get_instance():
            await bot.teardown()

    logger.bind(elapsed=timer.elapsed).info("Teardown completed")


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
