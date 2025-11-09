"""
injury_aux.py
=============
Auxiliary data class for character injuries.
Stores wounds, scars, and injury progression tracking.
"""

import mud
import storage
import json


class InjuryAuxData:
    """
    Stores character injury data (wounds, scars).
    Attached to characters as auxiliary data.
    
    Uses JSON serialization to store complex wound/scar data
    since StorageSet doesn't support dynamic key iteration.
    """
    
    def __init__(self, set=None):
        """Initialize with default values or load from storage set."""
        if set is None:
            # Default values
            self.wounds = {}              # body_part -> wound dict
            self.scars = {}               # body_part -> scar severity
            self.progression_counter = 0  # Counter for infection/progression checks
        else:
            # Load from storage set
            self.progression_counter = set.readInt("progression_counter") if set.contains("progression_counter") else 0
            
            # Load wounds from JSON string
            self.wounds = {}
            try:
                if set.contains("wounds_json"):
                    wounds_json = set.readString("wounds_json")
                    self.wounds = json.loads(wounds_json)
            except Exception as e:
                mud.log_string(f"ERROR loading wounds: {str(e)}")
                self.wounds = {}
            
            # Load scars from JSON string
            self.scars = {}
            try:
                if set.contains("scars_json"):
                    scars_json = set.readString("scars_json")
                    self.scars = json.loads(scars_json)
            except Exception as e:
                mud.log_string(f"ERROR loading scars: {str(e)}")
                self.scars = {}
    
    def copyTo(self, other):
        """Copy this data to another InjuryAuxData instance."""
        other.wounds = {}
        for body_part, wound in self.wounds.items():
            other.wounds[body_part] = {
                "type": wound["type"],
                "severity": wound["severity"],
                "status": wound["status"].copy() if isinstance(wound["status"], list) else [],
                "age": wound["age"],
                "scar_created": wound["scar_created"]
            }
        
        other.scars = self.scars.copy()
        other.progression_counter = self.progression_counter
    
    def copy(self):
        """Create a copy of this auxiliary data."""
        new_aux = InjuryAuxData()
        self.copyTo(new_aux)
        return new_aux
    
    def store(self):
        """Convert this data to a format that can be saved to disk."""
        set = storage.StorageSet()
        
        # Store progression counter
        set.storeInt("progression_counter", self.progression_counter)
        
        # Store wounds as JSON string
        try:
            wounds_json = json.dumps(self.wounds)
            set.storeString("wounds_json", wounds_json)
        except Exception as e:
            mud.log_string(f"ERROR storing wounds: {str(e)}")
        
        # Store scars as JSON string
        try:
            scars_json = json.dumps(self.scars)
            set.storeString("scars_json", scars_json)
        except Exception as e:
            mud.log_string(f"ERROR storing scars: {str(e)}")
        
        return set


def get_injuries(ch):
    """
    Get a character's injury auxiliary data.
    """
    return ch.getAuxiliary("injury_data")


def ensure_injuries(ch):
    """
    Make sure a character has injury data installed.
    """
    aux = get_injuries(ch)
    if aux is None:
        # In Python, auxiliary data is auto-created when accessed
        # if it's been properly installed
        return ch.getAuxiliary("injury_data")
    return aux