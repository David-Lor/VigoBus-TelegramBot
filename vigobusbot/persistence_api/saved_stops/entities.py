"""ENTITIES (SAVED STOPS)
Entities related with Saved Stops persisted data, with methods to convert between encoded/decoded class types.
"""

# # Native # #
from typing import Union, Optional, List

# # Installed # #
import pydantic

__all__ = ("SavedStopEncoded", "SavedStopDecoded", "SavedStopBase", "SavedStops")


class SavedStopBase(pydantic.BaseModel):
    stop_id: Union[str, int]
    user_id: Union[str, int]
    stop_name: Optional[str]
    stop_original_name: Optional[str]


class SavedStopEncoded(SavedStopBase):
    """Saved Stop encoded. Used to send as body of a POST request, or as result of a GET request.
    """
    stop_id: str
    user_id: Optional[str]


class SavedStopDecoded(SavedStopBase):
    """Saved Stop decoded/native. Used after decoding a GET request or before sending a POST request.
    """
    stop_id: int
    user_id: Optional[int]


SavedStops = List[SavedStopBase]
