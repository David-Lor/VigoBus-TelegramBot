"""ENCODER/DECODER
Functions to encode and decode persisted user data incoming/outcoming from/to the Persistance API.
"""

# # Native # #
from typing import Union, Optional

# # Package # #
from .key_generator import *

__all__ = ("encode", "decode")


def encode(user_id: int, raw_data: Optional[Union[str, int]]) -> Optional[str]:
    if raw_data is not None:
        key = generate_fernet_key(user_id)
        return key.encrypt(str(raw_data).encode()).decode()


def decode(user_id: int, encoded_data: Optional[str]) -> Optional[str]:
    if encoded_data is not None:
        key = generate_fernet_key(user_id)
        return key.decrypt(encoded_data.encode()).decode()
