
"""SETTINGS
Carga de las configuraciones del bot, almacenadas en settings.ini.
Las configuraciones son accesibles desde 'config', que actúa como clase con atributos,
siendo éstos las categorías y valores del fichero de configuración INI.
(p.ej. para acceder a Telegram > PollingFreq, usar config.Telegram.PollingFreq)
También contiene la función get_data_dir que devuelve la ruta al directorio de datos, que puede ser
la raíz del proyecto o una ruta personalizada si la variable de entorno 'DATA_DIR' existe.
"""

# Librerías nativas
from collections import namedtuple

# Paquete
from .settings import SettingsDict
from .settings import config as _config
from .data_dir import get_data_dir, join_data_dir


__all__ = ("config", "ConfigTuple", "get_data_dir", "join_data_dir")

# Esqueleto ConfigTuple
ConfigTuple = namedtuple("Settings", _config.keys())

# List con las Sections del ConfigFile
# p.ej. [Telegram, API]
_config_values = [SettingsDict(value) for value in _config.values()]

# ConfigTuple con las secciones y sus parámetros
# p.ej. config.Telegram.PollingFreq, config.API.URL, config.Mongo.Host
config = ConfigTuple(*_config_values)
