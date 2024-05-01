import hashlib
from typing import Optional

from .base import mapper, BaseModel, BaseMetadataedModel
from .stops_buses import Stop
from vigobusbot.services import encryption

__all__ = ("SavedUserStop", "SavedUserStopPersist")


class _SavedUserStopBase(BaseModel):
    stop_id: int
    stop_name: Optional[str] = None


class SavedUserStop(_SavedUserStopBase):
    # Fields not always passed
    user_id: Optional[int] = None
    """Only passed on create, since it is encoded and cannot be decoded."""
    stop: Optional[Stop] = None
    """Associated Stop object. Assigned after retrieving from the repository, for formatting the message."""


class SavedUserStopPersist(_SavedUserStopBase, BaseMetadataedModel):
    stop_id: int
    """Stop ID; raw/original."""
    user_id: str
    """User ID; encoded"""
    stop_name: Optional[str] = None
    """Custom user stop name, if any; encrypted"""

    @property
    def key(self) -> str:
        md5 = hashlib.md5()
        md5.update(self.user_id.encode())
        md5.update(str(self.stop_id).encode())
        return md5.hexdigest()

    @classmethod
    def get_current_version(cls):
        return 1


@mapper.register(SavedUserStop, SavedUserStopPersist)
def _mapper_to_persist(_from: SavedUserStop) -> SavedUserStopPersist:
    return SavedUserStopPersist(
        stop_id=_from.stop_id,
        user_id=encryption.encode_user_id(_from.user_id),
        stop_name=encryption.encrypt_user_data(_from.user_id, _from.stop_name) if _from.stop_name else None
    )


@mapper.register(SavedUserStopPersist, SavedUserStop)
def _mapper_from_persist(_from: SavedUserStopPersist, user_id: int) -> SavedUserStop:
    return SavedUserStop(
        stop_id=_from.stop_id,
        stop_name=encryption.decrypt_user_data(user_id, _from.stop_name) if _from.stop_name else None
    )
