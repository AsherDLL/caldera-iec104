# SPDX-License-Identifier: GPL-3.0-or-later
"""IEC 60870-5-104 master-station client actions, backed by the c104 library.

Every method maps to one IEC-104 master action and returns a bool that reflects
whether the outstation confirmed the request (ACT-CON positive). The class is
transport-only: it takes numeric addresses/values and has no knowledge of any
particular device, so it works against any conforming IEC-104 outstation.
"""
import socket
import time

import c104

# Set-point command variants: normalized / scaled / short-float.
_SETPOINT_TYPES = {
    "na": c104.Type.C_SE_NA_1,  # normalized value  [-1 .. +1)
    "nb": c104.Type.C_SE_NB_1,  # scaled value      [-32768 .. 32767]
    "nc": c104.Type.C_SE_NC_1,  # short floating point (IEEE-754)
}

# Interrogation qualifier (QOI): station (global) or group 1..16.
_QOI = {"station": c104.Qoi.STATION}
for _i in range(1, 17):
    _QOI[f"group{_i}"] = getattr(c104.Qoi, f"GROUP_{_i}", c104.Qoi.STATION)


class IEC104Error(Exception):
    """Raised when the connection cannot be established or an action is rejected."""


def parse_bool(value):
    """Accept ON/OFF, TRUE/FALSE, 1/0 (case-insensitive) as a boolean."""
    s = str(value).strip().lower()
    if s in ("on", "true", "1", "close", "closed"):
        return True
    if s in ("off", "false", "0", "open", "opened"):
        return False
    raise ValueError(f"expected ON/OFF (got {value!r})")


class IEC104Client:
    def __init__(self, host, port=2404, common_address=1, originator_address=0,
                 timeout=10.0, tick_rate_ms=100):
        # c104 requires a numeric IP; resolve hostnames so a fact/argument may be
        # either an IP or a DNS name.
        try:
            self.host = socket.gethostbyname(host)
        except socket.gaierror as exc:
            raise IEC104Error(f"cannot resolve host {host!r}: {exc}") from exc
        self.port = int(port)
        self.common_address = int(common_address)
        self.timeout = float(timeout)
        self._connected = False
        self._points_seen = {}  # io_address -> c104.Point (discovered via monitoring)

        self._client = c104.Client(tick_rate_ms=int(tick_rate_ms))
        # Originator address is optional and lives on the client in c104; apply
        # defensively so we stay compatible across c104 versions.
        if originator_address and hasattr(self._client, "originator_address"):
            self._client.originator_address = int(originator_address)

        self._conn = self._client.add_connection(
            ip=self.host, port=self.port, init=c104.Init.NONE
        )
        self._conn.on_state_change(callable=self._on_state)
        self._station = self._conn.add_station(common_address=self.common_address)
        self._client.on_new_point(callable=self._on_new_point)

    # -- connection lifecycle -------------------------------------------------
    def connect(self):
        self._client.start()
        deadline = time.time() + self.timeout
        while not self._connected and time.time() < deadline:
            time.sleep(0.05)
        if not self._connected:
            raise IEC104Error(f"could not connect to {self.host}:{self.port}")
        return True

    def close(self):
        try:
            self._client.stop()
        except Exception:
            pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_exc):
        self.close()

    # -- callbacks ------------------------------------------------------------
    # c104 validates callback signatures against these exact type annotations.
    def _on_state(self, connection: c104.Connection,
                  state: c104.ConnectionState) -> None:
        self._connected = state == c104.ConnectionState.OPEN

    def _on_new_point(self, client: c104.Client, station: c104.Station,
                      io_address: int, point_type: c104.Type) -> None:
        # Fired for a message from an IOA we have not registered yet: add it so
        # its value is tracked, then subscribe to further updates.
        point = station.get_point(io_address)
        if point is None:
            point = station.add_point(io_address=io_address, type=point_type)
        if point is not None:
            self._points_seen[io_address] = point
            try:
                point.on_receive(callable=self._on_receive)
            except Exception:
                pass

    def _on_receive(self, point: c104.Point, previous_info: c104.Information,
                    message: c104.IncomingMessage) -> c104.ResponseState:
        self._points_seen[point.io_address] = point
        return c104.ResponseState.SUCCESS

    # -- monitor direction ----------------------------------------------------
    def interrogate(self, qualifier="station"):
        """C_IC_NA_1 general (station/group) interrogation.

        The first interrogation registers any points the outstation reports (via
        the on_new_point callback); a second pass then populates their values on
        the now-registered points, so a caller can read them back.
        """
        qoi = _QOI.get(str(qualifier).lower(), c104.Qoi.STATION)
        ok = self._conn.interrogation(
            self.common_address, cause=c104.Cot.ACTIVATION, qualifier=qoi,
            wait_for_response=True)
        if ok and self._points_seen:
            self._conn.interrogation(
                self.common_address, cause=c104.Cot.ACTIVATION, qualifier=qoi,
                wait_for_response=True)
        return bool(ok)

    def counter_interrogate(self):
        """C_CI_NA_1 general counter interrogation (integrated totals)."""
        return bool(self._conn.counter_interrogation(
            self.common_address, cause=c104.Cot.ACTIVATION,
            qualifier=c104.Rqt.GENERAL, freeze=c104.Frz.READ,
            wait_for_response=True))

    def points(self):
        """Return {io_address: value} for every point seen so far."""
        merged = {}
        for point in list(self._station.points):
            merged[point.io_address] = point
        merged.update(self._points_seen)
        return {ioa: pt.value for ioa, pt in sorted(merged.items())}

    # -- control direction ----------------------------------------------------
    def _control_point(self, io_address, point_type, select):
        mode = (c104.CommandMode.SELECT_AND_EXECUTE if select
                else c104.CommandMode.DIRECT)
        point = self._station.get_point(io_address)
        if point is None:
            point = self._station.add_point(
                io_address=io_address, type=point_type, command_mode=mode)
        return point

    def single_command(self, io_address, on, select=False):
        """C_SC_NA_1 single command (ON/OFF)."""
        point = self._control_point(io_address, c104.Type.C_SC_NA_1, select)
        point.value = bool(on)
        return bool(point.transmit(c104.Cot.ACTIVATION))

    def double_command(self, io_address, on, select=False):
        """C_DC_NA_1 double command (ON/OFF)."""
        point = self._control_point(io_address, c104.Type.C_DC_NA_1, select)
        point.value = c104.Double.ON if on else c104.Double.OFF
        return bool(point.transmit(c104.Cot.ACTIVATION))

    def setpoint(self, io_address, value, kind="nc", select=False):
        """C_SE_Nx_1 set-point command (kind = na|nb|nc)."""
        point_type = _SETPOINT_TYPES[kind]
        point = self._control_point(io_address, point_type, select)
        point.value = int(value) if kind == "nb" else float(value)
        return bool(point.transmit(c104.Cot.ACTIVATION))

    def clock_sync(self):
        """C_CS_NA_1 clock synchronization (sets the outstation's time to now)."""
        return bool(self._conn.clock_sync(
            self.common_address, wait_for_response=True))
