"""
Vitality Module for NakedMud
==============================
Manages character HP, SP, and EP based on attributes.

This module provides:
- Vitality calculations from attributes
- Damage and healing functions
- Foundation for injury and death systems
- Regeneration framework
"""

import os
import importlib
import mud
import auxiliary

mud.log_string("Vitality module: Starting initialization...")

__all__ = []

# Compile a list of all our modules
for fl in os.listdir(__path__[0]):
    if fl.endswith(".py") and not (fl == "__init__.py" or fl.startswith(".")):
        __all__.append(fl[:-3])

# Import all of our modules
__all__ = ['vitality_core']

try:
    for module in __all__:
        mud.log_string(f"Vitality: Importing {module}...")
        importlib.import_module('.' + module, package=__name__)
        mud.log_string(f"Vitality: {module} imported successfully")
    
    # Import the core module
    from . import vitality_core
    from . import vitality_regen
    from . import commands
    
    # Install auxiliary data using Python's auxiliary system
    auxiliary.install("vitality_data", vitality_core.VitalityAuxData, "character")

    # Register regeneration pulse
    vitality_regen.register_regen_pulse()
    
    # Register commands
    vitality_regen.register_commands()
    commands.register_commands()
    mud.log_string("Vitality: Auxiliary data installed on characters")
    
    mud.log_string("Vitality module loaded successfully")
    
except Exception as e:
    mud.log_string(f"Vitality module FAILED to load: {str(e)}")
    import traceback
    mud.log_string(traceback.format_exc())
