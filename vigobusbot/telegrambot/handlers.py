
"""TELEGRAMBOT.HANDLERS
Los handlers procesan los mensajes y actualizaciones provenientes de clientes.
Todos los handlers son funciones con decoradores de pyTelegramBotAPI, y todos ellos están en
la función 'register_handlers' que debe llamarse ANTES de inicializar el bot, y provee las clases necesarias
para trabajar (el bot, PyBuses y la base de datos de clientes).
Se diferencian varios tipos de contenido:
- Mensajes: procesados por las funciones con decoradores 'message_handler'
- Pulsaciones sobre inline keyboard buttons (Callbacks): procesados por la función 'callback_handler'
"""

# Librerías nativas
import functools
import traceback

# Librerías instaladas
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from telebot.apihelper import ApiException
from pybuses import PyBuses
from pybuses.exceptions import *

# Proyecto
from vigobusbot.clientdata import ClientsDB
from vigobusbot.settings import config

# Paquete
from .messages import messages as msg
from .helpers import send_message, send_new_stop_message, update_stop_message
from .stop_message import StopMessage, decode_callback_data, generate_stops_markup, OPERATIONS

__all__ = ("register_handlers",)


def exceptions(function):
    """Decorador para capturar todas las excepciones producidas en los handlers y evitar que el programa principal
    rompa por una excepción en la consulta de un cliente.
    El decorador debe aplicarse de último (después de los decoradores de telebot)
    :param function: Función entrante
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        # noinspection PyBroadException
        try:
            return function(*args, **kwargs)
        except Exception:
            print(f"Error en Handler {function.__name__}:\n{traceback.format_exc()}")
    return wrapper


def register_handlers(bot: TeleBot, pybuses: PyBuses, clientsdb: ClientsDB):
    """Función contenedora de todas las funciones handlers del Bot de Telegram.
    Debe llamarse ANTES de comenzar la ejecución del bot de Telegram por polling o webhook.
    Es necesario asignar tres clases instanciadas para trabajar:
     - TeleBot: bot de Telegram para recibir y enviar mensajes y actualizaciones
     - PyBuses: para obtener los datos necesarios acerca de los buses y paradas
     - ClientsDB: para leer y escribir información de clientes en la base de datos (paradas guardadas)
    :param bot: objeto TeleBot
    :param pybuses: objeto PyBuses
    :param clientsdb: objeto ClientsDB
    """

    @bot.message_handler(commands=("start",))
    @exceptions
    def com_start(message: Message):
        send_message(bot, msg.get("/start"), to=message)
        send_message(bot, msg.get("/donate"), to=message.chat.id, preview_url=False)
        send_message(bot, msg.get("/stop").get("ask_for_stop"), to=message.chat.id)

    @bot.message_handler(commands=("help", "ayuda"))
    @exceptions
    def com_help(message: Message):
        send_message(bot, msg.get("/help"), to=message)

    @bot.message_handler(commands=("about", "acerca", "acercade"))
    @exceptions
    def com_help(message: Message):
        send_message(bot, msg.get("/about"), to=message)

    @bot.message_handler(commands=("donate", "donar", "donaciones", "aportar", "aportaciones"))
    @exceptions
    def com_donate(message: Message):
        send_message(bot, msg.get("/donate"), to=message)

    @bot.message_handler(commands=("feedback", "contacto", "contactar", "comentarios"))
    @exceptions
    def com_feedback(message: Message):
        text: str = message.text
        if len(text) < 15:
            # Se presume que se envió un comentario vacío
            send_message(bot, msg.get("/feedback").get("info"), to=message)
        else:
            # Se presume que es un mensaje válido que debe llegarle al Admin
            try:
                send_message(
                    bot=bot,
                    text=msg.get("/feedback").get("notify_admin").format(
                        text=text
                    ),
                    to=config.Telegram.Admin
                )
            except (ApiException, Exception):
                send_message(bot, msg.get("/feedback").get("notify_user_error"), to=message)
            else:
                send_message(bot, msg.get("/feedback").get("notify_user_success"), to=message)

    @bot.message_handler(commands=("stops", "paradas"))
    @exceptions
    def com_stops(message: Message):
        stops = clientsdb.get_stops(
            pybuses=pybuses,
            userid=message.chat.id
        )
        if not stops:
            # User no tiene paradas guardadas
            text = msg.get("/stops").get("no_stops_saved")
            markup = None
        else:
            # User tiene paradas guardadas
            text = msg.get("/stops").get("stops_saved").format(
                n_stops=len(stops),
                plural="s" if len(stops) > 1 else ""
            )
            markup = generate_stops_markup(stops)
        send_message(bot, text, to=message.chat.id, markup=markup)

    @exceptions
    def rename_stop_handler(message: Message, **kwargs):
        """Next Step Handler para las solicitudes de renombrado de paradas.
        """
        stopid: int = kwargs["stopid"]
        original_message: Message = kwargs["stop_message"]
        all_buses: bool = kwargs.get("all_buses", False)
        all_buttons: bool = kwargs.get("all_buttons", False)
        if message.text in ("/cancelar", "/volver", "/cancel"):
            # Cancelar operación
            return
        if message.text in ("/desnombrar", "/unname"):
            # Quitar nombre actualmente guardado
            name = None
        else:
            # Actualizar nombre
            name = message.text
            if len(name) > config.ClientsDB.CustomStopNameSizeLimit:
                # Nombre demasiado largo
                send_message(
                    bot=bot,
                    text=msg.get("saved_stop_name_too_long"),
                    to=message
                )
            elif not name:
                # Nombre vacío
                return
        # Nombre correcto o se quiere borrar nombre: guardar parada (se actualizará en DB)
        result = clientsdb.save_stop(
            userid=message.chat.id,
            stopid=stopid,
            custom_name=name
        )
        if result:
            try:
                update_stop_message(
                    bot=bot,
                    pybuses=pybuses,
                    clientsdb=clientsdb,
                    stopid=stopid,
                    message=original_message,
                    all_buses=all_buses,
                    all_buttons=all_buttons
                )
                # TODO mensajes de alerta en exito o error
            except GetterException:
                pass

    @bot.message_handler(func=lambda message: True)
    @exceptions
    def com_stop(message: Message):
        """Handler para todos los mensajes recibidos.
        Solicitudes de parada por comando o texto vacío.
        """
        query: str = message.text.replace("/stop", "").replace("/parada", "").strip()

        if query.isdigit():
            # User envió un ID de parada
            stopid = int(query)
            send_new_stop_message(
                pybuses=pybuses,
                bot=bot,
                source=message,
                stopid=stopid,
                clientsdb=clientsdb
            )

        elif len(query) == 0:
            # User envió el comando vacío
            send_message(bot, msg.get("/stop").get("ask_for_stop"), to=message)
            # bot.register_next_step_handler(msg_next_step_origin, com_stop)

        elif query[0] == "/":
            # User envió un comando no válido
            send_message(bot, msg.get("/stop").get("invalid_cmd"), to=message)

        elif len(query) < 3:
            # User envió menos de 3 caracteres, se interpreta como algo no válido
            send_message(bot, msg.get("/stop").get("syntax_error"), to=message)

        elif len(query) < 25:
            # User envió texto aparentemente válido, una parada a buscar por texto
            # Se limita el tamaño de la búsqueda a 25 caracteres para diferenciar entre búsquedas y mensajes random
            send_message(
                bot=bot,
                text="La búsqueda de paradas por texto todavía no ha sido implementada. Por favor, inténtalo de nuevo "
                     "introduciendo la ID de parada.",
                to=message
            )
            # TODO implementar búsqueda de paradas por texto
            # TODO límites y mínimos configurables

        else:
            # Resto de casos no detectados
            send_message(
                bot=bot,
                text=msg.get("/stop").get("invalid_cmd"),
                to=message
            )

    @bot.callback_query_handler(func=lambda call: True)
    @exceptions
    def callback_handler(callback: CallbackQuery):
        """Handler para las pulsaciones sobre botones de un Inline Keyboard.
        Campos de Callback Data:
            - stopid (int)
            - operation (int, relacionado con namedtuple 'OPERATIONS')
            - buses_available (int)
            - all_buses (int -> 0/1)
            - all_buttons (int -> 0/1)
        """
        print("Callback recibido:", callback.data)
        data = decode_callback_data(callback.data)
        message: Message = callback.message
        chatid: int = message.chat.id
        stopid: int = data.get("stopid", 0)
        operation: int = data.get("operation", -1)
        buses_available: int = data.get("buses_available", 0)
        all_buses = bool(data.get("all_buses", False))
        all_buttons = bool(data.get("all_buttons", False))

        try:
            if operation == OPERATIONS.stop:  # New Stop
                # Enviar un nuevo mensaje de Stop
                send_new_stop_message(
                    bot=bot,
                    pybuses=pybuses,
                    clientsdb=clientsdb,
                    source=chatid,
                    stopid=stopid,
                    send_message_on_error=False
                )

            elif operation == OPERATIONS.update:  # Update Stop Message
                update_stop_message(
                    bot=bot,
                    pybuses=pybuses,
                    clientsdb=clientsdb,
                    message=message,
                    stopid=stopid,
                    all_buses=all_buses,
                    all_buttons=all_buttons
                )

            elif operation in (OPERATIONS.save, OPERATIONS.delete):
                # Guardar o Borrar una Stop guardada
                stop_saved = clientsdb.is_stop_saved(chatid, stopid)

                if operation == OPERATIONS.save and not stop_saved:  # Save Stop
                    clientsdb.save_stop(chatid, stopid)
                elif operation == OPERATIONS.delete and stop_saved:  # Delete Stop
                    clientsdb.delete_stop(chatid, stopid)

                stop_message = StopMessage(
                    db=clientsdb,
                    stop=pybuses.find_stop(stopid),
                    buses=[None] * buses_available,  # Dummy Bus list
                    chatid=chatid,
                    all_buses=all_buses,
                    all_buttons=all_buttons
                )
                bot.edit_message_reply_markup(
                    chat_id=chatid,
                    message_id=message.message_id,
                    reply_markup=stop_message.generate_inline_keyboard()
                )

            elif operation == OPERATIONS.rename and clientsdb.is_stop_saved(chatid, stopid):
                message = send_message(
                    bot=bot,
                    text=msg.get("ask_saved_stop_name").format(
                        stop_id=stopid,
                        stop_name=pybuses.find_stop(stopid).name
                    ),
                    to=chatid
                )
                bot.register_next_step_handler(
                    message=message,
                    callback=rename_stop_handler,
                    stopid=stopid,
                    stop_message=message
                )

        except StopNotExist:
            # La parada ya no existe
            bot.answer_callback_query(
                callback_query_id=callback.id,
                text=msg["/stop"]["not_found"].format(stopid=stopid),
                show_alert=True
            )

        except (StopException, BusException, Exception) as ex:
            # No se han podido recuperar los buses o la parada
            bot.answer_callback_query(
                callback_query_id=callback.id,
                text=msg["/stop"]["generic_error"],
                show_alert=True
            )
            if type(ex) not in (StopException, BusException):
                print(f"Error en Callback Handler: {traceback.format_exc()}")

        finally:
            # Quitar icono de Cargando en botón del cliente
            bot.answer_callback_query(callback.id)
