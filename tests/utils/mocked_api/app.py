"""TESTS - UTILS - MOCKED API - APP
Fake API, to be used on the tests that require it
"""

# # Native # #
import time
import json
import threading
from typing import Optional

# # Installed # #
import flask
import requests
from pybusent.sorting import BusSort

# # Package # #
from .entities import *

# # Parent Package # #
from ..settings import settings


class FakeAPI:
    stop: Optional[StopOrException]
    buses: Optional[BusesOrException]
    stop_id_should_exist: Optional[int]
    """Set if 'buses' should return content while 'stop' is set to Exception"""
    # stop_endpoint_called: int
    # buses_endpoint_called: int
    _app: flask.Flask
    _app_thread: Optional[threading.Thread]

    def __init__(self):
        self._app = flask.Flask("Mocked_API")
        self._app_thread = None
        self.clear()

        self._app.route('/stop/<stop_id>')(self._get_stop_callback)
        self._app.route('/buses/<stop_id>')(self._get_buses_callback)
        self._app.route('/status')(lambda: self.json_response({"status": "OK"}))

    def _get_stop_callback(self, stop_id: int):
        if isinstance(self.stop, Stop) and self.stop.stopid == int(stop_id):
            return self.json_response(self.stop.get_dict())

        elif isinstance(self.stop, Exception):
            raise self.stop

        else:
            return self.not_found_response("Stop not exist")

    def _get_buses_callback(self, stop_id: int, get_all_buses=False):
        stop_id = int(stop_id)

        if isinstance(self.buses, list) \
                and (isinstance(self.stop, Stop) and self.stop.stopid == stop_id) \
                or self.stop_id_should_exist == stop_id:
            buses = [*self.buses]
            more_buses_available = False

            if not get_all_buses and len(self.buses) > settings.buses_limit:
                buses = buses[:settings.buses_limit]
                more_buses_available = True

            buses.sort(key=BusSort.time_line_route)  # Sorting is not tested (buses shall be sorted by the API)
            buses_response = BusesAPIResponse(buses=buses, more_buses_available=more_buses_available)
            return self.json_response(buses_response.dict())

        elif isinstance(self.buses, Exception):
            raise self.buses

        else:
            return self.not_found_response("Stop not exist")

    def not_found_response(self, reason="Unknown reason"):
        return self.json_response({"reason": reason}, status_code=404)

    @staticmethod
    def json_response(body: dict, status_code=200) -> flask.Response:
        return flask.Response(
            response=json.dumps(body),
            status=status_code,
            mimetype="application/json",
            content_type="application/json; charset=utf-8"
        )

    @staticmethod
    def wait_for_api(timeout=settings.api_join_timeout):
        start = time.time()
        exc = None

        while time.time() - start < timeout:
            try:
                result: requests.Response = requests.get(
                    f"http://127.0.0.1:{settings.fake_api_port}/status",
                    timeout=settings.api_join_timeout
                )
                result.raise_for_status()
                return result

            except (requests.HTTPError, requests.ConnectionError) as ex:
                exc = ex
                time.sleep(0.25)

        raise exc

    def start_server(self, wait=True):
        if self._app_thread is None or not self._app_thread.is_alive():
            self._app_thread = threading.Thread(
                target=self._app.run,
                kwargs={
                    "host": "0.0.0.0",
                    "port": settings.fake_api_port
                },
                daemon=True
            )
            self._app_thread.start()

            if wait:
                self.wait_for_api()

    def clear(self):
        self.stop = None
        self.buses = None
        self.stop_id_should_exist = None
        # self.stop_endpoint_called = 0
        # self.buses_endpoint_called = 0
