"""STOP MESSAGE BUTTONS
Helper to generate the Stop Message buttons markup
"""

# # Installed # #
import aiogram

# # Project # #
from ...static_handler import *
from ...entities import *

# # Package # #
from .source_context import *
from .callback_data import *

__all__ = ("generate_stop_message_buttons",)


def generate_stop_message_buttons(context: SourceContext) -> aiogram.types.InlineKeyboardMarkup:
    messages = get_messages()

    button_refresh = aiogram.types.InlineKeyboardButton(
        text=messages.stop.buttons.refresh,
        callback_data=StopUpdateCallbackData.new(
            stop_id=context.stopid,
            get_all_buses=int(context.get_all_buses)
        )
    )

    markup = aiogram.types.InlineKeyboardMarkup()
    markup.row(button_refresh)

    return markup
