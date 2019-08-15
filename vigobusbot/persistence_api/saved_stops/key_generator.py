"""KEY GENERATOR
Generate Fernet keys based on a fixed Salt and a variable Value (generated from the User ID).
These keys are used to encode or decode persisted user data incoming/outcoming from/to the Persistance API.
"""

# # Native # #
import base64
import hashlib
import functools

# # Installed # #
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# # Project # #
from vigobusbot.settings_handler import persistence_settings as settings

__all__ = ("generate_fernet_key", "generate_user_hash")


@functools.lru_cache(maxsize=settings.cache_size, typed=False)
def generate_user_hash(user_id: int) -> str:
    """Generate the User Hash used as UserID on the Persistence API.
    """
    key = hashlib.sha256()
    steps = (
        settings.salt.encode(),
        str(user_id).encode()
    )
    if user_id % 2 == 0:
        steps = reversed(steps)
    for step in steps:
        key.update(step)
    return key.hexdigest()


@functools.lru_cache(maxsize=settings.cache_size, typed=False)
def generate_user_key(user_id: int) -> str:
    """Generate the User Key used to generate the Fernet Key for encode/decode user data on the Persistence API.
    """
    key = hashlib.sha512()
    steps = (
        settings.salt.encode(),
        str(user_id).encode()
    )
    if user_id % 2 != 0:
        steps = reversed(steps)
    for step in steps:
        key.update(step)
    return key.hexdigest()


@functools.lru_cache(maxsize=settings.cache_size, typed=False)
def generate_fernet_key(user_id: int) -> Fernet:
    """Generate the Fernet Key used to encode/decode the Saved Stop data (Stop ID and Stop Name) on the Persistence API.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=settings.salt.encode(),
        iterations=1000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(generate_user_key(user_id).encode()))
    return Fernet(key)
