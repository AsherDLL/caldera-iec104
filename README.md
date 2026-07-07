# IEC 104 Plugin for Caldera

The IEC 104 plugin provides [Caldera](https://github.com/mitre/caldera) with
adversary-emulation abilities for the **IEC 60870-5-104** telecontrol protocol
(TCP/2404), used widely in electric power and other utility SCADA systems.

Abilities are mapped to [ATT&CK for ICS](https://attack.mitre.org/matrices/ics/) and
driven by a generic command-line master (`iec104_cli`), so they work against any
conforming IEC-104 outstation, the target address, common address, and information
object addresses are supplied as facts.

This is a single self-contained repository: the plugin and its payload source live
together. Because the payload wraps the GPL-3.0 `c104` library, the repository is
licensed **GPL-3.0**.

## Abilities

| Ability | IEC-104 | Tactic | Technique |
|---|---|---|---|
| IEC 104 - Station Interrogation | C_IC_NA_1 | Collection | T0861 Point & Tag Identification |
| IEC 104 - Counter Interrogation | C_CI_NA_1 | Collection | T0861 Point & Tag Identification |
| IEC 104 - Single Command | C_SC_NA_1 | Impair Process Control | T0855 Unauthorized Command Message |
| IEC 104 - Double Command | C_DC_NA_1 | Impair Process Control | T0855 Unauthorized Command Message |
| IEC 104 - Set Point Command | C_SE_NC_1 | Impair Process Control | T0836 Modify Parameter |
| IEC 104 - Clock Synchronization | C_CS_NA_1 | Impair Process Control | T0855 Unauthorized Command Message |

See [`docs/iec104.md`](docs/iec104.md) for per-ability commands and the fact
reference.

## Installation

1. Clone into Caldera's `plugins/` directory as `iec104`:

   ```
   git clone https://github.com/AsherDLL/caldera-iec104 plugins/iec104
   ```

   The payload binaries ship in `payloads/` (`iec104_cli`, and `iec104_cli.exe` /
   `iec104_cli_darwin` from the release CI).

2. Enable the plugin in `conf/local.yml`:

   ```yaml
   plugins:
     - iec104
   ```

3. Restart Caldera. The abilities appear under the tactics above, and an
   **IEC 104 Sample Facts** source is available to seed a fact source.

## Usage

Create a fact source (or edit **IEC 104 Sample Facts**) with your target:

| Fact | Example | Meaning |
|---|---|---|
| `iec104.server.ip` | `10.0.0.5` | outstation IP |
| `iec104.server.port` | `2404` | IEC-104 TCP port |
| `iec104.common_address` | `1` | ASDU common address |
| `iec104.command.ioa` | `100` | IOA for single/double commands |
| `iec104.command.value` | `"ON"` | `ON`/`OFF` (quote it, YAML boolean) |
| `iec104.setpoint.ioa` | `100` | IOA for set-point commands |
| `iec104.setpoint.value` | `12.5` | set-point value |

Then build an adversary from the abilities above and run an operation against an
agent that can reach the outstation.

## Payload

The `iec104_cli` payload source and build tooling are in [`src/`](src/README.md); the
Linux binary is committed in `payloads/`, and Windows/macOS binaries are produced by
the release CI (`.github/workflows/ci.yaml`). Build locally:

```
cd src && make build/linux && make update      # -> payloads/iec104_cli
```

## Tests

```
pip install -r src/requirements.txt pytest
PYTHONPATH=src python -m pytest tests -q
```

## License

GPL-3.0-or-later. See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
