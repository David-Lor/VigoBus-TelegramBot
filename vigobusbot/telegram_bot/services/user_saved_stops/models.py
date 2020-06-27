"""USER SAVED STOPS - Models
Models for User Saved Stops, including encrypt/decrypt logic
"""

# # Native # #
from typing import Optional, Union, List

# # Installed # #
import pydantic

__all__ = ("UserStopCreate", "UserStopRead", "UserStopsRead", "UserStopFilter")


class UserStopBase(pydantic.BaseModel):
    """Base model with common attributes for UserStop"""
    stop_id: int
    user_id: Union[str, int]
    stop_custom_name: Optional[str]


class UserStopCreate(UserStopBase):
    """Model used for storing a UserStop in database. Includes logic for encryption of fields.
    Encrypted fields are user_id and stop_custom_name"""
    user_id: str
    # TODO created, updated fields (Create/Update submodels?)

    @pydantic.root_validator(pre=True)
    def _encrypt_data(cls, data):
        user_id = data.pop("user_id")
        stop_custom_name = data.pop("stop_custom_name")
        # TODO encrypt data
        return {
            **data,
            "user_id": user_id,
            "stop_custom_name": stop_custom_name
        }


class UserStopFilter(UserStopCreate):
    """Model used for filtering - as it inherits from UserStopDatabase, it can use its encryption logic.
    Currently filtering fields are: user_id (required), stop_id (optional)"""
    stop_id = Optional[int]

    def filter(self):
        return self.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True)


class UserStopRead(UserStopBase):
    """Model used for reading a UserStop from database. Includes logic for decryption of fields.
    The real, raw user_id must be provided to override the document read value, so it can be used to fetch the key"""
    user_id: int
    stop_original_name: str
    """The original name of the Stop on the BusAPI"""

    @pydantic.validator("stop_original_name")
    def _decrypt_stop_original_name(cls, v):
        return v


UserStopsRead = List[UserStopRead]
