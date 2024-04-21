"""KEY GENERATOR
Generate keys to decode read data & encode data to write, from and into the Persist API
"""

# # Native # #
import hashlib
import base64

# # Installed # #
import cachetools
from cryptography.fernet import Fernet

# # Project # #
from vigobusbot.settings_handler import persistence_settings as settings

__all__ = ("get_user_key", "Fernet")

_key_cache = cachetools.LFUCache(maxsize=settings.key_cache_size)
"""Storage for keys generated for the users
Key=user_id (raw - int)
Value=Fernet object
"""


def get_user_key(user_id: int) -> Fernet:
    """Generate/get the Fernet key object for the given user.
    The key is generated from the MD5 of the fixed-salt set on Persistence Settings, and the given User ID.
    Generated keys are stored on a local LFU Cache.
    """
    try:
        return _key_cache[user_id]

    except KeyError:
        md5 = hashlib.md5()
        md5.update(settings.encryption_key.encode())
        md5.update(str(user_id).encode())

        key: bytes = base64.urlsafe_b64encode(md5.hexdigest().encode())
        fernet_key = Fernet(key)
        _key_cache[user_id] = fernet_key
        return fernet_key
