# SPDX-License-Identifier: Apache-2.0
from app.utility.base_world import BaseWorld

name = 'IEC104'
description = ('The IEC 104 plugin for Caldera provides adversary emulation abilities '
              'specific to the IEC 60870-5-104 telecontrol protocol.')
address = None
access = BaseWorld.Access.RED


async def enable(services):
    # Data-only plugin: Caldera auto-loads data/{abilities,sources,payloads} for
    # any enabled plugin. The payload binaries (iec104_cli) are provided by the
    # companion caldera-iec104-payloads repository; drop them into payloads/.
    pass
