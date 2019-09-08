"""ENTITIES
Definition of misc, static aiogram entities:
-CallbackData sent as data of the inline keyboard buttons
-ForceReply sent as reply markup of a Saved Stop Rename operation
"""

# # Installed # #
from aiogram.utils.callback_data import CallbackData
from aiogram.types.force_reply import ForceReply

__all__ = (
    "StopUpdateCallbackData", "StopGetCallbackData",
    "StopSaveCallbackData", "StopDeleteCallbackData", "StopRenameCallbackData",
    "RenameStopForceReply"
)

CommonCallbackDataKeys = ("stop_id", "get_all_buses")

StopUpdateCallbackData = CallbackData("refresh", *CommonCallbackDataKeys)

StopSaveCallbackData = CallbackData("save", *CommonCallbackDataKeys)
StopDeleteCallbackData = CallbackData("delete", *CommonCallbackDataKeys)
StopRenameCallbackData = CallbackData("rename", *CommonCallbackDataKeys)

StopGetCallbackData = CallbackData("get", "stop_id")

RenameStopForceReply = ForceReply()
