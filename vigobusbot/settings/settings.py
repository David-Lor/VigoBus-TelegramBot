
# Librerías nativas
import os
from configparser import ConfigParser

# Paquete
from .data_dir import get_data_dir

CONFIG_FILENAME = "settings.ini"
CONFIG_FILE_DIR = os.path.join(get_data_dir(), CONFIG_FILENAME)


class SettingsDict(dict):
    def __init__(self, d):
        super().__init__(d)
        for key, value in d.items():  # type: str, str
            if value.replace('.', '', 1).isdigit():
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            self.__setattr__(key, value)

    def __getattr__(self, val: str):
        return self[val]


config: ConfigParser = ConfigParser()
config.optionxform = str
config.read(CONFIG_FILE_DIR)
