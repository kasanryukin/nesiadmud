"""
Vitality Configuration Management

Handles loading and saving of vitality system configuration including
default stats, regeneration rates, and status messages.
"""

import storage
import mud
import os

# Global vitality configuration
vitality_config = None
vitality_config_file = "misc/vitality-config"

def create_default_vitality_config():
    """Create default vitality configuration file"""
    global vitality_config
    
    vitality_config = VitalityConfig()
    save_vitality_config()
    mud.log_string("Created default vitality configuration.")

class VitalityConfig:
    """Manages vitality system configuration"""
    
    def __init__(self, set=None):
        # Default values
        self.hp_hitdie = 10
        self.sp_hitdie = 10
        self.ep_hitdie = 10
        self.regen_heartbeat = 10
        self.hp_regen = 1
        self.sp_regen = 1
        self.ep_regen = 1
        self.corpse_object = "corpse@limbo"
        self.death_room = "limbo@limbo"
        self.regen_display = False
        self.regen_display_full = True
        
        # Status messages
        self.hp_status = {}
        self.sp_status = {}
        self.ep_status = {}
        
        if set is not None:
            self.read(set)
        else:
            self._create_default_status_messages()
    
    def _create_default_status_messages(self):
        """Create default status messages"""
        self.hp_status = {
            0: "You are at death's door.",
            10: "You are gushing vital fluids.",
            20: "You are bleeding profusely.",
            30: "You are badly wounded.",
            40: "You are wounded.",
            50: "You have moderate injuries.",
            60: "You have some cuts and bruises.",
            70: "You have light scratches.",
            80: "You have minor scrapes.",
            90: "You are in good condition.",
            100: "You are in perfect condition."
        }
        
        self.sp_status = {
            0: "You are magically drained.",
            10: "You are severely mentally exhausted.",
            20: "You are mentally exhausted.",
            30: "You are very mentally fatigued.",
            40: "You are mentally fatigued.",
            50: "You are moderately drained.",
            60: "You are slightly drained.",
            70: "You are feeling mentally sharp.",
            80: "You are mentally focused.",
            90: "You are mentally alert.",
            100: "You are mentally sharp and focused."
        }
        
        self.ep_status = {
            0: "You are utterly exhausted.",
            10: "You are completely drained.",
            20: "You are severely winded.",
            30: "You are breathing very heavily.",
            40: "You are breathing heavily.",
            50: "You are moderately tired.",
            60: "You are slightly winded.",
            70: "You are feeling energetic.",
            80: "You are feeling strong.",
            90: "You are feeling vigorous.",
            100: "You are fully energized."
        }
    
    def read(self, set):
        """Read configuration from storage set"""
        # Read defaults
        if set.contains("defaults"):
            defaults = set.readSet("defaults")
            if defaults.contains("hp_hitdie"):
                self.hp_hitdie = defaults.readInt("hp_hitdie")
            if defaults.contains("sp_hitdie"):
                self.sp_hitdie = defaults.readInt("sp_hitdie")
            if defaults.contains("ep_hitdie"):
                self.ep_hitdie = defaults.readInt("ep_hitdie")
            if defaults.contains("regen_heartbeat"):
                self.regen_heartbeat = defaults.readInt("regen_heartbeat")
            if defaults.contains("hp_regen"):
                self.hp_regen = defaults.readInt("hp_regen")
            if defaults.contains("sp_regen"):
                self.sp_regen = defaults.readInt("sp_regen")
            if defaults.contains("ep_regen"):
                self.ep_regen = defaults.readInt("ep_regen")
            if defaults.contains("corpse_object"):
                self.corpse_object = defaults.readString("corpse_object")
            if defaults.contains("death_room"):
                self.death_room = defaults.readString("death_room")
            if defaults.contains("regen_display"):
                self.regen_display = defaults.readBool("regen_display")
            if defaults.contains("regen_display_full"):
                self.regen_display_full = defaults.readBool("regen_display_full")
        
        # Read status messages
        if set.contains("status"):
            status = set.readSet("status")
            
            if status.contains("hp_status"):
                hp_set = status.readSet("hp_status")
                self.hp_status = {}
                # Use readList and iterate through sets like other modules
                hp_list = hp_set.readList("messages") if hp_set.contains("messages") else None
                if hp_list:
                    for msg_set in hp_list.sets():
                        threshold = msg_set.readString("threshold")
                        message = msg_set.readString("message")
                        if threshold and message:
                            self.hp_status[int(threshold)] = message
            
            if status.contains("sp_status"):
                sp_set = status.readSet("sp_status")
                self.sp_status = {}
                sp_list = sp_set.readList("messages") if sp_set.contains("messages") else None
                if sp_list:
                    for msg_set in sp_list.sets():
                        threshold = msg_set.readString("threshold")
                        message = msg_set.readString("message")
                        if threshold and message:
                            self.sp_status[int(threshold)] = message
            
            if status.contains("ep_status"):
                ep_set = status.readSet("ep_status")
                self.ep_status = {}
                ep_list = ep_set.readList("messages") if ep_set.contains("messages") else None
                if ep_list:
                    for msg_set in ep_list.sets():
                        threshold = msg_set.readString("threshold")
                        message = msg_set.readString("message")
                        if threshold and message:
                            self.ep_status[int(threshold)] = message
        
        # Create defaults if status messages are empty
        if not self.hp_status or not self.sp_status or not self.ep_status:
            self._create_default_status_messages()
    
    def store(self):
        """Store configuration to storage set"""
        set = storage.StorageSet()
        
        # Store defaults
        defaults = storage.StorageSet()
        defaults.storeInt("hp_hitdie", self.hp_hitdie)
        defaults.storeInt("sp_hitdie", self.sp_hitdie)
        defaults.storeInt("ep_hitdie", self.ep_hitdie)
        defaults.storeInt("regen_heartbeat", self.regen_heartbeat)
        defaults.storeInt("hp_regen", self.hp_regen)
        defaults.storeInt("sp_regen", self.sp_regen)
        defaults.storeInt("ep_regen", self.ep_regen)
        defaults.storeString("corpse_object", self.corpse_object)
        defaults.storeString("death_room", self.death_room)
        defaults.storeBool("regen_display", self.regen_display)
        defaults.storeBool("regen_display_full", self.regen_display_full)
        set.storeSet("defaults", defaults)
        
        # Store status messages
        status = storage.StorageSet()
        
        # Store HP status messages as list
        hp_set = storage.StorageSet()
        hp_list = storage.StorageList()
        for threshold, message in self.hp_status.items():
            msg_set = storage.StorageSet()
            msg_set.storeString("threshold", str(threshold))
            msg_set.storeString("message", message)
            hp_list.add(msg_set)
        hp_set.storeList("messages", hp_list)
        status.storeSet("hp_status", hp_set)
        
        # Store SP status messages as list
        sp_set = storage.StorageSet()
        sp_list = storage.StorageList()
        for threshold, message in self.sp_status.items():
            msg_set = storage.StorageSet()
            msg_set.storeString("threshold", str(threshold))
            msg_set.storeString("message", message)
            sp_list.add(msg_set)
        sp_set.storeList("messages", sp_list)
        status.storeSet("sp_status", sp_set)
        
        # Store EP status messages as list
        ep_set = storage.StorageSet()
        ep_list = storage.StorageList()
        for threshold, message in self.ep_status.items():
            msg_set = storage.StorageSet()
            msg_set.storeString("threshold", str(threshold))
            msg_set.storeString("message", message)
            ep_list.add(msg_set)
        ep_set.storeList("messages", ep_list)
        status.storeSet("ep_status", ep_set)
        
        set.storeSet("status", status)
        return set
    
    def get_status_message(self, stat_type, current, maximum):
        """Get status message for a stat based on percentage"""
        if maximum <= 0:
            return f"You have no {stat_type}."
        
        percentage = int((current * 100) / maximum)
        
        # Get the appropriate status dict
        if stat_type == "hp":
            status_dict = self.hp_status
        elif stat_type == "sp":
            status_dict = self.sp_status
        elif stat_type == "ep":
            status_dict = self.ep_status
        else:
            return f"Unknown stat type: {stat_type}"
        
        # Find the highest threshold we meet
        best_threshold = 0
        for threshold in status_dict.keys():
            if percentage >= threshold and threshold >= best_threshold:
                best_threshold = threshold
        
        return status_dict.get(best_threshold, f"No status message for {stat_type}")

def load_vitality_config():
    """Load vitality configuration from storage file"""
    global vitality_config
    
    config_file = vitality_config_file
    
    if not os.path.exists(config_file):
        create_default_vitality_config()
        return
    
    try:
        storage_set = storage.StorageSet(config_file)
        vitality_config = VitalityConfig(storage_set)
        storage_set.close()
        mud.log_string("Vitality configuration loaded successfully.")
    except Exception as e:
        mud.log_string(f"Error loading vitality config: {e}. Creating defaults.")
        create_default_vitality_config()

def save_vitality_config():
    """Save vitality configuration to storage file"""
    global vitality_config
    
    config_file = vitality_config_file
    try:
        vitality_config_data = vitality_config.store()
        vitality_config_data.write(config_file)
        vitality_config_data.close()
        mud.log_string("Vitality configuration saved successfully.")
    except Exception as e:
        mud.log_string(f"Error saving vitality configuration: {e}")

def get_vitality_config():
    """Get the global vitality configuration"""
    return vitality_config
