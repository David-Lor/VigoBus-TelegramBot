"""TESTS - UTILS - MOCKED PERSISTENCE API - ENTITIES
Entities used by the Fake Persistence API
"""

# # Native # #
from typing import Optional

# # Installed # #
import pydantic

__all__ = ("SavedStop",)


class SavedStop(pydantic.BaseModel):
    user_id: int
    stop_id: int
    stop_name: Optional[str]
