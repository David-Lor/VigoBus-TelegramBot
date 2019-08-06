"""PARSERS
Parsers for files previously opened
"""

# # Native # #
from typing import TextIO

# # Installed # #
import yaml
import addict


def parse_yaml_file(file: TextIO) -> addict.Dict:
    """Given a loaded YAML file, use pyyaml to read and parse it, and convert it to an addict Dict.
    """
    yaml_loaded = yaml.load(file, Loader=yaml.Loader)
    assert type(yaml_loaded) is dict, "YAML file is not valid! Should be a dictionary!"
    return addict.Dict(yaml_loaded)
