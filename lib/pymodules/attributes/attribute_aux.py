"""
Attribute Auxiliary Data
=========================
Manages character attribute data storage using NakedMud's auxiliary system.
This attaches attribute values to character objects.
"""

import random
import mudsys
import storage
from . import attribute_data


class AttributeAuxData:
    """
    Stores a character's attribute values and TDP.
    This class gets attached to each character as auxiliary data.
    """
    
    def __init__(self, set=None):
        """
        Initialize with baseline human values or from a storage set.
        """
        if set is None:
            # Default values
            self.strength = 10
            self.reflex = 10
            self.agility = 10
            self.charisma = 10
            self.discipline = 10
            self.wisdom = 10
            self.intelligence = 10
            self.stamina = 10
            self.tdp_available = 0
            self.tdp_spent = 0
            self.initialized = False
        else:
            # Load from storage set
            self.strength = set.readInt("strength")
            self.reflex = set.readInt("reflex")
            self.agility = set.readInt("agility")
            self.charisma = set.readInt("charisma")
            self.discipline = set.readInt("discipline")
            self.wisdom = set.readInt("wisdom")
            self.intelligence = set.readInt("intelligence")
            self.stamina = set.readInt("stamina")
            self.tdp_available = set.readInt("tdp_available")
            self.tdp_spent = set.readInt("tdp_spent")
            self.initialized = set.readBool("initialized")
    
    
    def get_attribute(self, attr_name):
        """Get the value of an attribute by name."""
        return getattr(self, attr_name, None)
    
    
    def set_attribute(self, attr_name, value):
        """Set an attribute value (with validation)."""
        validated_value = attribute_data.validate_attribute_value(attr_name, value)
        if hasattr(self, attr_name):
            setattr(self, attr_name, validated_value)
            return True
        return False
    
    
    def modify_attribute(self, attr_name, amount):
        """Add or subtract from an attribute."""
        current = self.get_attribute(attr_name)
        if current is None:
            return 0
        new_value = current + amount
        self.set_attribute(attr_name, new_value)
        return self.get_attribute(attr_name)
    
    
    def get_all_attributes(self):
        """Get a dictionary of all current attribute values."""
        return {
            "strength": self.strength,
            "reflex": self.reflex,
            "agility": self.agility,
            "charisma": self.charisma,
            "discipline": self.discipline,
            "wisdom": self.wisdom,
            "intelligence": self.intelligence,
            "stamina": self.stamina
        }
    
    
    def add_tdp(self, amount):
        """Grant TDP to the character."""
        self.tdp_available += amount
    
    
    def spend_tdp(self, amount):
        """Spend TDP (e.g., training an attribute)."""
        if self.tdp_available >= amount:
            self.tdp_available -= amount
            self.tdp_spent += amount
            return True
        return False
    
    
    def train_attribute(self, attr_name, points=1):
        """Train an attribute using TDP."""
        current_value = self.get_attribute(attr_name)
        if current_value is None:
            return (False, 0, "Invalid attribute.")
        
        cost = attribute_data.calculate_tdp_cost(current_value, current_value + points)
        
        if cost > self.tdp_available:
            return (False, cost, f"You need {cost} TDP but only have {self.tdp_available}.")
        
        if not self.spend_tdp(cost):
            return (False, cost, "Failed to spend TDP.")
        
        new_value = self.modify_attribute(attr_name, points)
        return (True, cost, f"Trained {attr_name} from {current_value} to {new_value} for {cost} TDP.")
    
    
    def initialize_for_race(self, race_name):
        """Set starting attributes based on race."""
        try:
            import entities.entity_config as entity_config
            race_config = entity_config.get_race_config()
            race = race_config.get_race(race_name)
            
            if race and hasattr(race, 'base_attributes'):
                racial_bases = race.base_attributes
            else:
                racial_bases = attribute_data.HUMAN_BASELINE.copy()
        except (ImportError, AttributeError):
            racial_bases = attribute_data.HUMAN_BASELINE.copy()
        
        variance = attribute_data.RACIAL_VARIANCE
        for attr_name in attribute_data.get_attribute_names():
            base_value = racial_bases.get(attr_name, 10)
            rolled_value = random.randint(base_value - variance, base_value + variance)
            self.set_attribute(attr_name, rolled_value)
        
        starting_tdp = attribute_data.calculate_starting_tdp(self.get_all_attributes())
        self.tdp_available = starting_tdp
        self.initialized = True
    
    
    def copyTo(self, other):
        """Copy this data to another AttributeAuxData instance."""
        other.strength = self.strength
        other.reflex = self.reflex
        other.agility = self.agility
        other.charisma = self.charisma
        other.discipline = self.discipline
        other.wisdom = self.wisdom
        other.intelligence = self.intelligence
        other.stamina = self.stamina
        other.tdp_available = self.tdp_available
        other.tdp_spent = self.tdp_spent
        other.initialized = self.initialized
    
    
    def copy(self):
        """Create a copy of this auxiliary data."""
        new_aux = AttributeAuxData()
        self.copyTo(new_aux)
        return new_aux
    
    
    def store(self):
        """Convert this data to a format that can be saved to disk."""
        set = storage.StorageSet()
        set.storeInt("strength", self.strength)
        set.storeInt("reflex", self.reflex)
        set.storeInt("agility", self.agility)
        set.storeInt("charisma", self.charisma)
        set.storeInt("discipline", self.discipline)
        set.storeInt("wisdom", self.wisdom)
        set.storeInt("intelligence", self.intelligence)
        set.storeInt("stamina", self.stamina)
        set.storeInt("tdp_available", self.tdp_available)
        set.storeInt("tdp_spent", self.tdp_spent)
        set.storeBool("initialized", self.initialized)
        return set


def get_attributes(ch):
    """
    Get a character's attribute auxiliary data.
    """
    return ch.getAuxiliary("attribute_data")


def ensure_attributes(ch):
    """
    Make sure a character has attribute data installed.
    """
    aux = get_attributes(ch)
    if aux is None:
        # In Python, auxiliary data is auto-created when accessed
        # if it's been properly installed
        return ch.getAuxiliary("attribute_data")
    return aux
