"""TESTS - UTILS - MOCKED BASE API - APP
Base Fake API to build other mocked fake APIs
"""

# # Native # #
import abc
import time
import json
import multiprocessing
import contextlib
from typing import Optional, Union

# # Installed # #
import flask
import httpx
from gevent.pywsgi import WSGIServer

# # Parent Package # #
from ..settings import settings
from ..helpers import get_free_port

__all__ = ("FakeAPIBase",)


class FakeAPIBase:
    app_name: str
    app_port: int
    _app: flask.Flask
    _app_process: Optional[multiprocessing.Process]
    _http_server: WSGIServer

    def __init__(self):
        """The init method on child classes must be called AFTER setting app_name, app_port
        """
        self._app = flask.Flask(self.app_name)
        self._app_process = None
        self._clear()
        self._app.route("/status")(self.ok_response)
        self._app.route("/stop")(self._stop_server_callback)
        self._app.route("/clear")(self._clear)
        self.app_port = get_free_port()
        self._http_server = WSGIServer(("0.0.0.0", self.app_port), self._app)

    # noinspection PyMethodMayBeStatic
    def _stop_server_callback(self):
        print(f"Stopping Fake API {self.app_name} on port {self.app_port}...")
        flask.request.environ.get("werkzeug.server.shutdown")()
        return self.ok_response()

    def ok_response(self):
        return self.json_response({"status": "OK"})

    @staticmethod
    def json_response(body: Union[dict, list], status_code=200) -> flask.Response:
        return flask.Response(
            response=json.dumps(body),
            status=status_code,
            mimetype="application/json",
            content_type="application/json; charset=utf-8"
        )

    def not_found_response(self, reason="Unknown reason"):
        return self.json_response({"reason": reason}, status_code=404)

    def wait_for_api(self, timeout=settings.api_join_timeout):
        start = time.time()

        while time.time() - start < timeout:
            try:
                result: httpx.Response = httpx.get(
                    f"http://127.0.0.1:{self.app_port}/status",
                    timeout=settings.api_join_timeout
                )
                result.raise_for_status()
                return result

            except (httpx.HTTPError, ConnectionError):
                time.sleep(0.25)

        raise TimeoutError(f"Timeout while waiting for the Fake {self.app_name} API to be initialized")

    @abc.abstractmethod
    def _clear(self):
        """clear method must reset persisted data between tests and sessions. Can be used to initialize the variables.
        """
        pass

    def start_server(self, wait=True):
        if self._app_process is None or not self._app_process.is_alive():
            self._app_process = multiprocessing.Process(
                target=self._app.run,
                kwargs={
                    "host": "0.0.0.0",
                    "port": self.app_port
                },
                daemon=True
            )
            self._app_process.start()
            print(f"Started Fake API {self.app_name} on port {self.app_port}")

            if wait:
                self.wait_for_api()

    def stop_server(self, timeout=settings.api_join_timeout, join=False):
        if self._app_process and self._app_process.is_alive():
            with contextlib.suppress(httpx.HTTPError):
                httpx.get(f"http://localhost:{self.app_port}/stop", timeout=timeout)
            if join:
                self._app_process.join(timeout=timeout)
