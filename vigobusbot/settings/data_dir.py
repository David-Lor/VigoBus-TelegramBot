
"""
SETTINGS.DATA_DIR
Obtención del directorio donde se guarda la configuración (settings.ini) y las bases de datos SQLite.
El directorio predeterminado es la raíz de la aplicación Python (junto al __main__.py),
pero se puede definir una variable de entorno llamada 'DATA_DIR' con la ruta completa al directorio
donde almacenar la configuración y bases de datos.
Esto es útil, por ejemplo, al ejecutar el bot en un contenedor Docker, para utilizar un volumen persistente.
"""

# Librerías nativas
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(CURRENT_DIR, "..")


def get_data_dir() -> str:
    return os.environ.get("DATA_DIR", os.path.join(ROOT_DIR, "Data"))


def join_data_dir(file: str) -> str:
    return os.path.join(get_data_dir(), file)
