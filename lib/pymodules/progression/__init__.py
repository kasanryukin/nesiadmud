"""
Progression Module
==================
Complete character progression system including skills, experience pools, and leveling.

REPLACE THE ENTIRE __init__.py WITH THIS VERSION
"""

import os
import importlib
import mud
import auxiliary
import storage
from . import yaml_parser as yaml

mud.log_string("Progression: Starting module initialization...")

"""
Add this to progression/__init__.py AFTER imports but BEFORE module loading.

This installs the auxiliary data structures on all characters using the proper auxiliary system.
"""

# Define auxiliary data classes
class SkillsAuxData:
    """Stores skill groups and character skill placement"""
    def __init__(self, set=None):
        self.groups = {}
        self.class_name = None
        if set:
            self.restore(set)
    
    def store(self):
        """Serialize to StorageSet for saving"""
        set = storage.StorageSet()
        set.storeString("class_name", self.class_name if self.class_name else "Unknown")
        # TODO: Serialize skill groups when we have serializable format for them
        return set
    
    def restore(self, set):
        """Restore from StorageSet"""
        self.class_name = set.readString("class_name")

class ExperienceAuxData:
    """Stores experience manager and pool data"""
    def __init__(self, set=None):
        self.manager = None
        if set:
            self.restore(set)
    
    def store(self):
        """Serialize to StorageSet for saving"""
        set = storage.StorageSet()
        # Manager is recreated on load, don't serialize it
        return set
    
    def restore(self, set):
        """Restore from StorageSet"""
        # Manager will be recreated when needed
        pass

class LevelingAuxData:
    """Stores leveling progress and requirements"""
    def __init__(self, set=None):
        self.current_level = 1
        self.experience_points = 0
        self.class_name = 'Unknown'
        self.level_definitions = {}
        if set:
            self.restore(set)
    
    def store(self):
        """Serialize to StorageSet for saving"""
        set = storage.StorageSet()
        set.storeInt("current_level", self.current_level)
        set.storeInt("experience_points", self.experience_points)
        set.storeString("class_name", self.class_name if self.class_name else "Unknown")
        # TODO: Serialize level_definitions when we have a format for them
        return set
    
    def restore(self, set):
        """Restore from StorageSet"""
        self.current_level = set.readInt("current_level")
        self.experience_points = set.readInt("experience_points")
        # Handle old pfiles that don't have class_name yet
        self.class_name = set.readString("class_name") if set.contains("class_name") else "Unknown"
        # level_definitions will be recreated from class config on next setup

def install_progression_auxiliaries():
    """Install all progression system auxiliaries on characters"""
    try:
        mud.log_string("Progression: Installing auxiliary data...")
        
        auxiliary.install("skills", SkillsAuxData, "character")
        auxiliary.install("experience", ExperienceAuxData, "character")
        auxiliary.install("leveling", LevelingAuxData, "character")
        # Note: TDP is handled by attributes module, progression just grants it
        
        mud.log_string("Progression: Auxiliary data installed on characters")
        return True
    except Exception as e:
        mud.log_string("ERROR: Failed to install progression auxiliaries: %s" % str(e))
        import traceback
        mud.log_string(traceback.format_exc())
        return False

__all__ = []

# Compile list of modules in dependency order
# CRITICAL: tdp must come before experience (experience imports tdp)
_modules = [
    'skills',        # Base skill definitions (no dependencies)
    'tdp',           # TDP management (depends on attributes, but imported lazily)
    'experience',    # Experience pools (depends on skills, tdp)
    'leveling',      # Level progression (depends on skills)
    'integration',   # Main API (depends on all above)
]

__all__ = _modules

install_progression_auxiliaries()
mud.log_string("Progression: Starting module initialization...")

try:
    # Import modules in dependency order
    for module_name in _modules:
        mud.log_string(f"Progression: Importing {module_name}...")
        importlib.import_module('.' + module_name, package=__name__)
        mud.log_string(f"Progression: {module_name} imported successfully")
    
    # Initialize the progression module
    from . import integration
    integration.init_progression()
    
    # Register all commands
    integration.register_all_commands()
    
    mud.log_string("Progression: Module loaded successfully")
    
except Exception as e:
    mud.log_string(f"Progression: FAILED to load: {str(e)}")
    import traceback
    mud.log_string(traceback.format_exc())


# =============================================================================
# PUBLIC API - Import commonly used functions
# =============================================================================

from .skills import (
    get_skill_registry,
    get_skill,
    get_skill_rank,
    get_skill_rank_with_fraction,
    get_all_skills_for_character,
    get_skill_placement,
    lookup_skill_by_weapon_class,
    lookup_skill_by_armor_type,
    get_skills_in_category,
)

from .experience import (
    get_experience_manager,
    add_skill_exp,
    get_skill_field_exp,
    get_pool_status,
)

from .leveling import (
    get_current_level,
    get_level_definition,
    get_next_level_progress,
    check_level_up,
)

from .integration import (
    setup_progression,
    on_character_login,
    on_character_logout,
    on_heartbeat,
    on_skill_rank_gained,
)

from .tdp import (
    grant_tdp_for_skill_rank,
    grant_tdp_for_level,
    get_available_tdp,
    get_spent_tdp,
    get_total_tdp,
)


# =============================================================================
# USAGE GUIDE
# =============================================================================

"""
Quick Integration Guide:

1. CHARACTER CREATION (with class selection):
   ──────────────────────────────────────────
   from progression import setup_progression
   import yaml
   
   # Load class config
   with open('config/classes/warrior.yml', 'r') as f:
       class_config = yaml.safe_load(f)
   
   setup_progression(character, class_config)

2. CHARACTER LOGIN:
   ────────────────
   from progression import on_character_login
   on_character_login(character)

3. CHARACTER LOGOUT:
   ──────────────────
   from progression import on_character_logout
   on_character_logout(character)

4. CHARACTER HEARTBEAT:
   ─────────────────────
   from progression import on_heartbeat
   on_heartbeat(character)

5. SKILL RANK INCREASE (from combat/crafting/etc):
   ────────────────────────────────────────────────
   from progression import on_skill_rank_gained
   on_skill_rank_gained(character, "Long Blades", 9.5, 10.0)

6. ADD FIELD EXPERIENCE:
   ──────────────────────
   from progression import add_skill_exp
   
   # Combat hit
   add_skill_exp(ch, "Melee Combat", 15, source="combat")
   
   # Used a weapon
   add_skill_exp(ch, "Long Blades", 10, source="combat")
   
   # Forged an item
   add_skill_exp(ch, "Forging", 20, source="crafting")

7. GET ITEM'S APPLICABLE SKILL:
   ────────────────────────────
   from progression import lookup_skill_by_weapon_class
   
   # In gear system:
   skill_name = lookup_skill_by_weapon_class("long_blades")
   # Returns: "Long Blades"

8. QUERY CHARACTER PROGRESSION:
   ────────────────────────────
   from progression import (
       get_current_level,
       get_next_level_progress,
       get_skill_rank,
       get_pool_status,
   )
   
   level = get_current_level(ch)
   progress, unmet = get_next_level_progress(ch)
   rank = get_skill_rank(ch, "Melee Combat")
   status = get_pool_status(ch, "Long Blades")
"""