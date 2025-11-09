"""
Vitality Module for NakedMud - DEBUG VERSION
==============================
Manages character HP, SP, and EP based on attributes.

DEBUGGING: Disabling modules one by one to find the crash source
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
__all__ = []

try:
    # Import core modules - TEST ONE AT A TIME
    mud.log_string("Vitality: About to import vitality_core...")
    from . import vitality_core
    mud.log_string("Vitality: vitality_core imported successfully")
    
    mud.log_string("Vitality: About to import injury_aux...")
    from . import injury_aux
    mud.log_string("Vitality: injury_aux imported successfully")
    
    mud.log_string("Vitality: About to import vitality_damage...")
    from . import vitality_damage
    mud.log_string("Vitality: vitality_damage imported successfully")
    
    mud.log_string("Vitality: About to import vitality_regen...")
    from . import vitality_regen
    mud.log_string("Vitality: vitality_regen imported successfully")
    
    mud.log_string("Vitality: About to import death_handler...")
    from . import death_handler
    mud.log_string("Vitality: death_handler imported successfully")
    
    mud.log_string("Vitality: About to import vitality_injury...")
    from . import vitality_injury
    mud.log_string("Vitality: vitality_injury imported successfully")
    
    mud.log_string("Vitality: About to import injury_penalties...")
    from . import injury_penalties
    mud.log_string("Vitality: injury_penalties imported successfully")
    
    mud.log_string("Vitality: About to import commands...")
    from . import commands
    mud.log_string("Vitality: commands imported successfully")
    
    mud.log_string("Vitality: Core modules imported successfully")
    
    # Install auxiliary data using Python's auxiliary system
    mud.log_string("Vitality: Installing auxiliary data...")
    auxiliary.install("vitality_data", vitality_core.VitalityAuxData, "character")
    auxiliary.install("injury_data", injury_aux.InjuryAuxData, "character")
    mud.log_string("Vitality: Auxiliary data installed on characters")
    
    # Register regeneration pulse
    mud.log_string("Vitality: Registering regeneration pulse...")
    vitality_regen.register_regen_pulse()
    mud.log_string("Vitality: Regeneration pulse registered")
    
    # Register death hooks
    mud.log_string("Vitality: Setting up death hooks...")
    death_handler.setup_death_hooks()
    mud.log_string("Vitality: Death hooks setup")
    
    # Register commands
    mud.log_string("Vitality: Registering commands...")
    commands.register_commands()
    mud.log_string("Vitality: Commands registered")
    
    # Register injury commands
    mud.log_string("Vitality: Registering injury commands...")
    vitality_injury.register_commands()
    mud.log_string("Vitality: Injury commands registered")
    
    mud.log_string("Vitality module loaded successfully")
    
except Exception as e:
    mud.log_string(f"Vitality module FAILED to load: {str(e)}")
    import traceback
    mud.log_string(traceback.format_exc())