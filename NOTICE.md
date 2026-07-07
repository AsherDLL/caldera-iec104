# NOTICE

caldera-iec104, an IEC 60870-5-104 plugin for MITRE Caldera, with its `iec104_cli`
payload.

Copyright (c) 2026 Asher Davila.

This program is free software: you can redistribute it and/or modify it under the
terms of the **GNU General Public License v3.0 or later** (see `LICENSE`).

## Third-party components

The `iec104_cli` payload links against and bundles:

- **c104**, a Python IEC 60870-5-104 implementation, licensed under the **GNU
  General Public License v3.0**.
  https://github.com/Fraunhofer-FIT-DIEN/iec104-python

Because the payload binaries bundle the GPL-3.0 `c104` library, this repository
(plugin **and** payload together) is licensed **GPL-3.0** as a whole. MITRE's own
`iec61850` plugin instead keeps the plugin Apache-2.0 and isolates the GPL payload in
a separate `iec61850-payloads` repo; this project keeps everything in one repository
under GPL-3.0.

- **PyInstaller** is used only as a build tool; its bootloader exception permits
  distributing the resulting binaries under this project's license.
