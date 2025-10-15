"""
Attributes Module for NakedMud
================================
Manages character attributes (STR, REF, AGI, CHA, DIS, WIS, INT, STA)
and their effects on game mechanics.

This module provides:
- Attribute definitions and valid ranges
- Auxiliary data storage for character attributes
- TDP (Time Development Points) system for attribute training
- Derived stat calculations (carrying capacity, etc.)
- Integration with vitality for HP/SP/EP calculations
- Integration with entities for racial attribute modifiers
"""
import os
import importlib
import mudsys
import mud

mud.log_string("Attributes module: Starting initialization...")

__all__ = []

# Compile a list of all our modules
for fl in os.listdir(__path__[0]):
    if fl.endswith(".py") and not (fl == "__init__.py" or fl.startswith(".")):
        __all__.append(fl[:-3])

# Import all of our modules so they can register and initialize
__all__ = ['attribute_data', 'attribute_aux', 'commands']

try:
    for module in __all__:
        mud.log_string(f"Attributes: Importing {module}...")
        importlib.import_module('.' + module, package=__name__)
        mud.log_string(f"Attributes: {module} imported successfully")
    
    # Import the modules we need
    from . import attribute_aux
    from . import commands
    import auxiliary
    
    # Install auxiliary data using Python's auxiliary system
    auxiliary.install("attribute_data", attribute_aux.AttributeAuxData, "character")
    mud.log_string("Attributes: Auxiliary data installed on characters")
    
    # Register commands
    commands.register_commands()
    
    mud.log_string("Attributes module loaded successfully")
    
except Exception as e:
    mud.log_string(f"Attributes module FAILED to load: {str(e)}")
    import traceback
    mud.log_string(traceback.format_exc())
