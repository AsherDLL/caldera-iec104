# Changelog

## v1.0.0

Initial release of the IEC 104 plugin.

- Six abilities mapped to ATT&CK for ICS: station interrogation (C_IC), counter
  interrogation (C_CI), single command (C_SC), double command (C_DC), set-point
  command (C_SE), and clock synchronization (C_CS).
- `IEC 104 Sample Facts` fact source and a payload registry for the `iec104_cli`
  Linux/Windows/macOS binaries.
- A GUI panel (splash service + Magma Vue view) listing the plugin's abilities.
- An output parser that turns interrogation results into `iec104.point.*` facts,
  wired into the interrogation abilities.
- The `iec104_cli` payload (source in `src/`, Linux binary in `payloads/`, wrapping
  the GPL-3.0 `c104` library) with PyInstaller build, cross-platform CI, and unit
  tests. Because the payload bundles `c104`, the whole repository is GPL-3.0.
- Fieldmanual documentation in `docs/iec104.md`.
