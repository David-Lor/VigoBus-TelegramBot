
"""TELEGRAMBOT.HELPERS
Funciones complementarias a los handlers para enviar datos a clientes, como enviar o actualizar mensajes de paradas.
"""

# Librerías nativas
from typing import Union, List
from datetime import datetime
from threading import Thread

# Librerías instaladas
from pybuses import PyBuses, Stop, Bus
from pybuses.exceptions import *
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telebot.apihelper import ApiException

# Paquete
from .messages import messages as msg

# Proyecto
from vigobusbot.clientdata import ClientsDB
from vigobusbot.settings import config

__all__ = ("send_message", "send_new_stop_message", "update_stop_message", "get_stop_custom_name", "get_time")


def send_message(
        bot: TeleBot,
        text: str,
        to: Union[int, Message],
        markdown: bool = True,
        html: bool = False,
        markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup] = None,
        reply: bool = True,
        edit: bool = False,
        preview_url: bool = True
) -> Union[Message, bool]:
    """Envía un mensaje o respuesta simple, con posibilidad de formateo Markdown/HTML y otras opciones,
    acortando el código en otras secciones al necesitar enviar un mensaje.
    Por defecto, el mensaje se envía con formato Markdown, y sólo es necesario indicar bot, texto y destinatario
    ó mensaje al que responder.
    :param bot: objeto TeleBot que usar para enviar el mensaje
    :param text: texto del mensaje
    :param to: Mensaje o ChatID al que enviar el mensaje.
               Si se proporciona un Mensaje, se responderá al mismo, salvo que reply sea False
    :param markdown: si es True, utilizar Markdown para formatear el mensaje
    :param html: si es True, utilizar HTML para formatear el mensaje. Markdown a True reemplaza este parámetro
    :param markup: InlineKeyboardMarkup o ReplyKeyboardMarkup que adjuntar al mensaje
    :param reply: si es True, responder al Mensaje proporcionado en 'to'; en caso contrario, enviar mensaje normal
    :param edit: si es True, edita el mensaje en lugar de enviarlo (en cuyo caso, el parámetro 'to' DEBE ser un Message)
    :param preview_url: si es False, deshabilita la previsualización de enlaces (default=True)
    :type bot: TeleBot
    :type text: str
    :type to: telebot.types.Message or int
    :type markdown: bool
    :type html: bool
    :type markup: telebot.types.InlineKeyboardMarkup or telebot.types.ReplyKeyboardMarkup
    :type reply: bool
    :type edit: bool
    :type preview_url: bool
    :return: Message enviado si se envió correctamente | False si hubo algún error (además, se imprime)
    :rtype: Message, false
    """
    chatid = None
    reply_to = None
    if isinstance(to, Message):
        chatid = to.chat.id
        reply_to = to.message_id
    elif isinstance(to, int):
        chatid = to
    parse_mode = None
    if markdown:
        parse_mode = "Markdown"
    elif html:
        parse_mode = "HTML"
    try:
        if not edit:
            return bot.send_message(
                chat_id=chatid,
                reply_to_message_id=reply_to if reply else None,
                parse_mode=parse_mode,
                text=text,
                reply_markup=markup,
                disable_web_page_preview=not preview_url
            )
        else:
            return bot.edit_message_text(
                chat_id=chatid,
                message_id=to.message_id,
                text=text,
                reply_markup=markup,
                parse_mode=parse_mode,
                disable_web_page_preview=not preview_url
            )
    except ApiException as ex:
        print(f"Error enviando mensaje:\n{ex}")
        return False


class ThreadResult(object):
    """Objeto utilizado por los hilos __get_stop_buses_threadable para depositar los resultados de las búsquedas
    de paradas y sus buses, o en su defecto, la excepción producida al realizar las consultas a los Getters.
    El método thread_finished se utiliza para comprobar si la ejecución del hilo finalizó,
    ya que deben de estar cubiertos los atributos stop y buses, o exception si se produjo un error
    """
    # noinspection PyTypeChecker
    def __init__(self, bot: TeleBot, chatid: int):
        self.bot: TeleBot = bot
        self.chatid: int = chatid
        self.thread: Thread = None
        self.stop: Stop = None
        self.buses: List[Bus] = None
        self.exception: Exception = None

    def set_thread(self, thread: Thread):
        self.thread = thread

    def set_stop(self, stop: Stop):
        self.stop = stop

    def set_buses(self, buses: List[Bus]):
        self.buses = buses

    def set_exception(self, exception: Exception):
        self.exception = exception

    def thread_finished(self):
        return (self.stop is not None and self.buses is not None) or (self.exception is not None)

    def start(self):
        self.thread.start()
        start = datetime.now()
        while not self.thread_finished():
            # Main Timeout para no exceder el timeout de respuesta ante un inline keyboard button Callback
            if (datetime.now() - start).seconds > config.API.Timeout:
                self.exception = GetterException("Timeout on ThreadResult join")
            else:
                self.bot.send_chat_action(self.chatid, "typing")  # Chat actions end after 5 seconds
                self.thread.join(timeout=4)


def __get_stop_buses_threadable(pybuses: PyBuses, stopid: int, thread_result: ThreadResult):
    """Función que se ejecutará en un hilo cuando se quiera generar un mensaje de Stop.
    La función en hilo buscará la parada y sus buses con los Getters. Mediante un hilo, se puede enviar al cliente
    el estado 'escribiendo' en Telegram mientras la API no responde, hasta que se obtenga resultado o surja un error
    (previsiblemente un Timeout).
    :param pybuses: objeto PyBuses
    :param stopid: ID de la parada a buscar
    :param thread_result: objeto ThreadResult donde depositar los resultados
    """
    try:
        stop = pybuses.find_stop(stopid)
        buses = pybuses.get_buses(stopid)
    except GetterException as ex:
        thread_result.set_exception(ex)
    else:
        thread_result.set_stop(stop)
        thread_result.set_buses(buses)


def get_stop_buses_thread(bot: TeleBot, chatid: int, pybuses: PyBuses, stopid: int) -> ThreadResult:
    """Creación de un hilo que ejecutará la función __get_stop_buses_threadable para obtener la parada y sus buses
    en un hilo, de forma que se puede enviar al cliente el estado 'escribiendo' en Telegram mientras la API no responde,
    hasta que se obtenga resultado o surja un error (previsiblemente un Timeout).
    Se devuelve una instancia de ThreadResult, que contiene el hilo como thread_result.thread.
    Los resultados se depositarán en thread_result.stop y thread_result.buses - si se produce algún error, la excepción
    se depositará en thread_result.exception.
    :param bot: objeto TeleBot
    :param chatid: ID del chat solicitante
    :param pybuses: objeto PyBuses
    :param stopid: ID de la parada
    :return: instancia de clase ThreadResult (propia de este módulo)
    """
    thread_result = ThreadResult(bot=bot, chatid=chatid)
    thread = Thread(
        target=__get_stop_buses_threadable,
        daemon=True,
        kwargs={
            "pybuses": pybuses,
            "stopid": stopid,
            "thread_result": thread_result
        }
    )
    thread_result.set_thread(thread)
    return thread_result


def send_new_stop_message(
        bot: TeleBot,
        pybuses: PyBuses,
        clientsdb: ClientsDB,
        source: Union[Message, int],
        stopid: int,
        send_message_on_error: bool = True
):
    """Envía un mensaje de Stop al solicitarlo por parte de un cliente.
    Se responderá debidamente en el caso de que la parada no exista o no sea posible obtenerla,
    excepto que 'send_message_on_error' sea False, en cuyo caso se lanzará la excepción pertinente.
    :param bot: objeto Telebot
    :param pybuses: objeto PyBuses
    :param clientsdb: objeto ClientsDB
    :param source: Message o ChatID que solicitó el mensaje de Stop.
                   Si se proporciona Message, se responderá al mismo.
                   Si se proporciona ChatID (int), se enviará un mensaje independiente.
    :param stopid: ID de la parada solicitada
    :param send_message_on_error: si es True, envía un mensaje en caso de error por parada no existente
                                  o Getter fallido. Si es False, lanza las excepciones pertinentes al origen.
    :type bot: TeleBot
    :type pybuses: PyBuses
    :type clientsdb: ClientsDB
    :type source: telebot.types.Message | int
    :type stopid: int
    :type send_message_on_error: bool
    :raises: StopNotExist | StopException | BusException (si send_message_on_error=False)
    """
    chatid = source.chat.id if isinstance(source, Message) else source
    thread_result = get_stop_buses_thread(bot=bot, chatid=chatid, pybuses=pybuses, stopid=stopid)
    thread_result.start()  # Block hasta que no encuentre parada o salte error

    try:
        if thread_result.exception:
            raise thread_result.exception

    except StopNotExist as ex:
        # Parada no existe
        if send_message_on_error:
            send_message(bot, msg["/stop"]["not_found"].format(stopid=stopid), to=source)
        else:
            raise ex

    except (StopException, BusException) as ex:
        # Problema al obtener parada o buses
        if isinstance(ex, StopException):
            print(f"Error obteniendo parada {stopid} para responder a solicitud de Stop:\n{ex}")
        elif isinstance(ex, BusException):
            print(f"Error obteniendo buses en la parada {stopid} para responder a solicitud de Stop:\n{ex}")

        if send_message_on_error:
            send_message(bot, msg["/stop"]["generic_error"], to=source)
        else:
            raise ex

    else:
        # Parada existente, buses obtenidos sin problemas
        from .stop_message import StopMessage
        StopMessage.send_new_message(
            bot=bot,
            clients_db=clientsdb,
            chatid=chatid,
            stop=thread_result.stop,
            buses=thread_result.buses
        )


def update_stop_message(
        bot: TeleBot,
        pybuses: PyBuses,
        clientsdb: ClientsDB,
        stopid: int,
        message: Message,
        all_buses: bool,
        all_buttons: bool
):
    """Actualiza un mensaje de Stop previamente enviado a un cliente, cuando éste solicita su actualización
    o se realiza una acción que deba actualizar el mensaje completo.
    Si la parada no existe o no es posible obtenerla, se lanzarán las excepciones pertinentes.
    :param bot: objeto Telebot
    :param pybuses: objeto PyBuses
    :param clientsdb: objeto ClientsDB
    :param stopid: ID de la parada solicitada
    :param message: objecto Message que se va a actualizar
    :param all_buses: estado contextual de all_buses (mostrar todos los buses disponibles?)
    :param all_buttons: estado contextual de all_buttons (mostrar todos los botones del inline keyboard?)
    :type bot: TeleBot
    :type pybuses: PyBuses
    :type clientsdb: ClientsDB
    :type stopid: int
    :type message: telebot.types.Message
    :type all_buttons: bool
    :type all_buses: bool
    :raises: StopNotExist | StopException | BusException
    """
    chatid = message.chat.id
    thread_result = get_stop_buses_thread(bot=bot, chatid=chatid, pybuses=pybuses, stopid=stopid)
    thread_result.start()

    if thread_result.exception:
        raise thread_result.exception

    else:
        from .stop_message import StopMessage
        stop_message = StopMessage(
            db=clientsdb,
            stop=pybuses.find_stop(stopid),
            buses=pybuses.get_buses(stopid),
            chatid=message.chat.id,
            all_buses=all_buses,
            all_buttons=all_buttons
        )
        send_message(
            bot=bot,
            text=stop_message.generate_text(),
            edit=True,
            to=message,
            markup=stop_message.generate_inline_keyboard()
        )


# def answer_callback_query(bot: TeleBot, callback_query_id: int, text: str, alert: bool = False):
#     """Responde a una callback query enviando un mensaje o alerta al cliente.
#     Las respuestas normales son un mensaje en la parte superior del chat.
#     Las alertas son popups con un mensaje y un botón para cerrarlo.
#     :param bot: objeto TeleBot
#     :param callback_query_id: ID de la Callback Query
#     :param text: Texto que enviar
#     :param alert: si es True, se envía la respuesta como Alert (default=False)
#     """
#     bot.answer_callback_query(
#         callback_query_id=callback_query_id,
#         text=text,
#         show_alert=alert
#     )

def get_stop_custom_name(stop: Stop) -> str:
    """A partir de una parada devuelta por ClientsDB (siendo una parada guardada de un usuario),
    devuelve el Custom Name de esa parada, si existe (concatenado con un guión flanqueado por espacios),
    o un string vacío si no existe.
    :param stop: parada devuelta por métodos que devuelven paradas guardadas desde ClientsDB
    :type stop: pybuses.Stop
    :return: string para concatenar en mensajes a enviar
    :rtype: str
    """
    if isinstance(stop.other, dict) and stop.other.get("custom_name"):
        return stop.other["custom_name"] + " - "
    else:
        return ""


def get_time() -> str:
    """Obtención de la fecha/hora actual como string, conforme al formateo declarado en la configuración.
    Este timestamp se usa para mostrar a clientes la fecha y hora de actualización de los mensajes con listas de buses.
    :return: fecha-hora como string
    :rtype: str
    """
    return datetime.now().strftime(config.TelegramMessages.BusLastUpdateFormat)
