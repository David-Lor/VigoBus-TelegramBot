"""BOT
Bot class and bot instance getter and generator
"""

import asyncio
from typing import Optional

import aiogram

from .handlers import register_handlers
from vigobusbot.telegram_bot.services.stop_messages_deprecation_reminder import stop_messages_deprecation_reminder_worker
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.static_handler import get_messages
from vigobusbot.logger import logger


class Bot(aiogram.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatcher = aiogram.Dispatcher(self)
        logger.debug(f"Created new Bot instance with token {kwargs['token'][:4]}...{kwargs['token'][-4:]}, "
                     f"using Bot API {kwargs['server']}")

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

    async def set_commands(self) -> bool:
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

    async def start_background_services(self):
        # noinspection PyAsyncCall
        asyncio.create_task(stop_messages_deprecation_reminder_worker(self))


_bot: Optional[Bot] = None


def get_bot() -> Bot:
    """Get the bot instance or generate and return a new one. Register all the handlers on bot instance generation.
    """
    global _bot
    if _bot is None:
        _bot = Bot(token=settings.token, server=settings.bot_api_server)
        register_handlers(_bot.dispatcher)
    return _bot
