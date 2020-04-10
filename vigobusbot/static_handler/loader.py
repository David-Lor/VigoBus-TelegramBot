"""LOADER
Load, read and parse static files from the 'static' path
"""

# # Native # #
import json

# # Package # #
from .files import set_messages, MESSAGES_FILENAME
from .path_loader import get_static_path
from .parsers import parse_yaml_file, parse_emojis

# # Project # #
from vigobusbot.logger import *

__all__ = ("load_messages", "static_path")

static_path = get_static_path()


def load_messages():
    file_path = static_path.joinpath(MESSAGES_FILENAME)
    logger.debug(f"Found Messages file at {file_path}")

    with open(str(file_path), "r") as file:
        content = parse_emojis(file.read())
        messages_content = parse_yaml_file(content)
        logger.debug(f"Parsed Messages file:\n{json.dumps(messages_content, indent=2)}")

    set_messages(messages_content)
