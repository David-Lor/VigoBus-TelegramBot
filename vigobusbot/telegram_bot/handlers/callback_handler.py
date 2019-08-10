"""CALLBACK HANDLER
Unique handler for the Callback Queries, produced when users press buttons from the inline keyboards on messages
"""

# # Installed # #
import aiogram

# # Project # #
from ..message_generators import StopUpdateCallbackData

__all__ = ("register_handler",)


async def stop_refresh(callback_query: aiogram.types.CallbackQuery, callback_data: dict):
    stop_id = callback_data["stop_id"]
    get_all_buses = int(callback_data["get_all_buses"])
    print("Refresh Callback Query:", stop_id, get_all_buses)
    await callback_query.answer()


def register_handler(dispatcher: aiogram.Dispatcher):
    """Register the callback query handler for the given Bot Dispatcher.
    """
    # Stop Refresh button
    dispatcher.register_callback_query_handler(stop_refresh, StopUpdateCallbackData.filter())
