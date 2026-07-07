# SPDX-License-Identifier: GPL-3.0-or-later
"""A small IEC 60870-5-104 client action library built on top of c104.

Exposes IEC104Client, a thin wrapper that turns the c104 master/client API into
the discrete master-station actions an operator drives from the command line:
station/counter interrogation, single/double commands, set-point commands, and
clock synchronization.
"""
from .client import IEC104Client, IEC104Error
from .version import __version__

__all__ = ["IEC104Client", "IEC104Error", "__version__"]
