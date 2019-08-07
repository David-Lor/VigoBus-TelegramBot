"""PARSERS
Parsers for files previously opened
"""

# # Native # #
from typing import TextIO

# # Installed # #
import yaml
import addict
import emoji

__all__ = ("parse_yaml_file", "parse_emojis")


def parse_yaml_file(content: str) -> addict.Dict:
    """Given the string content of a YAML file, use pyyaml to read and parse it, and convert it to an addict Dict.
    """
    yaml_loaded = yaml.load(content, Loader=yaml.Loader)
    assert type(yaml_loaded) is dict, "YAML file is not valid! Should be a dictionary!"
    return addict.Dict(yaml_loaded)


def parse_emojis(content: str) -> str:
    """Given a string content, use emoji lib to parse the emojis inserted with their aliases:
    https://www.webfx.com/tools/emoji-cheat-sheet/
    """
    return emoji.emojize(content, use_aliases=True)
