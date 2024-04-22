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
from vigobusbot.utils import SetupTeardown, SingletonHold
from vigobusbot.logger import logger


services: SingletonHold[list[SetupTeardown]] = SingletonHold()


async def async_setup():
    logger.debug("Initializing the app...")
    with Timer() as timer:
        services.set_value([
            Bot.get_instance(initialize=True),
            StopMessagesDeprecationReminder.get_instance(initialize=True),
            CouchDB.get_instance(initialize=True),
        ])

        await asyncio.gather(*[service.setup() for service in services.get_value()])

    logger.bind(elapsed=timer.elapsed).info("Initialization completed")


async def async_teardown():
    logger.info("Closing the app...")
    with Timer() as timer:
        await asyncio.gather(*[service.teardown() for service in services.get_value()])

    logger.bind(elapsed=timer.elapsed).info("Teardown completed")


def run():
    load_static_files()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_setup())

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
