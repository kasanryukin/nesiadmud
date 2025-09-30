"""
package: mssp

MSSP (Mud Server Status Protocol) implementation for NakedMud.
Provides automatic response to MSSP requests via IAC telnet negotiation.

MSSP allows MUD listing sites and clients to query server information
such as player count, uptime, codebase, and other metadata.
"""
import os
import importlib

__all__ = [ ]

# compile a list of all our modules
for fl in os.listdir(__path__[0]):
    if fl.endswith(".py") and not (fl == "__init__.py" or fl.startswith(".")):
        __all__.append(fl[:-3])

# import all of our modules so they can register relevant mud settings and data
__all__ = ['mssp', 'msspedit']
for module in __all__:
    importlib.import_module('.' + module, package=__name__)
