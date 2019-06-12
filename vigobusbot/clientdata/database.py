
""" CLIENTDATA.DATABASE
Gestión de la base de datos SQLite que almacena los datos de clientes.
Contiene la clase ClientsDB y las sentencias SQL para trabajar con la base de datos.
Los métodos de acceso y escritura de datos pueden lanzar excepciones DatabaseError
  de sqlite3 si se produce cualquier error.

ESTRUCTURA BASE DE DATOS SQLITE
IDs de clientes: generados

a) Tabla stops
     Paradas guardadas por clientes
   Campos:
     * user: int (text para encoded)
     * stopid: int (NO se encodea)
     * name: text (default: NULL)
   Encode:
     * user: sha256 hexdigest (string) desde función 'hash_userid' de encoding.py
     * stopid: sin encodear
     * name: función 'encrypt' de encoding.py, usando la key generada desde función 'hash_userid_to_key'

"""

# Librerías nativas
import sqlite3
import atexit
from sqlite3 import DatabaseError
from threading import Lock
from typing import List, Optional, Tuple

# Librerías instaladas
from pybuses import Stop, StopException, PyBuses

# Paquete
from .encoding import *

__all__ = ("ClientsDB", "DatabaseError")


_STOPS_TABLE_CREATE_NOT_ENCODED = """CREATE TABLE IF NOT EXISTS stops(
    user INTEGER NOT NULL,
    stopid INTEGER NOT NULL,
    name TEXT DEFAULT NULL,
    PRIMARY KEY (user, stopid)
)"""
_STOPS_TABLE_CREATE_ENCODED = """CREATE TABLE IF NOT EXISTS stops(
    user TEXT NOT NULL,
    stopid INTEGER NOT NULL,
    name TEXT DEFAULT NULL,
    PRIMARY KEY (user, stopid)
)"""
_SAVE_STOP = """REPLACE INTO stops(user, stopid, name) VALUES (?,?,?)"""
_DELETE_STOP = """DELETE FROM stops WHERE user=? AND stopid=?"""
_UPDATE_STOP_NAME = """UPDATE stops SET name=? WHERE user=? AND stopid=?"""
_SELECT_ALL_STOPS = """SELECT stopid, name FROM stops WHERE user=?"""
_IS_STOP_SAVED = """SELECT COUNT(stopid) FROM stops WHERE user=? AND stopid=?"""
_SELECT_CUSTOM_STOPNAME = """SELECT name FROM stops WHERE user=? AND stopid=?"""


class ClientsDB(object):
    """Clase que trabaja con los datos de clientes (paradas guardadas).
    Debe inicializarse con una ruta a una base de datos SQLite, que se creará si no existe.
    Los datos pueden estar codificados en la base de datos.
    Las consultas pueden lanzar excepciones DatabaseError de sqlite3.
    """
    def __init__(self, filename: str, encoded: bool):
        """
        :param filename: nombre del fichero de base de datos Sqlite
        :param encoded: codificar datos?
        :type filename: str
        :type encoded: bool
        """
        self.filename = filename
        self.encoded = encoded
        self.lock = Lock()
        self.db: sqlite3.Connection = None

        try:
            self.connect()
        except sqlite3.DatabaseError as ex:
            print(f"No se pudo conectar la base de datos de Clientes:\n{ex}")
            self.disconnect()
        else:
            atexit.register(self.disconnect)

        # Alias
        self.close = self.disconnect

    def connect(self):
        """Conectarse a la base de datos Sqlite. La instancia de conexión se guarda en self.db.
        Las tablas se crean automáticamente en la base de datos si no existen.
        :raise: excepciones de Sqlite3
        """
        self.db = sqlite3.connect(self.filename, check_same_thread=False)
        cursor = self.db.cursor()
        if self.encoded:
            cursor.execute(_STOPS_TABLE_CREATE_ENCODED)
        else:
            cursor.execute(_STOPS_TABLE_CREATE_NOT_ENCODED)
        self.db.commit()
        cursor.close()
        print("Base de datos Sqlite3 de Clientes conectada")

    def disconnect(self):
        """Desconexión de la base de datos. Se ignoran errores o que la base de datos no esté inicializada.
        """
        if isinstance(self.db, sqlite3.Connection):
            try:
                self.db.close()
            except sqlite3.Error:
                pass
            self.db = None
            print("Base de datos Sqlite3 de Clientes desconectada")

    def __get_uid_key(self, userid: int, get_key: bool = True) -> Tuple[str, Optional[bytes]]:
        if self.encoded:
            uid = hash_userid(userid)
            if get_key:
                key = hash_userid_to_key(userid)
            else:
                key = None
        else:
            uid = userid
            key = None
        return uid, key

    def get_stops(self, userid: int, pybuses: PyBuses) -> List[Stop]:
        """Buscar todas las paradas guardadas por un cliente.
        Las paradas se devuelven en una lista de objetos Stop, con el ID de parada, el nombre real de la parada,
        y si la parada guardada tiene un nombre personalizado, se guarda en el diccionario 'other'
        bajo la key 'custom_name'.
        :param userid: ID de usuario
        :param pybuses: instancia de PyBuses inicializada, necesaria para llamar a los StopGetters
        :type userid: int
        :type pybuses: PyBuses
        :return: Lista de objetos Stop (lista vacía si no hay paradas guardadas)
        :raise: excepciones de Sqlite3
        """
        stops = list()
        cursor = self.db.cursor()
        uid, key = self.__get_uid_key(userid)
        cursor.execute(_SELECT_ALL_STOPS, (uid,))
        results = cursor.fetchall()
        for stopid, custom_name in results:
            try:
                if self.encoded and custom_name is not None:
                    custom_name = decrypt(key, custom_name)
                stop = pybuses.find_stop(stopid)
                stop.other["custom_name"] = custom_name
                stops.append(stop)
            except StopException:
                pass
        cursor.close()
        return stops

    def is_stop_saved(self, userid: int, stopid: int) -> bool:
        """Comprobar si cierta parada está guardada por un usuario en la base de datos.
        :param userid: ID del usuario
        :param stopid: ID de la parada a comprobar
        :type userid: int
        :type stopid: int
        :return: True si está guardada, False si no lo está
        :rtype: bool
        :raise: excepciones de Sqlite3
        """
        cursor = self.db.cursor()
        uid, key = self.__get_uid_key(userid, False)
        cursor.execute(_IS_STOP_SAVED, (uid, stopid))
        result = cursor.fetchone()[0]
        cursor.close()
        return bool(result)

    def save_stop(self, userid: int, stopid: int, custom_name: Optional[str] = None) -> bool:
        """Guardar o actualizar una parada de un usuario en la base de datos.
        No lanza excepción en caso de error, sino que devuelve True/False con el resultado de la operación.
        :param userid: ID del usuario
        :param stopid: ID de la parada a guardar
        :param custom_name: Nombre personalizado de la parada (opcional, default=None=sin nombre personalizado)
        :type userid: int
        :type stopid: int
        :type custom_name: str
        :return: True si la parada se guardó, False si no se pudo guardar
        :rtype: bool
        """
        cursor = self.db.cursor()
        uid, key = self.__get_uid_key(userid)
        result = False
        if self.encoded and custom_name:
                custom_name = encrypt(key, custom_name)
        try:
            self.lock.acquire()
            cursor.execute(_SAVE_STOP, (uid, stopid, custom_name))
            self.db.commit()
            cursor.close()
            result = True
        except DatabaseError as ex:
            print(f"Error guardando/actualizando parada de usuario en BD:\n{ex}")
        finally:
            self.lock.release()
            return result

    def delete_stop(self, userid: int, stopid: int) -> bool:
        """Borrar una parada guardada por un usuario de la base de datos.
        No lanza excepción en caso de error, sino que devuelve True/False con el resultado de la operación.
        :param userid: ID del usuario
        :param stopid: ID de la parada a borrar
        :type userid: int
        :type stopid: int
        :return: True si la parada se borró correctamente, False si no se pudo borrar
        :rtype: bool
        """
        cursor = self.db.cursor()
        uid, key = self.__get_uid_key(userid)
        result = False
        try:
            self.lock.acquire()
            cursor.execute(_DELETE_STOP, (uid, stopid))
            self.db.commit()
            cursor.close()
            result = True
        except DatabaseError as ex:
            print(f"Error borrando parada de usuario en BD:\n{ex}")
        finally:
            self.lock.release()
            return result

    def get_custom_stop_name(self, userid: int, stopid: int) -> Optional[str]:
        """Obtener el nombre personalizado de una parada guardada de un usuario.
        Si la parada no está guardada, no tiene un nombre personalizado o se produjo un error, se devuelve None.
        :param userid: ID del usuario
        :param stopid: ID de la parada a buscar
        :type userid: int
        :type stopid: int
        :return: String con el nombre personalizado de parada, si existe |
                 None si la parada no está guardada o no tiene nombre personalizado o se produjo un error
        :rtype: str | None
        """
        try:
            cursor = self.db.cursor()
            uid, key = self.__get_uid_key(userid)
            cursor.execute(_SELECT_CUSTOM_STOPNAME, (uid, stopid))
            result = cursor.fetchone()
            custom_name = result[0] if isinstance(result, tuple) else None
            cursor.close()
            if custom_name and self.encoded:
                custom_name = decrypt(key, custom_name)
            return custom_name
        except DatabaseError as ex:
            print(f"Error buscando Custon Name de parada de usuario en BD:\n{ex}")
            return None
