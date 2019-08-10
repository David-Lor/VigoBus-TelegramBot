"""BOT
Bot class and bot instance getter and generator
"""

# # Native # #
from typing import Optional

# # Installed # #
import aiogram

# # Project # #
from ..settings_handler import telegram_settings as settings

# # Package # #
from .handlers import register_handlers

__all__ = ("Bot", "get_bot")


class Bot(aiogram.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dispatcher = aiogram.Dispatcher(self)


_bot: Optional[Bot] = None


def get_bot() -> Bot:
    """Get the bot instance or generate and return a new one. Register all the handlers on bot instance generation.
    """
    global _bot
    if _bot is None:
        _bot = Bot(token=settings.token)
        register_handlers(_bot.dispatcher)
    return _bot
