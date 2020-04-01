"""TELEGRAM BOT - ENTITIES
Entities related with the Telegram Bot
"""

# # Native # #
from typing import Optional, Union

# # Installed # #
from aiogram.types import Message, CallbackQuery

OptionalString = Optional[str]
OptionalMessage = Optional[Message]
OptionalCallbackQuery = Optional[CallbackQuery]
RequestSource = Union[Message, CallbackQuery]
