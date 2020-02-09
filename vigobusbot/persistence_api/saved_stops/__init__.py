"""PERSISTENCE API - SAVED STOPS
Stops saved by the users on their own stop list.
The Stop data is encoded before sent to the API, and decoded when read from it.
"""

from .entities import *
from .saved_stops_manager import *

__all__ = (
    "SavedStopEncoded", "SavedStop", "SavedStops",
    "get_user_saved_stops", "save_stop", "delete_stop", "is_stop_saved"
)
