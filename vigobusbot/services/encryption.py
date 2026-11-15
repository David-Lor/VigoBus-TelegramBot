"""ENCRYPTION
Functions for encrypting/decrypting and encoding sensitive data to be persisted.

Encrypting/decrypting: bidirectional way of storing data.
Encoding: unidirectional way of storing data (from raw to encoded), using hashes.
"""

import hashlib
import base64

import cachetools
from cryptography.fernet import Fernet

from vigobusbot.logger import logger
from vigobusbot.settings import PersistenceSettings, SettingsLoadedSignal
from vigobusbot.utils import SingletonHold


_user_keys_cache: SingletonHold[cachetools.Cache[int, Fernet]] = SingletonHold()
"""Local cache for keys generated for the users.
Key=user_id (raw - int)
Value=Fernet object
"""

_general_key_cache: SingletonHold[Fernet] = SingletonHold()
"""Local cache for the general key."""


@SettingsLoadedSignal.connect
def _on_settings_loaded(*_, **__):
    cache = cachetools.LFUCache(maxsize=PersistenceSettings.get().key_cache_size)
    _user_keys_cache.set_value(cache)
    logger.bind(cache_maxsize=cache.maxsize).debug("Initialized Encryption-UserKeys cache")


def encode_user_id(user_id: int) -> str:
    sha512 = hashlib.sha512()
    sha512.update(PersistenceSettings.get().encryption_key.encode())
    sha512.update(str(user_id).encode())
    return sha512.hexdigest()


def encrypt_user_data(user_id: int, data: str) -> str:
    return _get_user_encryption_key(user_id).encrypt(data.encode()).decode()


def encrypt_general_data(data: str) -> str:
    return _get_general_encryption_key().encrypt(data.encode()).decode()


def decrypt_user_data(user_id: int, encrypted_data: str) -> str:
    return _get_user_encryption_key(user_id).decrypt(encrypted_data.encode()).decode()


def decrypt_general_data(encrypted_data: str) -> str:
    return _get_general_encryption_key().decrypt(encrypted_data.encode()).decode()


def _get_user_encryption_key(user_id: int) -> Fernet:
    """Generate/get the Fernet key object for the given user.
    The key is generated from the MD5 of the encryption key set on Persistence Settings, and the given User ID.
    Generated keys are stored on a local cache.
    """
    if (cache := _user_keys_cache.get_value()) is not None:
        if fernet_key := cache.get(user_id):
            return fernet_key

    md5 = hashlib.md5()
    md5.update(PersistenceSettings.get().encryption_key.encode())
    md5.update(str(user_id).encode())

    fernet_key = _generate_fernet_key(md5.hexdigest())
    if cache is not None:
        cache[user_id] = fernet_key
    return fernet_key


def _get_general_encryption_key() -> Fernet:
    """Generate/get the Fernet key object for general values.
    The key is generated from the key configured in PersistenceSettings.
    Generated key is stored on a local cached variable.
    """
    if (fernet_key := _general_key_cache.get_value()) is None:
        md5 = hashlib.md5()
        md5.update(PersistenceSettings.get().encryption_key.encode())

        fernet_key = _generate_fernet_key(md5.hexdigest())
        _general_key_cache.set_value(fernet_key)

    return fernet_key


def _generate_fernet_key(key: str) -> Fernet:
    return Fernet(base64.urlsafe_b64encode(key.encode()))
