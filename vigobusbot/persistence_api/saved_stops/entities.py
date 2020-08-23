"""ENTITIES (SAVED STOPS)
Entities related with Saved Stops persisted data
"""

# # Native # #
from typing import Union, Optional, List

# # Installed # #
import pydantic

__all__ = ("SavedStopEncoded", "SavedStop", "SavedStops")


class SavedStopBase(pydantic.BaseModel):
    stop_id: int
    user_id: Union[str, int]
    stop_name: Optional[str]
    stop_original_name: Optional[str]
    """Stop original name is not saved on database"""


class SavedStopEncoded(SavedStopBase):
    """Saved Stop encoded. Used to send as body of a POST request, or as result of a GET request.
    """
    user_id: str


class SavedStop(SavedStopBase):
    """Saved Stop decoded/native. Used after decoding a GET request or before sending a POST request.
    """
    user_id: int


SavedStops = List[SavedStop]
