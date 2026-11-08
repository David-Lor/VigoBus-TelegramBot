"""BOT
Bot class and bot instance getter and generator
"""

import asyncio
import logging

import aiogram

from .handlers import register_handlers
from vigobusbot.settings import TelegramSettings
from vigobusbot.static_handler import get_messages
from vigobusbot.logger import logger
from vigobusbot.utils import Singleton, SetupTeardown


class Bot(aiogram.Bot, Singleton, SetupTeardown):
    def __init__(self, loop=None):
        token = TelegramSettings.get().token.get_secret_value()
        super().__init__(
            token=token,
            loop=loop if loop else asyncio.get_running_loop(),
        )
        self.dispatcher = aiogram.Dispatcher(self, loop=loop)
        register_handlers(self.dispatcher)
        logger.debug(f"Created new Bot instance with token {token[:4]}...{token[-4:]}")

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
            return True

        except Exception:
            logger.opt(exception=True).warning("Bot commands could not be set")
            return False

    async def setup(self):
        await self._setup_commands()
        if TelegramSettings.get().disable_dispatcher_logger:
            # TODO Unify aiogram logger with our logger
            logging.getLogger("aiogram.dispatcher.dispatcher").disabled = True

    async def teardown(self):
        pass


def run_bot_polling():
    """Run the Telegram bot with the Polling method.
    This is a blocking function (bot runs on foreground until shutdown).
    """
    logger.info("Bot polling starting now")
    telegram_settings = TelegramSettings.get()
    bot = Bot.get_instance()
    aiogram.executor.start_polling(
        dispatcher=bot.dispatcher,
        skip_updates=telegram_settings.skip_prev_updates,
        timeout=telegram_settings.polling_timeout,
        fast=telegram_settings.polling_fast,
        loop=bot.loop,
    )
    logger.info("Bot polling finished")
