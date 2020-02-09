"""DECODER
Functions to decode data to raw (Persist API to Bot)
"""

# # Package # #
from .key_generator import *
from ..entities import *

__all__ = ("decode_stop", "decode_string")


def decode_string(data: str, key: Fernet) -> str:
    return key.decrypt(data.encode()).decode()


def decode_stop(encoded_stop: SavedStopEncoded, user_id: int) -> SavedStop:
    key = get_user_key(user_id)
    return SavedStop(
        stop_id=encoded_stop.stop_id,
        user_id=user_id,
        stop_name=decode_string(key=key, data=encoded_stop.stop_name) if encoded_stop.stop_name else None
    )
