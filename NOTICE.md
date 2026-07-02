# NOTICE

caldera-iec104 — an IEC 60870-5-104 plugin for MITRE Caldera.

Copyright (c) 2026 Asher Davila.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
these files except in compliance with the License. You may obtain a copy of the
License in the `LICENSE` file or at http://www.apache.org/licenses/LICENSE-2.0.

## Payloads

The compiled payload binaries used by this plugin's abilities (`iec104_cli`) are
**not** part of this repository. They are built and distributed separately in the
GPL-3.0-licensed companion repository
[`caldera-iec104-payloads`](https://github.com/AsherDavila/caldera-iec104-payloads),
because they bundle the GPL-3.0 `c104` library. This split keeps the plugin itself
Apache-2.0, mirroring the MITRE `iec61850` / `iec61850-payloads` model.
