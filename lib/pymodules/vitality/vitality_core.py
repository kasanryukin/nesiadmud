"""
Vitality Core Module
====================
Manages character HP (Health Points), SP (Spell Points), and EP (Energy Points).

This module calculates max vitality from attributes and provides damage/healing
functions. It serves as the foundation for injury and death systems.

Formulas (from attribute_data.py):
- HP = stamina + ((strength + discipline) * 0.125)
- SP = intelligence + ((discipline + wisdom) * 0.25)
- EP = stamina + ((discipline + reflex + strength + agility) * 0.125)
"""

import math
import storage
import hooks
import mud

# Try to import attributes module
try:
    import attributes.attribute_aux as attribute_aux
    import attributes.attribute_data as attribute_data
    ATTRIBUTES_AVAILABLE = True
except ImportError:
    ATTRIBUTES_AVAILABLE = False
    mud.log_string("vitality_core: Attributes module not available")


class VitalityAuxData:
    """
    Stores character vitality data (HP, SP, EP).
    Attached to characters as auxiliary data.
    """
    
    def __init__(self, set=None):
        """Initialize with default values or load from storage set."""
        if set is None:
            # Default values - will be recalculated from attributes
            self.hp = 100.0
            self.max_hp = 100.0
            self.sp = 100.0
            self.max_sp = 100.0
            self.ep = 100.0
            self.max_ep = 100.0
            
            # Regeneration tracking
            self.last_regen_tick = 0
            
            # Death tracking (for future death.py module)
            self.is_dead = False
            self.death_count = 0
            
            # Injury tracking (for future injury.py module)
            self.injuries = {}  # {body_part: injury_level}
            
            # Status flags
            self.initialized = False
        else:
            # Load from storage set
            self.hp = set.readDouble("hp")
            self.max_hp = set.readDouble("max_hp")
            self.sp = set.readDouble("sp")
            self.max_sp = set.readDouble("max_sp")
            self.ep = set.readDouble("ep")
            self.max_ep = set.readDouble("max_ep")
            self.last_regen_tick = set.readInt("last_regen_tick")
            self.is_dead = set.readBool("is_dead")
            self.death_count = set.readInt("death_count")
            self.initialized = set.readBool("initialized")
            
            # Load injuries dict (for future use)
            self.injuries = {}
            if set.contains("injuries"):
                injury_set = set.readSet("injuries")
                # TODO: Parse injury data when injury.py is implemented
    
    
    def copyTo(self, other):
        """Copy this data to another VitalityAuxData instance."""
        other.hp = self.hp
        other.max_hp = self.max_hp
        other.sp = self.sp
        other.max_sp = self.max_sp
        other.ep = self.ep
        other.max_ep = self.max_ep
        other.last_regen_tick = self.last_regen_tick
        other.is_dead = self.is_dead
        other.death_count = self.death_count
        other.injuries = self.injuries.copy()
        other.initialized = self.initialized
    
    
    def copy(self):
        """Create a copy of this auxiliary data."""
        new_aux = VitalityAuxData()
        self.copyTo(new_aux)
        return new_aux
    
    
    def store(self):
        """Convert this data to a StorageSet for saving."""
        set = storage.StorageSet()
        
        set.storeDouble("hp", self.hp)
        set.storeDouble("max_hp", self.max_hp)
        set.storeDouble("sp", self.sp)
        set.storeDouble("max_sp", self.max_sp)
        set.storeDouble("ep", self.ep)
        set.storeDouble("max_ep", self.max_ep)
        set.storeInt("last_regen_tick", self.last_regen_tick)
        set.storeBool("is_dead", self.is_dead)
        set.storeInt("death_count", self.death_count)
        set.storeBool("initialized", self.initialized)
        
        # Store injuries (placeholder for future injury.py)
        # injury_set = storage.StorageSet()
        # set.storeSet("injuries", injury_set)
        
        return set

def get_vitality(ch):
    """
    Get a character's vitality auxiliary data.
    
    Args:
        ch: Character object
    
    Returns:
        VitalityAuxData: The character's vitality data, or None
    """
    return ch.getAuxiliary("vitality_data")


def ensure_vitality(ch):
    """
    Ensure a character has vitality data installed.
    
    Args:
        ch: Character object
    
    Returns:
        VitalityAuxData: The character's vitality data
    """
    aux = get_vitality(ch)
    if aux is None:
        # Auxiliary data is auto-created when accessed if properly installed
        return ch.getAuxiliary("vitality_data")
    return aux


def get_vitality_percent(ch, vitality_type="hp"):
    """
    Get the percentage of a vitality pool.
    
    Args:
        ch: Character object
        vitality_type: "hp", "sp", or "ep"
    
    Returns:
        float: Percentage (0.0 to 100.0)
    """
    vit_aux = get_vitality(ch)
    if not vit_aux:
        return 100.0
    
    if vitality_type == "hp":
        return (vit_aux.hp / vit_aux.max_hp * 100.0) if vit_aux.max_hp > 0 else 0.0
    elif vitality_type == "sp":
        return (vit_aux.sp / vit_aux.max_sp * 100.0) if vit_aux.max_sp > 0 else 0.0
    elif vitality_type == "ep":
        return (vit_aux.ep / vit_aux.max_ep * 100.0) if vit_aux.max_ep > 0 else 0.0
    
    return 0.0


def get_vitality_color(percent):
    """
    Get a color code based on vitality percentage.
    
    Args:
        percent: Vitality percentage (0-100)
    
    Returns:
        str: Color code for display
    """
    if percent >= 75:
        return "{G"  # Green - healthy
    elif percent >= 50:
        return "{Y"  # Yellow - wounded
    elif percent >= 25:
        return "{y"  # Dark yellow - badly wounded
    else:
        return "{R"  # Red - critical

def calculate_max_hp(ch):
    """
    Calculate maximum HP from character attributes.
    Formula: stamina + ((strength + discipline) * 0.125)
    
    Args:
        ch: Character object
    
    Returns:
        float: Maximum HP (rounded up)
    """
    if not ATTRIBUTES_AVAILABLE:
        return 100.0
    
    attr_aux = attribute_aux.get_attributes(ch)
    if not attr_aux:
        return 100.0
    
    stamina = attr_aux.get_attribute("stamina")
    strength = attr_aux.get_attribute("strength")
    discipline = attr_aux.get_attribute("discipline")
    
    result = stamina + ((strength + discipline) * 0.125)
    
    # TODO: Add guild bonuses
    # TODO: Add equipment bonuses
    # TODO: Add temporary buffs
    
    return math.ceil(result)


def calculate_max_sp(ch):
    """
    Calculate maximum SP from character attributes.
    Formula: intelligence + ((discipline + wisdom) * 0.25)
    
    Args:
        ch: Character object
    
    Returns:
        float: Maximum SP (rounded up)
    """
    if not ATTRIBUTES_AVAILABLE:
        return 100.0
    
    attr_aux = attribute_aux.get_attributes(ch)
    if not attr_aux:
        return 100.0
    
    intelligence = attr_aux.get_attribute("intelligence")
    discipline = attr_aux.get_attribute("discipline")
    wisdom = attr_aux.get_attribute("wisdom")
    
    result = intelligence + ((discipline + wisdom) * 0.25)
    
    # TODO: Add guild bonuses
    # TODO: Add equipment bonuses
    # TODO: Add temporary buffs
    
    return math.ceil(result)


def calculate_max_ep(ch):
    """
    Calculate maximum EP from character attributes.
    Formula: stamina + ((discipline + reflex + strength + agility) * 0.125)
    
    Args:
        ch: Character object
    
    Returns:
        float: Maximum EP (rounded up)
    """
    if not ATTRIBUTES_AVAILABLE:
        return 100.0
    
    attr_aux = attribute_aux.get_attributes(ch)
    if not attr_aux:
        return 100.0
    
    stamina = attr_aux.get_attribute("stamina")
    discipline = attr_aux.get_attribute("discipline")
    reflex = attr_aux.get_attribute("reflex")
    strength = attr_aux.get_attribute("strength")
    agility = attr_aux.get_attribute("agility")
    
    result = stamina + ((discipline + reflex + strength + agility) * 0.125)
    
    # TODO: Add guild bonuses
    # TODO: Add equipment bonuses
    # TODO: Add temporary buffs
    
    return math.ceil(result)


def recalculate_vitality(ch):
    """
    Recalculate max HP/SP/EP from current attributes.
    Called when attributes change (training, gear, etc.)
    
    Args:
        ch: Character object
    """
    vit_aux = get_vitality(ch)
    if not vit_aux:
        return
    
    # Store old maximums
    old_max_hp = vit_aux.max_hp
    old_max_sp = vit_aux.max_sp
    old_max_ep = vit_aux.max_ep
    
    # Calculate new maximums
    new_max_hp = calculate_max_hp(ch)
    new_max_sp = calculate_max_sp(ch)
    new_max_ep = calculate_max_ep(ch)
    
    # Calculate the ratio of change to adjust current values proportionally
    if old_max_hp > 0:
        hp_ratio = vit_aux.hp / old_max_hp
        vit_aux.hp = min(new_max_hp, hp_ratio * new_max_hp)
    else:
        vit_aux.hp = new_max_hp
    
    if old_max_sp > 0:
        sp_ratio = vit_aux.sp / old_max_sp
        vit_aux.sp = min(new_max_sp, sp_ratio * new_max_sp)
    else:
        vit_aux.sp = new_max_sp
    
    if old_max_ep > 0:
        ep_ratio = vit_aux.ep / old_max_ep
        vit_aux.ep = min(new_max_ep, ep_ratio * new_max_ep)
    else:
        vit_aux.ep = new_max_ep
    
    # Update maximums
    vit_aux.max_hp = new_max_hp
    vit_aux.max_sp = new_max_sp
    vit_aux.max_ep = new_max_ep
    
    mud.log_string(f"Recalculated vitality for {ch.name}: HP {old_max_hp:.0f}→{new_max_hp:.0f}, "
                   f"SP {old_max_sp:.0f}→{new_max_sp:.0f}, EP {old_max_ep:.0f}→{new_max_ep:.0f}")


def initialize_vitality(ch):
    """
    Initialize vitality for a new character.
    Calculates maximums from attributes and sets current to max.
    
    Args:
        ch: Character object
    """
    vit_aux = get_vitality(ch)
    if not vit_aux:
        return
    
    if vit_aux.initialized:
        return
    
    # Calculate maximums from attributes
    vit_aux.max_hp = calculate_max_hp(ch)
    vit_aux.max_sp = calculate_max_sp(ch)
    vit_aux.max_ep = calculate_max_ep(ch)
    
    # Set current to max
    vit_aux.hp = vit_aux.max_hp
    vit_aux.sp = vit_aux.max_sp
    vit_aux.ep = vit_aux.max_ep
    
    vit_aux.initialized = True
    
    mud.log_string(f"Initialized vitality for {ch.name}: "
                   f"HP {vit_aux.max_hp:.0f}, SP {vit_aux.max_sp:.0f}, EP {vit_aux.max_ep:.0f}")

