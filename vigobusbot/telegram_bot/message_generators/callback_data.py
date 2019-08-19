"""CALLBACK DATA
Definition of the Callback Data sent on the inline keyboard buttons
"""

# # Installed # #
from aiogram.utils.callback_data import CallbackData

__all__ = ("StopUpdateCallbackData", "StopSaveCallbackData", "StopDeleteCallbackData", "StopGetCallbackData")

StopUpdateCallbackData = CallbackData("refresh", "stop_id", "get_all_buses")
StopSaveCallbackData = CallbackData("save", "stop_id", "get_all_buses")
StopDeleteCallbackData = CallbackData("delete", "stop_id", "get_all_buses")

StopGetCallbackData = CallbackData("get", "stop_id")
