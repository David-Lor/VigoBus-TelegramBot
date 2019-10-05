"""TESTS - UTILS - MOCKED BUS API - APP
Fake API, to be used on the tests that require it
"""

# # Native # #
from typing import Optional
import pickle
import base64

# # Installed # #
import flask
import requests
from pybusent.sorting import BusSort

# # Package # #
from .entities import *

# # Parent Package # #
from ..mocked_base_api import FakeAPIBase
from ..settings import settings

__all__ = ("FakeBusAPI", "BusData")


class BusData:
    stop: Optional[StopOrException]
    buses: Optional[BusesOrException]
    stop_id_should_exist: Optional[int]
    """Set if 'buses' should return content while 'stop' is set to Exception"""

    def __init__(self, **kwargs):
        self.stop = kwargs.get("stop")
        self.buses = kwargs.get("buses")
        self.stop_id_should_exist = kwargs.get("stop_id_should_exist")

    @staticmethod
    def parse_data(data: dict):
        """Parse received data from a HTTP POST request on the server"""
        parsed_dict = dict()

        for k, v in data.items():
            if isinstance(v, str):
                parsed_dict[k] = pickle.loads(base64.b64decode(v.encode()))

        return BusData(**parsed_dict)

    def encode_data(self) -> dict:
        """Prepare BusData to be sent on a HTTP POST request"""
        encoded_dict = dict()

        for k, v in vars(self).items():
            if v is not None:
                encoded_dict[k] = base64.b64encode(pickle.dumps(v)).decode()

        return encoded_dict


class FakeBusAPI(FakeAPIBase, BusData):
    app_name = "Mocked_Bus_API"

    def __init__(self):
        super().__init__()

        self._app.route("/stop/<stop_id>")(self._get_stop_callback)
        self._app.route("/buses/<stop_id>")(self._get_buses_callback)
        self._app.route("/data", methods=("POST",))(self._post_set_data)

    def set_data(self, data: BusData):
        self._clear()
        requests.post(f"http://localhost:{self.app_port}/data", json=data.encode_data())
        return self.ok_response()

    def _post_set_data(self):
        body: dict = flask.request.get_json()
        data: BusData = self.parse_data(body)

        if data.stop is not None:
            self.stop = data.stop
        if data.buses is not None:
            self.buses = data.buses
        if data.stop_id_should_exist is not None:
            self.stop_id_should_exist = data.stop_id_should_exist

    def _get_stop_callback(self, stop_id):
        if isinstance(self.stop, Stop) and self.stop.stopid == int(stop_id):
            return self.json_response(self.stop.get_dict())

        elif isinstance(self.stop, Exception):
            raise self.stop

        else:
            return self.not_found_response("Stop not exist")

    def _get_buses_callback(self, stop_id, get_all_buses=False):
        stop_id = int(stop_id)

        if isinstance(self.buses, list) \
                and (isinstance(self.stop, Stop) and self.stop.stopid == stop_id) \
                or self.stop_id_should_exist == stop_id:
            buses = [*self.buses]
            more_buses_available = False

            if not int(get_all_buses) and len(self.buses) > settings.buses_limit:
                buses = buses[:settings.buses_limit]
                more_buses_available = True

            buses.sort(key=BusSort.time_line_route)  # Sorting is not tested (buses shall be sorted by the API)
            buses_response = BusesAPIResponse(buses=buses, more_buses_available=more_buses_available)
            return self.json_response(buses_response.dict())

        elif isinstance(self.buses, Exception):
            raise self.buses

        else:
            return self.not_found_response("Stop not exist")

    def _clear(self):
        self.stop = None
        self.buses = None
        self.stop_id_should_exist = None
