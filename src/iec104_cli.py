# SPDX-License-Identifier: GPL-3.0-or-later
"""iec104_cli - a command-line IEC 60870-5-104 master for adversary emulation.

A single, generic client that speaks IEC-104 to any conforming outstation. It is
transport-only (numeric common addresses / IOAs / values); the semantics of each
point belong to the target device. Intended to be driven from Caldera abilities,
one subcommand per master action.

    iec104_cli <host> [--port 2404] [--ca 1] <action> [args]
"""
import argparse
import sys

from iec104 import IEC104Client, IEC104Error, __version__
from iec104.client import parse_bool


def _build_parser():
    p = argparse.ArgumentParser(
        prog="iec104_cli",
        description="IEC 60870-5-104 master action library v%s" % __version__,
    )
    p.add_argument("host", help="target outstation IP address or hostname")
    p.add_argument("-p", "--port", type=int, default=2404,
                   help="IEC-104 TCP port (default 2404)")
    p.add_argument("--ca", "--common-address", dest="ca", type=int, default=1,
                   help="ASDU common address of the target station (default 1)")
    p.add_argument("--originator-address", type=int, default=0,
                   help="originator address to stamp on requests (default 0)")
    p.add_argument("--timeout", type=float, default=10.0,
                   help="connect/response timeout in seconds (default 10)")
    p.add_argument("--version", action="version", version=__version__)

    sub = p.add_subparsers(dest="action", required=True, metavar="action")

    s = sub.add_parser("interrogate", help="C_IC_NA_1 station/group interrogation")
    s.add_argument("--qualifier", default="station",
                   help="station or group1..group16 (default station)")

    sub.add_parser("counter-interrogate",
                   help="C_CI_NA_1 general counter interrogation")

    sub.add_parser("scan",
                   help="interrogate, then list every point the station reports")

    s = sub.add_parser("single-command", help="C_SC_NA_1 single command")
    s.add_argument("ioa", type=int, help="information object address")
    s.add_argument("value", help="ON or OFF")
    s.add_argument("--select", action="store_true",
                   help="use select-before-operate instead of direct execute")

    s = sub.add_parser("double-command", help="C_DC_NA_1 double command")
    s.add_argument("ioa", type=int, help="information object address")
    s.add_argument("value", help="ON or OFF")
    s.add_argument("--select", action="store_true",
                   help="use select-before-operate instead of direct execute")

    s = sub.add_parser("setpoint", help="C_SE_Nx_1 set-point command")
    s.add_argument("ioa", type=int, help="information object address")
    s.add_argument("value", type=float, help="set-point value")
    s.add_argument("--type", dest="kind", choices=("na", "nb", "nc"), default="nc",
                   help="na=normalized, nb=scaled, nc=short float (default nc)")
    s.add_argument("--select", action="store_true",
                   help="use select-before-operate instead of direct execute")

    sub.add_parser("clock-sync", help="C_CS_NA_1 clock synchronization")
    return p


def _print_points(client):
    points = client.points()
    if not points:
        print("no points reported by the station")
        return
    print("[*] %d point(s) reported:" % len(points))
    for ioa, value in points.items():
        print("point %d = %s" % (ioa, value))


def _run(args):
    client = IEC104Client(
        host=args.host, port=args.port, common_address=args.ca,
        originator_address=args.originator_address, timeout=args.timeout,
    )
    client.connect()
    try:
        if args.action == "interrogate":
            print("[*] Station interrogation (C_IC_NA_1)")
            ok = client.interrogate(args.qualifier)
            _print_points(client)
            return ok
        if args.action == "counter-interrogate":
            print("[*] Counter interrogation (C_CI_NA_1)")
            ok = client.counter_interrogate()
            _print_points(client)
            return ok
        if args.action == "scan":
            print("[*] Scan: interrogation + point listing")
            ok = client.interrogate("station")
            _print_points(client)
            return ok
        if args.action == "single-command":
            on = parse_bool(args.value)
            print("[*] Single command (C_SC_NA_1) IOA %d = %s%s"
                  % (args.ioa, "ON" if on else "OFF",
                     " [select-before-operate]" if args.select else ""))
            return client.single_command(args.ioa, on, select=args.select)
        if args.action == "double-command":
            on = parse_bool(args.value)
            print("[*] Double command (C_DC_NA_1) IOA %d = %s%s"
                  % (args.ioa, "ON" if on else "OFF",
                     " [select-before-operate]" if args.select else ""))
            return client.double_command(args.ioa, on, select=args.select)
        if args.action == "setpoint":
            print("[*] Set-point command (C_SE_N%s_1) IOA %d = %s"
                  % (args.kind[-1].upper(), args.ioa, args.value))
            return client.setpoint(args.ioa, args.value, kind=args.kind,
                                   select=args.select)
        if args.action == "clock-sync":
            print("[*] Clock synchronization (C_CS_NA_1)")
            return client.clock_sync()
        return False
    finally:
        client.close()


def main(argv=None):
    args = _build_parser().parse_args(argv)
    try:
        ok = _run(args)
    except IEC104Error as exc:
        print("[!] %s" % exc, file=sys.stderr)
        return 2
    except ValueError as exc:
        print("[!] %s" % exc, file=sys.stderr)
        return 2
    if ok:
        print("[+] %s: outstation confirmed" % args.action)
        return 0
    print("[!] %s: no positive confirmation from the outstation" % args.action,
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
