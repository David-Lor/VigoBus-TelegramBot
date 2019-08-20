"""SOURCE CONTEXT
SourceContext helps understanding where a request came from and what details and features are requested
"""

# # Native # #
from typing import Optional

# # Installed # #
import pydantic
import aiogram

__all__ = ("SourceType", "SourceContext")


class SourceType:
    PrivateChat = 0
    Inline = 1


class SourceContext(pydantic.BaseModel):
    stop_id: int
    user_id: int
    source_message: Optional[aiogram.types.Message]
    """Message object if message come from a private chat"""
    source_chat_id: Optional[int]
    """Chat ID if message come from inline mode"""
    get_all_buses = False
    """True if user want to get the complete list of available buses"""

    @property
    def source_type(self):
        return SourceType.PrivateChat if self.source_message is not None else SourceType.Inline

    class Config:
        arbitrary_types_allowed = True
