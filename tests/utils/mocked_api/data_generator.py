"""DATA GENERATOR
Generate random Stop & Buses data using Faker.
"""

# # Native # #
import random
from typing import Tuple

# # Installed # #
from faker import Faker

# # Parent Package # #
from ..settings import settings

# # Project # #
from vigobusbot.entities import *

__all__ = ("given_stop_id", "given_stop", "given_bus", "given_buses", "given_stop_and_buses")

faker = Faker()


def given_stop_id(minimum=100, maximum=100000) -> int:
    return random.randint(minimum, maximum)


def given_stop(**kwargs) -> Stop:
    location = faker.location_on_land(coords_only=True)
    return Stop(
        stopid=kwargs.get("stop_id", given_stop_id()),
        name=kwargs.get("stop_name", faker.street_address()),
        lat=kwargs.get("stop_lat", location[0]),
        lon=kwargs.get("stop_lon", location[1])
    )


def given_bus(**kwargs) -> Bus:
    line_number = random.randint(4, 25)
    line_letter = random.choice(("", "A", "B", "C", "D"))
    return Bus(
        line=kwargs.get("line", f"{line_number}{line_letter}"),
        route=kwargs.get("route", faker.street_name() + "-" + faker.street_name()),
        time=kwargs.get("time", random.randint(0, 31))
    )


def given_buses(**kwargs) -> Buses:
    limit = kwargs.get("limit", settings.buses_limit)
    return [given_bus() for _ in range(limit)]


def given_stop_and_buses(**kwargs) -> Tuple[Stop, Buses]:
    return given_stop(**kwargs), given_buses(**kwargs)
