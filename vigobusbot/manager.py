
""" MANAGER
Aquí se instancian clases usadas por el resto del proyecto y se prepara el bot:
1) instancia las bases de datos SQLite donde guardar paradas
2) instancia PyBuses y se inicializa con todos sus getters-setters-deleters
3) instancia el bot de Telegram con pyTelegramBotApi
4) instancia la base de datos para datos de clientes (paradas guardadas)
5) registro de handlers del bot
"""

# Librerías instaladas
from telebot import TeleBot
from pybuses import PyBuses, SqliteDB

# Paquetes del proyecto
from vigobusbot.vigobusapi.getters import get_buses, get_stop
from vigobusbot.telegrambot import register_handlers
from vigobusbot.settings import config, join_data_dir
from vigobusbot.clientdata import ClientsDB


# PyBuses Core logging
import logging
logger = logging.getLogger("pybuses.core")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(0)
logger.addHandler(stream_handler)

#############################################
# INSTANCIACIONES CON CONFIGURACIONES
#############################################

# Telegram Bot
bot = TeleBot(config.Telegram.TOKEN)

# Sqlite (para PyBuses)
sqlite = SqliteDB(join_data_dir(config.Sqlite.File))

# ClientsDB (para bot Telegram)
clientsdb = ClientsDB(join_data_dir(config.ClientsDB.File), bool(config.ClientsDB.Encoded))

#############################################
# Instanciaciones SIN configuraciones
#############################################

# Objeto PyBuses
pybuses = PyBuses(use_all_stop_setters=True, auto_save_stop=True)

# Añadir Stop Getters
pybuses.add_stop_getter(sqlite.find_stop, online=False)
pybuses.add_stop_getter(get_stop, online=True)

# Añadir Bus Getters
pybuses.add_bus_getter(get_buses)

# Añadir Stop Setters
pybuses.add_stop_setter(sqlite.save_stop)

# Registro de bot handlers
register_handlers(bot=bot, pybuses=pybuses, clientsdb=clientsdb)
