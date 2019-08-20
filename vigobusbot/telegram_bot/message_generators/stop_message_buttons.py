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
    row1 = list()

    is_stop_saved = await saved_stops.is_stop_saved(user_id=context.user_id, stop_id=context.stop_id)

    button_refresh = aiogram.types.InlineKeyboardButton(
        text=messages.stop.buttons.refresh,
        callback_data=StopUpdateCallbackData.new(
            stop_id=context.stop_id,
            get_all_buses=int(context.get_all_buses)
        )
    )
    row1.append(button_refresh)

    if not is_stop_saved:
        # Stop Not saved
        button_save = aiogram.types.InlineKeyboardButton(
            text=messages.stop.buttons.save,
            callback_data=StopSaveCallbackData.new(
                stop_id=context.stop_id,
                get_all_buses=int(context.get_all_buses)
            )
        )
        row1.append(button_save)
    else:
        # Stop saved
        button_delete = aiogram.types.InlineKeyboardButton(
            text=messages.stop.buttons.delete,
            callback_data=StopDeleteCallbackData.new(
                stop_id=context.stop_id,
                get_all_buses=int(context.get_all_buses)
            )
        )
        button_rename = aiogram.types.InlineKeyboardButton(
            text=messages.stop.buttons.rename,
            callback_data=StopRenameCallbackData.new(
                stop_id=context.stop_id
            )
        )
        row1.append(button_delete)
        row1.append(button_rename)

    markup = aiogram.types.InlineKeyboardMarkup()
    markup.row(*row1)

    return markup
