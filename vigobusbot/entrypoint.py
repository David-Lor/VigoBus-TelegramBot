"""ENTRYPOINT
Start Telegram bot using Polling/Webhook methods depending on the settings
"""

import asyncio

from contexttimer import Timer

from vigobusbot.telegram_bot import Bot, run_bot_polling, run_bot_webhook
from vigobusbot.services.couchdb import CouchDB
from vigobusbot.vigobus_api import VigoBusAPI
from vigobusbot.services.schedulers import StopUpdaterService, StopMessagesDeprecationReminder
from vigobusbot.static_handler import load_static_files
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.utils import SetupTeardown
from vigobusbot.logger import logger


class App(SetupTeardown):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.services: list[SetupTeardown] = list()

    async def setup(self):
        logger.debug("Initializing the app...")
        with Timer() as timer:
            # Services that do not require setup/teardown
            VigoBusAPI.get_instance(initialize=True)

            # Services with setup/teardown
            self.services = [
                Bot.get_instance(initialize=True),
                CouchDB.get_instance(initialize=True),
                StopUpdaterService(settings.stop_updater_cron, limit_concurrency=True).set_current_as_singleton(),
                StopMessagesDeprecationReminder(settings.stop_messages_deprecation_reminder_cron).set_current_as_singleton()
            ]

            load_static_files()
            await asyncio.gather(*[service.setup() for service in self.services])

        logger.bind(elapsed=timer.elapsed).info("Initialization completed")

    async def teardown(self):
        logger.info("Closing the app...")
        with Timer() as timer:
            await asyncio.gather(*[service.teardown() for service in self.services])

        logger.bind(elapsed=timer.elapsed).info("Teardown completed")

    def run(self):
        self.loop.run_until_complete(self.setup())

        try:
            if settings.webhook_enabled:
                run_bot_webhook()
            else:
                run_bot_polling()
        except (SystemExit, KeyboardInterrupt):
            # TODO Exit with corresponding exit code
            pass

        self.loop.run_until_complete(self.teardown())


def run():
    App().run()


if __name__ == '__main__':
    run()
