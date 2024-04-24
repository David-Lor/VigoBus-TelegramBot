"""BOT
Bot class and bot instance getter and generator
"""

import asyncio

import aiogram
import aiohttp.web

from .handlers import register_handlers
from vigobusbot.settings_handler import telegram_settings, system_settings
from vigobusbot.static_handler import get_messages
from vigobusbot.logger import logger
from vigobusbot.utils import Singleton, SetupTeardown


class Bot(aiogram.Bot, Singleton, SetupTeardown):
    def __init__(self, loop=None):
        token = telegram_settings.token
        botapi_server = telegram_settings.bot_api

        super().__init__(
            token=telegram_settings.token,
            server=aiogram.bot.api.TelegramAPIServer.from_base(botapi_server),
            loop=loop if loop else asyncio.get_running_loop(),
        )
        self.dispatcher = aiogram.Dispatcher(self, loop=loop)
        register_handlers(self.dispatcher)
        logger.debug(f"Created new Bot instance with token {token[:4]}...{token[-4:]}, using Bot API {botapi_server}")

    @staticmethod
    def __set_message_kwargs(kwargs: dict):
        kwargs.setdefault("parse_mode", "HTML")
        kwargs.setdefault("disable_web_page_preview", True)

    async def send_message(self, *args, **kwargs):
        self.__set_message_kwargs(kwargs)
        return await super().send_message(*args, **kwargs)

    async def edit_message_text(self, *args, **kwargs):
        self.__set_message_kwargs(kwargs)
        return await super().edit_message_text(*args, **kwargs)

    async def _setup_commands(self) -> bool:
        # noinspection PyBroadException
        try:
            commands_dict: dict = get_messages().commands
            logger.bind(commands=commands_dict).debug("Setting bot commands...")

            await self.set_my_commands([
                aiogram.types.BotCommand(command=key, description=value)
                for key, value in commands_dict.items()
            ])
            logger.debug("Bot commands successfully set")

        except Exception:
            logger.opt(exception=True).warning("Bot commands could not be set")
            return False

    # noinspection PyUnusedLocal
    async def webhook_on_startup(self, *args, **kwargs):
        logger.debug("Setting webhook...")
        await self.set_webhook(
            url=telegram_settings.webhook_url,
            secret_token=telegram_settings.webhook_secret,
        )
        logger.info(f"Webhook set for URL {telegram_settings.webhook_url}")

    async def setup(self):
        await self._setup_commands()

    async def teardown(self):
        if telegram_settings.webhook_enabled and telegram_settings.webhook_delete_on_close:
            logger.debug("Deleting bot webhook...")
            await self.delete_webhook()
            logger.info("Bot webhook deleted")


def run_bot_polling():
    """Run the Telegram bot with the Polling method.
    This is a blocking function (bot runs on foreground until shutdown).
    """
    logger.info("Bot polling starting now")
    bot = Bot.get_instance()
    aiogram.executor.start_polling(
        dispatcher=bot.dispatcher,
        skip_updates=telegram_settings.skip_prev_updates,
        timeout=telegram_settings.polling_timeout,
        fast=telegram_settings.polling_fast,
        loop=bot.loop,
    )
    logger.info("Bot polling finished")


def run_bot_webhook():
    """Run the Telegram bot with the Webhook method, running an HTTP server.
    This is a blocking function (bot runs on foreground until shutdown).
    Implements a workaround for using a custom loop in the HTTP server, and avoid closing it on exit.
    """
    bot = Bot.get_instance()

    executor = aiogram.executor.set_webhook(
        dispatcher=bot.dispatcher,
        webhook_path=telegram_settings.webhook_path,
        skip_updates=telegram_settings.skip_prev_updates,
        on_startup=bot.webhook_on_startup,
        loop=bot.loop,
    )

    if status_path := telegram_settings.webhook_status_path:
        logger.info(f"Webhook status path available at {status_path}")
        executor.web_app.add_routes([aiohttp.web.get(status_path, webhook_status_endpoint_handler)])

    logger.info("Bot webhook starting now")
    # noinspection PyProtectedMember
    bot.loop.run_until_complete(aiohttp.web._run_app(
        app=executor.web_app,
        host=telegram_settings.webhook_host,
        port=telegram_settings.webhook_port,
    ))

    logger.info("Bot webhook finished")


# noinspection PyUnusedLocal
async def webhook_status_endpoint_handler(*args, **kwargs) -> aiohttp.web.Response:
    return aiohttp.web.json_response(dict(
        success=True,
        node=system_settings.node_name
    ))
