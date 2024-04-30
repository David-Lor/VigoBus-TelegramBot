"""PERSISTENCE API - SAVED STOPS
Stops saved by the users on their own stop list.
The Stop data is encoded before sent to the API, and decoded when read from it.
"""

from .saved_stops_manager import *

__all__ = (
    "get_user_saved_stops", "save_stop", "delete_stop", "is_stop_saved", "delete_all_stops"
)
