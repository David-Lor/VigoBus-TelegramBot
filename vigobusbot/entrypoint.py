"""ENTRYPOINT
Start Telegram bot using Polling/Webhook methods depending on the settings
"""

import asyncio

from contexttimer import Timer

from vigobusbot.telegram_bot import Bot, run_bot_polling, run_bot_webhook
from vigobusbot.telegram_bot.services.stop_messages_deprecation_reminder import StopMessagesDeprecationReminder
from vigobusbot.services.couchdb import CouchDB
from vigobusbot.static_handler import load_static_files
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.logger import logger


async def async_initialize():
    logger.debug("Initializing the app...")
    with Timer() as timer:
        bot = Bot().set_current_as_singleton()
        await asyncio.gather(
            bot.setup(),
            StopMessagesDeprecationReminder.get_instance(initialize=True).setup(),
            CouchDB.get_instance(initialize=True).setup(),
        )

    logger.bind(elapsed=timer.elapsed).info("Initialization completed")


async def async_teardown():
    logger.info("Closing the app...")
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
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_initialize())

    try:
        if settings.webhook_enabled:
            run_bot_webhook()
        else:
            run_bot_polling()
    except (SystemExit, KeyboardInterrupt):
        # TODO Exit with corresponding exit code
        pass

    loop.run_until_complete(async_teardown())


if __name__ == '__main__':
    run()
