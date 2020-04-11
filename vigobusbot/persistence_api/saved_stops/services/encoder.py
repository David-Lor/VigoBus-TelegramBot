"""ENCODER
Functions to encode data from raw (Bot to Persist API)
"""

# # Native # #
import hashlib

# # Package # #
from .key_generator import *

# # Project # #
from vigobusbot.persistence_api.saved_stops.entities import SavedStop, SavedStopEncoded
from vigobusbot.settings_handler import persistence_settings as settings

__all__ = ("encode_user_id", "encode_stop", "encode_string")


def encode_user_id(user_id: int) -> str:
    sha512 = hashlib.sha512()
    sha512.update(settings.salt.encode())
    sha512.update(str(user_id).encode())
    return sha512.hexdigest()


def encode_string(data: str, key: Fernet) -> str:
    return key.encrypt(data.encode()).decode()


def encode_stop(raw_stop: SavedStop, user_id: int) -> SavedStopEncoded:
    key = get_user_key(user_id)
    return SavedStopEncoded(
        stop_id=raw_stop.stop_id,
        user_id=encode_user_id(user_id=user_id),
        stop_name=encode_string(key=key, data=raw_stop.stop_name) if raw_stop.stop_name else None
    )
