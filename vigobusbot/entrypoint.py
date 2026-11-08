"""ENTRYPOINT
Start Telegram bot using the Polling method.
"""

import asyncio

from contexttimer import Timer

from vigobusbot.telegram_bot import Bot, run_bot_polling
from vigobusbot.services.couchdb import CouchDB
from vigobusbot.services.elasticsearch import ElasticSearch
from vigobusbot.vigobus_api import VigoBusAPI
from vigobusbot.services import schedulers
from vigobusbot.static_handler import load_static_files
from vigobusbot.settings import Settings, load_settings
from vigobusbot.utils import SetupTeardown, async_noop
from vigobusbot.logger import logger


class App(SetupTeardown):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.services: list[SetupTeardown] = list()

    async def setup(self):
        logger.debug("Initializing the app...")
        with Timer() as timer:
            load_settings()

            elastic_settings = Settings.get().elasticsearch
            telegram_settings = Settings.get().telegram

            # Services that do not require setup/teardown
            VigoBusAPI.get_instance(initialize=True)
            load_static_files()

            # Services with setup/teardown
            # Initialize in different blocks based on the dependencies between services

            # Block 1
            services = [
                Bot.get_instance(initialize=True),
                CouchDB.get_instance(initialize=True),
            ]
            if elastic_settings.enabled:
                services.append(ElasticSearch.get_instance(initialize=True))
            await self._init_services(*services)

            # Block 2
            await self._init_services(
                schedulers.StopUpdaterService(
                    cron_schedule=telegram_settings.stop_updater_cron,
                    first_run=telegram_settings.stop_updater_first_run,
                    limit_concurrency=True,
                ).set_current_as_singleton(),
                schedulers.StopMessagesDeprecationReminder(
                    cron_schedule=telegram_settings.stop_messages_deprecation_reminder_cron,
                ).set_current_as_singleton(),
                schedulers.StopSyncToElasticService(
                    cron_schedule=telegram_settings.stop_elastic_sync_cron,
                    first_run=telegram_settings.stop_elastic_sync_first_run,
                    limit_concurrency=True,
                ),
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
