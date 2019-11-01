"""TESTS - UTILS - MOCKED PERSISTENCE API - APP
Fake API, to be used on the tests that require it
"""

# # Native # #
import json
import contextlib
import urllib.parse
from typing import List, Optional

# # Installed # #
import flask
import httpx

# # Package # #
from .entities import *

# # Parent Package # #
from ..mocked_base_api import FakeAPIBase

__all__ = ("FakePersistenceAPI",)


class FakePersistenceAPI(FakeAPIBase):
    app_name = "Mocked_Persistence_API"
    stops: List[SavedStop]

    def __init__(self):
        super().__init__()

        self._app.route("/stops/<user_id>")(self._get_stops_callback)
        self._app.route("/stops", methods=("POST",))(self._post_stop_callback)
        self._app.route("/stops/<user_id>/<stop_id>", methods=("DELETE",))(self._delete_stop_callback)
        self._app.route("/clear")(self._clear_callback)

    def save_stop(self, **kwargs):
        if kwargs.get("user_id") is None:
            kwargs["user_id"] = 0
        stop = SavedStop(**kwargs)
        r = self._request("/stops", method="POST", data=dict(stop))
        r.raise_for_status()

    def delete_stop(self, user_id: int, stop_id: int):
        r = self._request(f"/stops/{user_id}/{stop_id}", method="DELETE")
        r.raise_for_status()

    def get_stop(self, user_id: int, stop_id: int) -> Optional[SavedStop]:
        stops = self.get_user_stops(user_id)
        try:
            return next(stop for stop in stops if stop.stop_id == stop_id)
        except StopIteration:
            return None

    def get_user_stops(self, user_id: int) -> List[SavedStop]:
        r = self._request(f"/stops/{user_id}")
        r.raise_for_status()
        data = json.loads(r.text)
        return [SavedStop(**chunk) for chunk in data]

    def clear(self):
        self._request("/clear")

    def _request(self, endpoint: str, method: str = "GET", data: Optional[dict] = None) -> httpx.Response:
        functions = {
            "GET": httpx.get,
            "POST": httpx.post,
            "DELETE": httpx.delete
        }
        return functions[method](urllib.parse.urljoin(f"http://localhost:{self.app_port}", endpoint), json=data)

    def _get_stops_callback(self, user_id):
        body = [dict(stop) for stop in self._get_user_stops(int(user_id))]
        return self.json_response(body)

    def _post_stop_callback(self):
        body: dict = flask.request.get_json()
        self._save_stop(**body)
        return self.ok_response()

    def _delete_stop_callback(self, user_id, stop_id):
        self._delete_stop(int(user_id), int(stop_id))
        return self.ok_response()

    def _clear_callback(self):
        self._clear()
        return self.ok_response()

    def _get_stop(self, user_id: int, stop_id: int):
        return next(
            stop for stop in self.stops
            if stop.user_id == user_id
            and stop.stop_id == stop_id
        )

    def _get_user_stops(self, user_id: int):
        return [
            stop for stop in self.stops
            if stop.user_id == user_id
        ]

    def _save_stop(self, **kwargs):
        self.stops.append(SavedStop(**kwargs))

    def _delete_stop(self, user_id: int, stop_id: int):
        with contextlib.suppress(StopIteration):
            self.stops.remove(self._get_stop(user_id, stop_id))

    def _clear(self):
        self.stops = []
