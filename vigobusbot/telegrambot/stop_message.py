
"""TELEGRAMBOT.STOP_MESSAGE
Generación, edición y tratamiento de los mensajes de paradas.
La clase StopMessage se utiliza para darle contexto a los mensajes de parada, al contar con un Inline Keyboard,
aunque los nuevos mensajes se generan de forma genérica en funciones Helpers.
Otras funciones trabajan con los callback_data asociados a los botones de los Inline Keyboard.
Se definen listas fijas de los códigos para usar en los callback_data, que se convierten a números por orden.
"""

# Librerías nativas
from typing import List, Union, Optional, Dict
from collections import namedtuple, OrderedDict

# Librerías instaladas
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pybuses import Bus, Stop
from pybuses.exceptions import *

# Proyecto
from vigobusbot.settings import config
from vigobusbot.clientdata import ClientsDB, DatabaseError

# Paquete
from .messages import messages
from .helpers import send_message, get_stop_custom_name, get_time


__all__ = ("OPERATIONS", "CALLBACK_FIELDS", "StopMessage", "generate_stops_markup", "decode_callback_data")

# Nombres de los códigos de operaciones
# Se envían en el callback_data como números, desde 0, según el índice en la tupla
# Resultan en la generación de una NamedTuple importable desde otros módulos
_operations_names = ("stop", "update", "save", "delete", "update_kb", "set_clientsdb", "rename")
_operations_namedtuple = namedtuple("Operations", _operations_names)
OPERATIONS = _operations_namedtuple(*range(len(_operations_names)))
CALLBACK_FIELDS = ("stopid", "operation", "buses_available", "all_buses", "all_buttons")  # TODO Implementarlo


class StopMessage(object):
    """Objeto base para generar mensajes Stop (paradas y sus buses en tiempo real),
    tanto para nuevos mensajes como actualizaciones.
    """
    def __init__(
            self,
            db: ClientsDB,
            stop: Stop,
            buses: List[Union[Bus, None]],
            chatid: Optional[int],
            all_buses: bool = False,
            all_buttons: bool = False
    ):
        """
        :param db: Objeto ClientsDB para acceder a las paradas guardadas de los usuarios
        :param stop: Objeto Stop de la parada a mostrar
        :param buses: Listado de objetos Bus, con los Buses que pasarán por esta parada.
                      Si sólo se necesita obtener el inline keyboard, este parámetro puede ser
                      una lista de None, tantos como buses hubiese en el mensaje a actualizar.
        :param chatid: ID del chat que solicitó el mensaje. Si el mensaje es inline, asignar None
        :param all_buses: mostrar todos los buses disponibles? (opcional, default = False)
        :param all_buttons: mostrar todos los botones disponibles? (opcional, default = False)
        :type stop: Stop
        :type buses: List[Bus]
        :type chatid: int
        :type all_buses: bool
        :type all_buttons: bool
        """
        self.db = db
        self.stop = stop
        self.buses = buses
        self.chatid = chatid
        self.buses_available = len(self.buses)
        self.all_buses = all_buses
        self.all_buttons = all_buttons

        # Aliases
        self.clientsdb = self.db
        self.userid = self.chatid
        self.stopid = self.stop.stopid

        # Obtener Stop Custom Name si existe, y guardarlo en stop.other
        if self.chatid:
            self.stop.other["custom_name"] = db.get_custom_stop_name(self.chatid, self.stopid)

    def generate_callback_data(self, operation: int = None, data: OrderedDict = None) -> str:
        """Generar código Callback Data (str) para cada uno de los botones generales del Inline Keyboard.
        Se puede proporcionar un OrderedDict con todos los datos pertinentes (útil para modificar parámetros).
        Si no se proporciona, se generará uno con los datos de este objeto.
        :param operation: código de operación (opcional, no necesario si se especifica 'data')
        :param data: OrderedDict con todos los atributos del CallbackData
                     (generado por método 'generate_callback_data_dict')
                     (opcional, si no se especifica se genera automáticamente con los atributos del objeto)
        :type operation: int, None
        :type data: OrderedDict, None
        :return: Callback Data como String, debidamente formateado para asociar a un botón de Inline Keyboard
        :rtype: str
        """
        if not data:
            data = self.generate_callback_data_dict(operation)
        return ",".join([str(x) for x in data.values()])

    def generate_callback_data_dict(self, operation: int) -> OrderedDict:
        """Genera un OrderedDict con el Callback Data, para poder modificarlo posteriormente.
        El método generate_callback_data, con este OrderedDict como atributo 'data', lo convierte en el string apropiado
        IMPORTANTE a la hora de modificar externamente los valores:
        - Los valores del diccionario deberían ser strings, pero se convierten automáticamente
          en el método 'generate_callback_data'.
        - Los booleanos deben convertirse a int para que sean 0/1.
        :param operation: código numérico de la operación asociada a este callback
        :type operation: int
        :return: OrderedDict con los datos del callback data
        :rtype: OrderedDict
        """
        return OrderedDict(  # TODO usar CALLBACK_FIELDS
            stopid=self.stopid,
            operation=operation,
            buses_available=self.buses_available,
            all_buses=int(self.all_buses),
            all_buttons=int(self.all_buttons)
        )

    def generate_text(self) -> str:
        """Genera el cuerpo (texto) del mensaje de parada con los datos de la clase.
        Se utilizarán la Stop, la lista de Buses (debe tener objetos Bus reales) y el parámetro
          all_buses, guardados en la clase.
        :return: texto del mensaje como String
        :rtype: str
        """
        msg = messages.get("stop_result")

        if len(self.buses) == 0:
            buses_text = msg.get("no_buses")
        else:
            buses_text = ""
            max_buses = config.TelegramMessages.BusLimit
            for index, bus in enumerate(self.buses):
                if not self.all_buses and index == max_buses:
                    break
                buses_text += msg.get("bus_item").format(
                    line=bus.line,
                    route=bus.route,
                    time=msg.get("bus_item_time").format(time=bus.time) if bus.time > 0 else msg.get("bus_item_time_0")
                )

        return msg.get("message").format(
            stopid=self.stop.stopid,
            stop_customname=get_stop_custom_name(self.stop),
            stopname=self.stop.name,
            bus_list=buses_text,
            update_timestamp=msg.get("timestamp").format(time=get_time())
        )

    def generate_inline_keyboard(self) -> InlineKeyboardMarkup:
        """Genera un Inline Keyboard con los parámetros del objeto.
        Se utilizarán la Stop, el número de elementos de la lista Buses, el chatid y los parámetros
        all_buses y all_buttons, guardados en la clase.
        :return: InlineKeyboardMarkup con los botones generados acorde a los datos de la clase
        :rtype: telebot.types.InlineKeyboardMarkup
        """
        row1, row2 = list(), list()
        txt = messages.get("inline_kb_buttons")

        # Botón Actualizar
        row1.append(InlineKeyboardButton(
            text=txt.get("stop_update"),
            callback_data=self.generate_callback_data(operation=OPERATIONS.update)
        ))

        # Botón Mostrar Todos Buses
        if not self.all_buses and self.buses_available > config.TelegramMessages.BusLimit:
            data = self.generate_callback_data_dict(operation=OPERATIONS.update)
            data["all_buses"] = 1
            row1.append(InlineKeyboardButton(
                text=txt.get("more_buses"),
                callback_data=self.generate_callback_data(data=data)
            ))

        # Por ahora, no vamos a usar un botón para mostrar/ocultar segunda row de botones
        # # Botón Mostrar Todos Botones
        # if not self.all_buttons:
        #     data = self.generate_callback_data_dict(OPERATIONS.update_kb)
        #     data["all_buttons"] = 1
        #     row1.append(InlineKeyboardButton(
        #         text=txt.get("more_buttons"),
        #         callback_data=self.generate_callback_data(data=data)
        #     ))
        # # Botón Ocultar segunda línea de botones
        # else:
        #     data = self.generate_callback_data_dict(OPERATIONS.update_kb)
        #     data["all_buttons"] = 0
        #     row2.append(InlineKeyboardButton(
        #         text=txt.get("less_buttons"),
        #         callback_data=self.generate_callback_data(data=data)
        #     ))

        # Botones Guardar/Eliminar parada
        if self.clientsdb:
            try:
                # Botón Guardar Parada
                if not self.clientsdb.is_stop_saved(self.userid, self.stopid):
                    data = self.generate_callback_data_dict(operation=OPERATIONS.save)
                    row1.append(InlineKeyboardButton(
                        text=txt.get("stop_save"),
                        callback_data=self.generate_callback_data(data=data)
                    ))

                # Botón Eliminar Parada
                else:
                    data = self.generate_callback_data_dict(operation=OPERATIONS.delete)
                    row1.append(InlineKeyboardButton(
                        text=txt.get("stop_delete"),
                        callback_data=self.generate_callback_data(data=data)
                    ))
                    # Botón Renombrar parada
                    data = self.generate_callback_data_dict(operation=OPERATIONS.rename)
                    row1.append(InlineKeyboardButton(
                        text=txt.get("stop_rename"),
                        callback_data=self.generate_callback_data(data=data)
                    ))
            except DatabaseError:
                pass

        # Generar markup y devolverlo
        markup = InlineKeyboardMarkup()
        markup.row(*row1)
        if row2:
            markup.row(*row2)
        return markup

    @staticmethod
    def send_new_message(
            bot: TeleBot,
            clients_db: ClientsDB,
            chatid: int,
            stop: Stop,
            buses: List[Bus]
    ) -> Union[Message, bool]:
        """Enviar un nuevo mensaje de Stop con los parámetros por defecto
        :param bot: objeto TeleBot
        :param clients_db: objeto ClientsDB
        :param chatid: ID del chat al que enviar mensaje
        :param stop: objeto Stop de la parada
        :param buses: lista de objetos Bus, con todos los buses disponibles en la parada
        :return: telebot.types.Message si se envió correctamente | False si hubo algún error (se imprime)
        """
        stop_message = StopMessage(
            stop=stop,
            buses=buses,
            chatid=chatid,
            db=clients_db
        )
        return send_message(
            bot=bot,
            text=stop_message.generate_text(),
            to=chatid,
            markup=stop_message.generate_inline_keyboard()
        )


def decode_callback_data(data: str) -> Dict:
    """Convierte un string con Callback Data a su representación como diccionario.
    Se utiliza en el callback handler para leer el callback data de un botón pulsado.
    Campos de Callback Data:
        - stopid (int)
        - operation (int, relacionado con namedtuple 'OPERATIONS')
        - buses_available (int)
        - all_buses (int -> 0/1)
        - all_buttons (int -> 0/1)
    :param data: Callback Data como String
    :type data: str
    :return: Dictionary
    :rtype: dict
    """
    data = data.split(",")
    return {  # TODO usar CALLBACK_FIELDS
        "stopid": int(data[0]),
        "operation": int(data[1]),
        "buses_available": int(data[2]),
        "all_buses": int(data[3]),
        "all_buttons": int(data[4])
    }


def generate_stops_markup(stops: List[Stop]) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for stop in stops:
        try:
            markup.row(InlineKeyboardButton(
                text=messages.get("/stops").get("stop_button").format(
                    stop_customname=get_stop_custom_name(stop),
                    stopname=stop.name,
                    stopid=stop.stopid
                ),
                callback_data=f"{stop.stopid},{OPERATIONS.stop},0,0,0,0,0,0,0,0,0"
            ))
        except StopException:
            pass
    return markup
