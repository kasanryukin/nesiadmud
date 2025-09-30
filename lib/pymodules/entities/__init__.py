"""
package: entities

Entity system for NakedMud - body types, sizes, and race management.
Provides Python-based configuration for races and body templates.

This module extends the world system with:
- Body type and size management
- Race configuration with custom body templates
- Storage and OLC interfaces for entity data
"""
import os
import importlib

__all__ = []

# compile a list of all our modules
for fl in os.listdir(__path__[0]):
    if fl.endswith(".py") and not (fl == "__init__.py" or fl.startswith(".")):
        __all__.append(fl[:-3])

# import all of our modules so they can register and initialize
__all__ = ['entity_config', 'entity_config_olc']
for module in __all__:
    importlib.import_module('.' + module, package=__name__)

# Initialize entity configuration on module load
from .entity_config import load_entity_configs
load_entity_configs()
