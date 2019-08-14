"""CALLBACK DATA
Definition of the Callback Data sent on the inline keyboard buttons
"""

# # Installed # #
from aiogram.utils.callback_data import CallbackData

__all__ = ("StopUpdateCallbackData",)

StopUpdateCallbackData = CallbackData("refresh", "stop_id", "get_all_buses")
