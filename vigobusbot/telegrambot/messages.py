
"""TELEGRAMBOT.MESSAGES
Lectura del fichero de mensajes, 'messages.json', que contiene los textos de todos los mensajes
y contenidos enviados a los clientes por parte del bot.
"""

# Librerías nativas
import json
from typing import Dict

# Proyecto
from vigobusbot.settings import join_data_dir

__all__ = ("messages",)


MESSAGES_FILENAME = "messages.json"

with open(join_data_dir(MESSAGES_FILENAME), "r") as file:
    messages: Dict = json.load(file)
