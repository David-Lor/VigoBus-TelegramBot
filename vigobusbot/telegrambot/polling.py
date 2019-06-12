
"""TELEGRAMBOT.POLLING
Ejecución del bot con el método Polling (no requiere servidor web).
Debe llamarse a 'start_polling' para comenzar su ejecución, y opcionalmente, si se quiere parar, a 'stop_polling'.
La función de 'stop_polling' se llama automáticamente cuando desde el Main se desea finalizar la ejecución
del hilo principal por señales de terminación.
Se utiliza un stop_event para que la función 'start_polling' (que funciona en bucle, para recuperarse ante fallos)
sepa cuándo detenerse.
"""

# Librerías nativas
from time import time
from threading import Event

# Librerías instaladas
from telebot import TeleBot
from telebot.apihelper import ApiException

# Proyecto
from vigobusbot.settings import config

__all__ = ("start_polling", "stop_polling")

__stop_event = Event()


def _get_error_delay(min_delay, max_delay, last, time_to_max):
    """Calcula el tiempo de delay al sucederse un error de polling.
    El tiempo de delay puede ser PollingErrorDelayMin o PollingErrorDelayMax
    Se toma el tiempo transcurrido entre el último fallo y el actual.
    Si el tiempo transcurrido es mayor/igual al PollingErrorTimeToMax, se devuelve el tiempo mínimo.
    Si el tiempo transcurrido es menor al PollingErrorTimeToMax, se devuelve el tiempo máximo.
    :param min_delay: Delay mínimo
    :param max_delay: Delay máximo
    :param last: Tiempo epoch del último error
    :return: Tiempo de delay a aplicar
    """
    diff = time() - last
    print(f"Diferencia entre los dos últimos errores: {diff} seg.")
    if time() - last >= time_to_max:
        # Pasó más tiempo del indicado: No hubo errores recientes
        return min_delay
    else:
        # Pasó poco tiempo: Hubo errores recientes
        return max_delay


def stop_polling(bot: TeleBot):
    """Para el polling del bot indicado.
    La parada puede tardar unos segundos en completarse, bloqueando el programa mientras tanto.
    :param bot: objeto TeleBot
    """
    __stop_event.set()
    bot.stop_polling()


def start_polling(bot: TeleBot):
    """Inicia el polling del bot indicado.
    Se ejecuta en primer plano, bloqueando el programa hasta que el polling finaliza.
    :param bot: objeto TeleBot
    """
    __stop_event.clear()
    interval = config.Telegram.PollingFreq
    timeout = config.Telegram.Timeout
    error_delay_min = config.Telegram.PollingErrorDelayMin
    error_delay_max = config.Telegram.PollingErrorDelayMax
    time_to_max = config.Telegram.PollingErrorTimeToMax
    last_error = time()

    while not __stop_event.is_set():
        # noinspection PyBroadException
        try:
            print(f"Polling iniciado con una frecuencia de {interval} s")
            bot.polling(none_stop=True, interval=interval, timeout=timeout)

        except KeyboardInterrupt:
            print("Interrupción manual del polling por KeyboardInterrupt")
            # stop_polling(bot)

        except (ApiException, IOError) as ex:
            error_delay = _get_error_delay(error_delay_min, error_delay_max, last_error, time_to_max)
            print(f"Error en polling:\n{ex}\nReiniciando en {error_delay} segundos")
            __stop_event.wait(error_delay)
            last_error = time()

        except Exception as ex:
            print(f"Error en polling:\n{ex}\nReiniciando en {error_delay_min} segundos")

        else:
            print("Interrupción manual del polling")

        finally:
            # Forzar finalización del polling antes de salir o reiniciar
            # De lo contrario puede reconectarse mientras todavía está en ejecución y entrar en bucle de errores
            stop_polling(bot)
