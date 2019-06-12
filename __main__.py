
""" MAIN
Ejecución principal del proyecto.
Los imports de manager inicializan todo lo necesario.
La ejecución del bot en polling o webhook se mantiene en ejecución en el hilo principal, desde aquí.
"""

# Librerías nativas
import signal

# Paquetes del proyecto
from vigobusbot.telegrambot import start_polling, stop_polling

# Módulos del proyecto
# Se inicializan todas las configuraciones al realizar este import
from vigobusbot.manager import bot


# Sigint
# noinspection PyUnusedLocal
def signal_handler(signum, frame):
    """Listener de signals SIGINT/SIGTERM, llamando a stop_polling para finalizar la ejecución del bot
    cuando se finaliza la ejecución del programa.
    """
    stop_polling(bot)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Ejecución del bot, en hilo principal
    start_polling(bot)
