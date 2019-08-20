"""STOP MESSAGE BUTTONS
Helper to generate the Stop Message buttons markup
"""

# # Installed # #
import aiogram

# # Project # #
from ...static_handler import *
from ...persistence_api import saved_stops

# # Package # #
from .source_context import *
from .callback_data import *

__all__ = ("generate_stop_message_buttons",)


async def generate_stop_message_buttons(context: SourceContext) -> aiogram.types.InlineKeyboardMarkup:
    messages = get_messages()

    is_stop_saved = await saved_stops.is_stop_saved(user_id=context.user_id, stop_id=context.stop_id)

    button_refresh = aiogram.types.InlineKeyboardButton(
        text=messages.stop.buttons.refresh,
        callback_data=StopUpdateCallbackData.new(
            stop_id=context.stop_id,
            get_all_buses=int(context.get_all_buses)
        )
    )

    if not is_stop_saved:
        button_save_delete = aiogram.types.InlineKeyboardButton(
            text=messages.stop.buttons.save,
            callback_data=StopSaveCallbackData.new(
                stop_id=context.stop_id,
                get_all_buses=int(context.get_all_buses)
            )
        )
    else:
        button_save_delete = aiogram.types.InlineKeyboardButton(
            text=messages.stop.buttons.delete,
            callback_data=StopDeleteCallbackData.new(
                stop_id=context.stop_id,
                get_all_buses=int(context.get_all_buses)
            )
        )

    markup = aiogram.types.InlineKeyboardMarkup()
    markup.row(button_refresh, button_save_delete)

    return markup
