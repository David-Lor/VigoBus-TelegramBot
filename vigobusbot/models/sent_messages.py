from typing import Optional

from .base import BaseModel, Metadata, mapper
from vigobusbot.services import encryption


class SentMessageTypes:
    STOP = "stop"


class _SentMessageBase(BaseModel):
    message_type: str
    message_id: int

    # Fields provided from SentMessagePersist
    metadata: Metadata = None
    message_key: str = ""

    def is_expired(self, now: int, ttl_seconds: int) -> bool:
        return (now - self.published_on) >= ttl_seconds

    @property
    def published_on(self) -> int:
        return self.metadata.created_on.unix


class SentMessage(_SentMessageBase):
    message_text: str
    message_reply_markup_json: Optional[str] = None
    chat_id: int


class SentMessagePersist(_SentMessageBase):
    message_text_encrypted: str
    message_reply_markup_json_encrypted: Optional[str] = None
    chat_id_encoded: str
    chat_id_encrypted: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.complete_fields()

    def complete_fields(self):
        if not self.message_key:
            self.message_key = f"{self.message_type}_{self.chat_id_encoded}_{self.message_id}"
        if not self.metadata:
            self.metadata = Metadata(version=self.get_current_version())

    @classmethod
    def get_current_version(cls):
        return 1


@mapper.register(SentMessage, SentMessagePersist)
def _mapper_to_persist(_from: SentMessage) -> SentMessagePersist:
    user_id = _from.chat_id
    message_text = _from.message_text
    reply_markup_json = _from.message_reply_markup_json

    return SentMessagePersist(
        **_from.dict(),
        message_text_encrypted=encryption.encrypt_user_data(user_id, message_text),
        message_reply_markup_json_encrypted=encryption.encrypt_user_data(user_id, reply_markup_json) if reply_markup_json else None,
        chat_id_encoded=encryption.encode_user_id(user_id),
        chat_id_encrypted=encryption.encrypt_general_data(str(user_id)),
    )


@mapper.register(SentMessagePersist, SentMessage)
def _mapper_from_persist(_from: SentMessagePersist) -> SentMessage:
    user_id = int(encryption.decrypt_general_data(_from.chat_id_encrypted))
    return SentMessage(
        **_from.dict(),
        chat_id=user_id,
        message_text=encryption.decrypt_user_data(user_id, _from.message_text_encrypted),
        message_reply_markup_json=encryption.decrypt_user_data(user_id, _from.message_reply_markup_json_encrypted),
    )
