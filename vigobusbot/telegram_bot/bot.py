"""BOT
Bot class and bot instance getter and generator
"""

# # Native # #
from typing import Optional

# # Installed # #
import aiogram

# # Package # #
from .handlers import register_handlers

# # Project # #
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.logger import logger

__all__ = ("Bot", "get_bot")


class Bot(aiogram.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatcher = aiogram.Dispatcher(self)
        logger.debug(f"Created new Bot instance with token {kwargs['token'][:4]}...{kwargs['token'][-4:]}")

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


_bot: Optional[Bot] = None


def get_bot() -> Bot:
    """Get the bot instance or generate and return a new one. Register all the handlers on bot instance generation.
    """
    global _bot
    if _bot is None:
        _bot = Bot(token=settings.token)
        register_handlers(_bot.dispatcher)
    return _bot
