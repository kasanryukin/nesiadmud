"""
package: vitality

Vitality system for NakedMud - health, spell points, and energy management.
Provides Python-based vitality tracking with damage, healing, regeneration, and death mechanics.

This module extends the character system with:
- Health/Spell/Energy point tracking
- Damage and healing functions with hooks
- Automatic regeneration system
- Death mechanics and status messages
"""
import os
import importlib

__all__ = []

# compile a list of all our modules
for fl in os.listdir(__path__[0]):
    if fl.endswith(".py") and not (fl == "__init__.py" or fl.startswith(".")):
        __all__.append(fl[:-3])

# import all of our modules so they can register and initialize
__all__ = ['vitality_config', 'vitality_system']
for module in __all__:
    importlib.import_module('.' + module, package=__name__)

# Initialize vitality configuration on module load
from .vitality_config import load_vitality_config
load_vitality_config()
