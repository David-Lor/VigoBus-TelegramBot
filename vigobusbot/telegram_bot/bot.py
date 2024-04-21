"""BOT
Bot class and bot instance getter and generator
"""

import aiogram

from .handlers import register_handlers
from vigobusbot.settings_handler import telegram_settings
from vigobusbot.static_handler import get_messages
from vigobusbot.logger import logger
from vigobusbot.utils import Singleton, SetupTeardown


class Bot(aiogram.Bot, Singleton, SetupTeardown):
    def __init__(self):
        token = telegram_settings.token
        botapi_server = telegram_settings.bot_api

        super().__init__(
            token=telegram_settings.token,
            server=aiogram.bot.api.TelegramAPIServer.from_base(botapi_server)
        )
        self.dispatcher = aiogram.Dispatcher(self)
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

    async def _set_commands(self) -> bool:
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

    async def setup(self):
        await self._set_commands()
