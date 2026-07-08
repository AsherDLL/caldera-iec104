# SPDX-License-Identifier: GPL-3.0-or-later
"""Unit tests for the iec104_cli action library.

Each test stands up a real c104 outstation (server) on localhost and drives it
with IEC104Client, asserting the outstation actually observed the master action.
The tests fail if the client logic is wrong or missing.
"""
import datetime
import time

import c104
import pytest

from iec104 import IEC104Client, IEC104Error
from iec104.client import parse_bool

CA = 1
PORT = 24044


@pytest.fixture(scope="module")
def server():
    srv = c104.Server(ip="127.0.0.1", port=PORT)
    station = srv.add_station(common_address=CA)
    sc = station.add_point(io_address=11, type=c104.Type.C_SC_NA_1)
    se = station.add_point(io_address=12, type=c104.Type.C_SE_NC_1)
    meas = station.add_point(io_address=100, type=c104.Type.M_ME_NC_1)
    meas.value = 42.0

    clock = {"synced": False}

    def on_clock_sync(server: c104.Server, ip: str,
                      date_time: datetime.datetime) -> c104.ResponseState:
        clock["synced"] = True
        return c104.ResponseState.SUCCESS

    srv.on_clock_sync(callable=on_clock_sync)
    srv.start()
    time.sleep(0.5)
    yield {"srv": srv, "sc": sc, "se": se, "meas": meas, "clock": clock}
    srv.stop()


@pytest.fixture
def client(server):
    c = IEC104Client(host="127.0.0.1", port=PORT, common_address=CA, timeout=8.0)
    for attempt in range(4):  # c104 connect can be briefly flaky on Windows CI
        try:
            c.connect()
            break
        except IEC104Error:
            if attempt == 3:
                raise
            time.sleep(0.5)
    yield c
    c.close()
    time.sleep(0.3)


def test_hostname_is_resolved():
    # c104 requires a numeric IP; a hostname must be resolved at construction.
    c = IEC104Client(host="localhost", port=PORT, common_address=CA)
    assert c.host == "127.0.0.1"


def test_unresolvable_host_raises():
    with pytest.raises(IEC104Error):
        IEC104Client(host="no.such.host.invalid.", port=PORT, common_address=CA)


def test_parse_bool():
    assert parse_bool("ON") is True
    assert parse_bool("Off") is False
    assert parse_bool("1") is True and parse_bool("0") is False
    with pytest.raises(ValueError):
        parse_bool("maybe")


def test_single_command_drives_outstation(server, client):
    assert client.single_command(11, True) is True
    time.sleep(0.4)
    assert bool(server["sc"].value) is True
    assert client.single_command(11, False) is True
    time.sleep(0.4)
    assert bool(server["sc"].value) is False


def test_setpoint_drives_outstation(server, client):
    assert client.setpoint(12, 3.5, kind="nc") is True
    time.sleep(0.4)
    assert abs(float(server["se"].value) - 3.5) < 0.01


def test_interrogation_confirms(server, client):
    assert client.interrogate("station") is True


def test_interrogation_discovers_points(server, client):
    client.interrogate("station")
    time.sleep(0.5)
    points = client.points()
    assert 100 in points, f"expected measurement IOA 100 to be reported, saw {sorted(points)}"


def test_clock_sync_reaches_outstation(server, client):
    assert client.clock_sync() is True
    time.sleep(0.3)
    assert server["clock"]["synced"] is True
