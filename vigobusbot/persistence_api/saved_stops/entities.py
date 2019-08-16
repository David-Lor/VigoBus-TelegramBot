"""ENTITIES (SAVED STOPS)
Entities related with Saved Stops persisted data, with methods to convert between encoded/decoded class types.
"""

# # Native # #
from typing import Union, Optional, List

# # Installed # #
import pydantic

# # Package # #
from .encoder_decoder import *
from .key_generator import *

__all__ = ("SavedStopEncoded", "SavedStopDecoded", "SavedStops")

# TODO decode/encode methods are not used for now until finding best encoding/encryption method for the data


class SavedStopBase(pydantic.BaseModel):
    stop_id: Union[str, int]
    user_id: Union[str, int]
    stop_name: Optional[str]


class SavedStopEncoded(SavedStopBase):
    """Saved Stop encoded. Used to send as body of a POST request, or as result of a GET request.
    """
    stop_id: str
    user_id: Optional[str]

    # def decode(self, decoded_user_id: int) -> SavedStopBase:
    #     """Get the SavedStopDecoded equivalent of this encoded Saved Stop.
    #     """
    #     return SavedStopDecoded(
    #         user_id=decoded_user_id,
    #         stop_id=decode(user_id=decoded_user_id, encoded_data=self.stop_id),
    #         stop_name=decode(user_id=decoded_user_id, encoded_data=self.stop_name)
    #     )


class SavedStopDecoded(SavedStopBase):
    """Saved Stop decoded/native. Used after decoding a GET request or before sending a POST request.
    """
    stop_id: int
    user_id: Optional[int]

    # def encode(self) -> SavedStopEncoded:
    #     """Get the SavedStopEncoded equivalent of this decoded/native Saved Stop.
    #     """
    #     return SavedStopEncoded(
    #         user_id=generate_user_hash(self.user_id),
    #         stop_id=encode(user_id=self.user_id, raw_data=self.stop_id),
    #         stop_name=encode(user_id=self.user_id, raw_data=self.stop_name)
    #     )


SavedStops = List[SavedStopBase]
