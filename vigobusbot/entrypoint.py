"""ENTRYPOINT
Start Telegram bot using Polling/Webhook methods depending on the telegram_settings
"""

import asyncio

from contexttimer import Timer

from vigobusbot.telegram_bot import Bot, run_bot_polling, run_bot_webhook
from vigobusbot.services.couchdb import CouchDB
from vigobusbot.services.elasticsearch import ElasticSearch
from vigobusbot.vigobus_api import VigoBusAPI
from vigobusbot.services.schedulers import StopUpdaterService, StopMessagesDeprecationReminder
from vigobusbot.static_handler import load_static_files
from vigobusbot.settings_handler import telegram_settings, elastic_settings
from vigobusbot.utils import SetupTeardown, async_noop
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
            load_static_files()

            # Services with setup/teardown
            # Initialize in different blocks based on the dependencies between services
            await self._init_services(
                Bot.get_instance(initialize=True),
                CouchDB.get_instance(initialize=True),
                ElasticSearch.get_instance(initialize=True) if elastic_settings.enabled else async_noop(),
            )
            await self._init_services(
                StopUpdaterService(telegram_settings.stop_updater_cron, first_run=telegram_settings.stop_updater_first_run, limit_concurrency=True).set_current_as_singleton(),
                StopMessagesDeprecationReminder(telegram_settings.stop_messages_deprecation_reminder_cron).set_current_as_singleton()
            )

        logger.bind(elapsed=timer.elapsed).info("Initialization completed")

    async def teardown(self):
        logger.info("Closing the app...")
        with Timer() as timer:
            await asyncio.gather(*[service.teardown() for service in self.services if service])

        logger.bind(elapsed=timer.elapsed).info("Teardown completed")

    def run(self):
        self.loop.run_until_complete(self.setup())

        try:
            if telegram_settings.webhook_enabled:
                run_bot_webhook()
            else:
                run_bot_polling()
        except (SystemExit, KeyboardInterrupt):
            # TODO Exit with corresponding exit code
            pass

        self.loop.run_until_complete(self.teardown())

    async def _init_services(self, *services: SetupTeardown):
        await asyncio.gather(*[service.setup() for service in services if service])
        self.services.extend(services)


def run():
    App().run()


if __name__ == '__main__':
    run()
