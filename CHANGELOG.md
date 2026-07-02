# Changelog

## v1.0.0

Initial release of the IEC 104 plugin.

- Six abilities mapped to ATT&CK for ICS: station interrogation (C_IC), counter
  interrogation (C_CI), single command (C_SC), double command (C_DC), set-point
  command (C_SE), and clock synchronization (C_CS).
- `IEC 104 Sample Facts` fact source and a payload registry for the `iec104_cli`
  Linux/Windows/macOS binaries.
- Fieldmanual documentation in `docs/iec104.md`.

Planned: a Magma GUI panel and an output parser that turns interrogation results
into `iec104.point.*` facts.
