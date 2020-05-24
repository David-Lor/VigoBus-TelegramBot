"""SOURCE CONTEXT
SourceContext helps understanding where a request came from and what details and features are requested
"""

# # Native # #
from typing import Optional

# # Installed # #
import pydantic
import aiogram

__all__ = ("SourceContext",)


class SourceContext(pydantic.BaseModel):
    """Class used to track context of a Stop message (the Source) when the user requests actions from it.
    For example, by pressing the inline buttons to Refresh the message.
    """
    stop_id: int
    user_id: Optional[int]
    source_message: Optional[aiogram.types.Message]
    """Message object if message come from a private chat"""
    get_all_buses: bool = False
    """True if user wants to get the complete list of available buses"""
    more_buses_available: bool = False
    """True if the Bus API returned that more buses were available on last call to Buses endpoint"""
    from_inline: bool = False

    class Config:
        arbitrary_types_allowed = True
