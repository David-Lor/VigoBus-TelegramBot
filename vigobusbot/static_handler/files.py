"""FILES CONTENT
Store content of files to be read; functions to update that content; filename variables
"""

# # Native # #
from typing import Optional

# # Installed # #
import addict

__all__ = ("get_messages", "set_messages", "MESSAGES_FILENAME")

MESSAGES_FILENAME = "messages.yaml"

__messages: Optional[addict.Dict] = None


def get_messages():
    return __messages


def set_messages(content: addict.Dict):
    global __messages
    __messages = content
