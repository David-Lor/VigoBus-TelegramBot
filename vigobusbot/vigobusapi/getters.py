
"""VIGOBUSAPI.GETTERS
Conjunto de métodos que acceden a la API pertinente de VigoBus para obtener los datos de paradas y buses online.
"""

# Librerías nativas
import json
import requests
from typing import List
from requests.exceptions import *

# Librerías instaladas
from pybuses import Bus, Stop
from pybuses.exceptions import *

# Proyecto
from vigobusbot.settings import config


API_URL = config.API.URL
TIMEOUT = config.API.Timeout


def get_buses(stopid: int) -> List[Bus]:
    """Obtener listado de buses de la API
    :param stopid: ID de parada de la cual obtener los buses
    :type stopid: int
    :return: Lista de objetos Bus
    :rtype: List[Bus]
    :raises: BusGetterUnavailable si hay errores al consultar con la API, obtener datos o ésta reportó un error
    """
    try:
        r = requests.get(f"{API_URL}/buses/{stopid}", timeout=TIMEOUT)
    except RequestException as ex:
        raise BusGetterUnavailable(ex)
    if r.status_code != 200:
        raise BusGetterUnavailable(f"Status Code={r.status_code}")

    try:
        j: dict = json.loads(r.text)
        if j["error"] == 1:
            raise BusGetterUnavailable("Error en API")

        jbuses = j["buses"]
        buses = list()
        for jbus in jbuses:
            buses.append(Bus(
                line=jbus["line"],
                route=jbus["route"],
                time=jbus["time"],
                distance=jbus.get("dist")
            ))
        return buses

    except KeyError:
        raise BusGetterUnavailable("KeyError")

    except json.decoder.JSONDecodeError as ex:
        raise BusGetterUnavailable(f"Error decoding JSON:\n{ex}")


def get_stop(stopid: int) -> Stop:
    """Buscar una parada en la API y obtener su información
    :param stopid: ID de parada a buscar
    :type stopid: int
    :return: Objeto Stop con toda la información (nombre y ubicación)
    :rtype: Stop
    :raises: StopGetterUnavailable si hay errores al consultar con la API, obtener datos o ésta reportó un error |
             StopNotExist si la parada a consultar no existe
    """
    try:
        r = requests.get(f"{API_URL}/stop/{stopid}", timeout=TIMEOUT, params={"timeout": TIMEOUT-1})
    except RequestException as ex:
        raise StopGetterUnavailable(ex)
    if r.status_code != 200:
        raise StopGetterUnavailable(f"Status Code={r.status_code}")

    try:
        j: dict = json.loads(r.text)
        if j["error"] == 1:
            raise StopGetterUnavailable("Error en API")
        if j["exists"] == 0:
            raise StopNotExist(f"La parada {stopid} no existe, según la API")
        return Stop(
            stopid=stopid,
            name=j["name"],
            lat=j.get("lat"),
            lon=j.get("lon")
        )

    except KeyError:
        raise StopGetterUnavailable("KeyError")

    except json.decoder.JSONDecodeError as ex:
        raise BusGetterUnavailable(f"Error decoding JSON:\n{ex}")
