"""
Forms configuration management for NakedMud.

Provides storage and management of body types, sizes, and race configurations
using the auxiliary data storage system. Follows the gear module pattern.
"""
import mud
import storage

class BodyPosition:
    """Represents a single body position with name, type, and weight."""
    
    def __init__(self, name="", pos_type="", weight=0):
        self.name = name
        self.pos_type = pos_type
        self.weight = weight
    
    def store(self, storage_set):
        """Store this body position to a storage set."""
        storage_set.storeString("name", self.name)
        storage_set.storeString("type", self.pos_type)
        storage_set.storeInt("weight", self.weight)
    
    @staticmethod
    def from_storage(storage_set):
        """Create a BodyPosition from a storage set."""
        name = storage_set.readString("name")
        pos_type = storage_set.readString("type")
        weight = storage_set.readInt("weight")
        return BodyPosition(name, pos_type, weight)

class Race:
    """Represents a race configuration with body template and PC flag."""
    
    def __init__(self, name="", abbrev="", pc_ok=False):
        self.name = name
        self.abbrev = abbrev
        self.pc_ok = pc_ok
        self.body_positions = []
        self.body_size = "medium"
    
    def add_position(self, position):
        """Add a body position to this race."""
        self.body_positions.append(position)
    
    def remove_position(self, name):
        """Remove a body position by name."""
        self.body_positions = [pos for pos in self.body_positions if pos.name != name]
    
    def get_position(self, name):
        """Get a body position by name."""
        for pos in self.body_positions:
            if pos.name == name:
                return pos
        return None
    
    def store(self, storage_set):
        """Store this race to a storage set."""
        storage_set.storeString("name", self.name)
        storage_set.storeString("abbrev", self.abbrev)
        storage_set.storeBool("pc_ok", self.pc_ok)
        storage_set.storeString("body_size", self.body_size)
        
        # Store body positions
        positions_list = storage.StorageList()
        for position in self.body_positions:
            pos_set = storage.StorageSet()
            position.store(pos_set)
            positions_list.add(pos_set)
        storage_set.storeList("body_positions", positions_list)
    
    @staticmethod
    def from_storage(storage_set):
        """Create a Race from a storage set."""
        name = storage_set.readString("name")
        abbrev = storage_set.readString("abbrev")
        pc_ok = storage_set.readBool("pc_ok")
        body_size = storage_set.readString("body_size")
        
        race = Race(name, abbrev, pc_ok)
        race.body_size = body_size
        
        # Load body positions
        positions_list = storage_set.readList("body_positions")
        for pos_set in positions_list.sets():
            position = BodyPosition.from_storage(pos_set)
            race.add_position(position)
        
        return race

class BodyTypes:
    """Manages custom body position types and sizes."""
    
    def __init__(self):
        self.bodypart_types = []
        self.bodysizes = []
    
    def add_bodypart_type(self, type_name):
        """Add a custom body part type."""
        if type_name not in self.bodypart_types:
            self.bodypart_types.append(type_name)
    
    def remove_bodypart_type(self, type_name):
        """Remove a custom body part type."""
        if type_name in self.bodypart_types:
            self.bodypart_types.remove(type_name)
    
    def add_bodysize(self, size_name):
        """Add a custom body size."""
        if size_name not in self.bodysizes:
            self.bodysizes.append(size_name)
    
    def remove_bodysize(self, size_name):
        """Remove a custom body size."""
        if size_name in self.bodysizes:
            self.bodysizes.remove(size_name)
    
    def get_bodysizes(self):
        """Get all custom body sizes."""
        return self.bodysizes
    
    def get_bodypos_types(self):
        """Get all custom body position types."""
        return self.bodypart_types
    
    def store(self, storage_set):
        """Store body types configuration to a storage set."""
        # Store bodypart types
        types_list = storage.StorageList()
        for type_name in self.bodypart_types:
            type_set = storage.StorageSet()
            type_set.storeString(type_name, "")
            types_list.add(type_set)
        storage_set.storeList("bodypart_types", types_list)
        
        # Store body sizes
        sizes_list = storage.StorageList()
        for size_name in self.bodysizes:
            size_set = storage.StorageSet()
            size_set.storeString(size_name, "")
            sizes_list.add(size_set)
        storage_set.storeList("bodysizes", sizes_list)
    
    @staticmethod
    def from_storage(storage_set):
        """Create BodyTypes from a storage set."""
        body_types = BodyTypes()
        
        # Load bodypart types
        types_list = storage_set.readList("bodypart_types")
        for type_set in types_list.sets():
            for key in type_set.keys():
                if key != "-":
                    body_types.add_bodypart_type(key)
        
        # Load body sizes
        sizes_list = storage_set.readList("bodysizes")
        for size_set in sizes_list.sets():
            for key in size_set.keys():
                if key != "-":
                    body_types.add_bodysize(key)
        
        return body_types

class RaceConfig:
    """Race configuration container."""
    
    def __init__(self):
        self.races = {}
    
    def add_race(self, race):
        """Add a race to the configuration."""
        self.races[race.name] = race
    
    def remove_race(self, name):
        """Remove a race from the configuration."""
        if name in self.races:
            del self.races[name]
    
    def get_race(self, name):
        """Get a race by name."""
        return self.races.get(name)
    
    def get_race_names(self):
        """Get a list of all race names."""
        return list(self.races.keys())
    
    def store(self, storage_set):
        """Store races as a direct list in the storage set."""
        races_list = storage.StorageList()
        for race in self.races.values():
            race_set = storage.StorageSet()
            race.store(race_set)
            races_list.add(race_set)
        storage_set.storeList("races", races_list)
    
    @staticmethod
    def from_storage(storage_set):
        """Create RaceConfig from a storage set."""
        config = RaceConfig()
        
        # Load races
        races_list = storage_set.readList("races")
        for race_set in races_list.sets():
            race = Race.from_storage(race_set)
            config.add_race(race)
        
        return config

class BodyConfig:
    """Body configuration container with proper nested structure."""
    
    def __init__(self):
        self.body_types = BodyTypes()
    
    def store(self, storage_set):
        """Store body config with nested structure: body -> part_types/sizes lists."""
        body_set = storage.StorageSet()
        
        # Store part_types as StorageList with name: value format like gear module
        part_types_list = storage.StorageList()
        for type_name in self.body_types.bodypart_types:
            type_set = storage.StorageSet()
            type_set.storeString("name", type_name)
            part_types_list.add(type_set)
        body_set.storeList("part_types", part_types_list)
        
        # Store sizes as StorageList with name: value format like gear module
        sizes_list = storage.StorageList()
        for size_name in self.body_types.bodysizes:
            size_set = storage.StorageSet()
            size_set.storeString("name", size_name)
            sizes_list.add(size_set)
        body_set.storeList("sizes", sizes_list)
        
        # Store the body set in the main storage set
        storage_set.storeSet("body", body_set)
    
    @staticmethod
    def from_storage(storage_set):
        """Create BodyConfig from a storage set."""
        config = BodyConfig()
        
        # Load body section with part_types and sizes
        try:
            body_set = storage_set.readSet("body")
            
            # Load part_types from StorageList with name: value format like gear module
            part_types_list = body_set.readList("part_types")
            for type_set in part_types_list.sets():
                type_name = type_set.readString("name")
                if type_name:
                    config.body_types.add_bodypart_type(type_name)
            
            # Load sizes from StorageList with name: value format like gear module
            sizes_list = body_set.readList("sizes")
            for size_set in sizes_list.sets():
                size_name = size_set.readString("name")
                if size_name:
                    config.body_types.add_bodysize(size_name)
        except:
            # Handle missing body section
            pass
        
        return config

# Global configuration instances
race_config = None
body_config = None

def create_default_race_config():
    """Create default race configuration with test races."""
    global race_config
    
    race_config = RaceConfig()
    
    # Create elf race - similar to human but more graceful
    elf = Race("elf", "elf", True)
    elf.body_size = "medium"
    elf.add_position(BodyPosition("floating about head", "floating about head", 0))
    elf.add_position(BodyPosition("head", "head", 2))
    elf.add_position(BodyPosition("face", "face", 2))
    elf.add_position(BodyPosition("left ear", "ear", 0))
    elf.add_position(BodyPosition("right ear", "ear", 0))
    elf.add_position(BodyPosition("neck", "neck", 1))
    elf.add_position(BodyPosition("torso", "torso", 50))
    elf.add_position(BodyPosition("about body", "about body", 0))
    elf.add_position(BodyPosition("left arm", "arm", 7))
    elf.add_position(BodyPosition("right arm", "arm", 7))
    elf.add_position(BodyPosition("left wrist", "wrist", 1))
    elf.add_position(BodyPosition("right wrist", "wrist", 1))
    elf.add_position(BodyPosition("hands", "hands", 4))
    elf.add_position(BodyPosition("left finger", "finger", 1))
    elf.add_position(BodyPosition("right finger", "finger", 1))
    elf.add_position(BodyPosition("waist", "waist", 1))
    elf.add_position(BodyPosition("legs", "legs", 18))
    elf.add_position(BodyPosition("feet", "feet", 4))
    elf.add_position(BodyPosition("left grip", "held", 0))
    elf.add_position(BodyPosition("right grip", "held", 0))
    race_config.add_race(elf)
    
    # Create hill giant race - massive humanoid
    hill_giant = Race("hill giant", "hgi", False)
    hill_giant.body_size = "huge"
    hill_giant.add_position(BodyPosition("floating about head", "floating about head", 0))
    hill_giant.add_position(BodyPosition("head", "head", 2))
    hill_giant.add_position(BodyPosition("face", "face", 2))
    hill_giant.add_position(BodyPosition("left ear", "ear", 0))
    hill_giant.add_position(BodyPosition("right ear", "ear", 0))
    hill_giant.add_position(BodyPosition("neck", "neck", 1))
    hill_giant.add_position(BodyPosition("torso", "torso", 50))
    hill_giant.add_position(BodyPosition("about body", "about body", 0))
    hill_giant.add_position(BodyPosition("left arm", "arm", 7))
    hill_giant.add_position(BodyPosition("right arm", "arm", 7))
    hill_giant.add_position(BodyPosition("left wrist", "wrist", 1))
    hill_giant.add_position(BodyPosition("right wrist", "wrist", 1))
    hill_giant.add_position(BodyPosition("hands", "hands", 4))
    hill_giant.add_position(BodyPosition("left finger", "finger", 1))
    hill_giant.add_position(BodyPosition("right finger", "finger", 1))
    hill_giant.add_position(BodyPosition("waist", "waist", 1))
    hill_giant.add_position(BodyPosition("legs", "legs", 18))
    hill_giant.add_position(BodyPosition("feet", "feet", 4))
    hill_giant.add_position(BodyPosition("left grip", "held", 0))
    hill_giant.add_position(BodyPosition("right grip", "held", 0))
    race_config.add_race(hill_giant)
    
    # Create dragon race - quadruped with wings
    dragon = Race("dragon", "dra", False)
    dragon.body_size = "gigantic"
    dragon.add_position(BodyPosition("floating about head", "floating about head", 0))
    dragon.add_position(BodyPosition("head", "head", 2))
    dragon.add_position(BodyPosition("face", "face", 2))
    dragon.add_position(BodyPosition("left ear", "ear", 0))
    dragon.add_position(BodyPosition("right ear", "ear", 0))
    dragon.add_position(BodyPosition("neck", "neck", 8))
    dragon.add_position(BodyPosition("torso", "torso", 35))
    dragon.add_position(BodyPosition("about body", "about body", 0))
    dragon.add_position(BodyPosition("wings", "wings", 20))
    dragon.add_position(BodyPosition("left foreleg", "leg", 8))
    dragon.add_position(BodyPosition("right foreleg", "leg", 8))
    dragon.add_position(BodyPosition("left hindleg", "leg", 6))
    dragon.add_position(BodyPosition("right hindleg", "leg", 6))
    dragon.add_position(BodyPosition("legs", "legs", 14))
    dragon.add_position(BodyPosition("feet", "feet", 8))
    dragon.add_position(BodyPosition("tail", "tail", 7))
    dragon.add_position(BodyPosition("left grip", "held", 0))
    dragon.add_position(BodyPosition("right grip", "held", 0))
    race_config.add_race(dragon)
    
    # Create centaur race - human torso on horse body
    centaur = Race("centaur", "cen", True)
    centaur.body_size = "large"
    centaur.add_position(BodyPosition("floating about head", "floating about head", 0))
    centaur.add_position(BodyPosition("head", "head", 2))
    centaur.add_position(BodyPosition("face", "face", 2))
    centaur.add_position(BodyPosition("left ear", "ear", 0))
    centaur.add_position(BodyPosition("right ear", "ear", 0))
    centaur.add_position(BodyPosition("neck", "neck", 1))
    centaur.add_position(BodyPosition("torso", "torso", 25))
    centaur.add_position(BodyPosition("about body", "about body", 0))
    centaur.add_position(BodyPosition("left arm", "arm", 7))
    centaur.add_position(BodyPosition("right arm", "arm", 7))
    centaur.add_position(BodyPosition("left wrist", "wrist", 1))
    centaur.add_position(BodyPosition("right wrist", "wrist", 1))
    centaur.add_position(BodyPosition("hands", "hands", 4))
    centaur.add_position(BodyPosition("left finger", "finger", 1))
    centaur.add_position(BodyPosition("right finger", "finger", 1))
    centaur.add_position(BodyPosition("waist", "waist", 1))
    centaur.add_position(BodyPosition("horse body", "torso", 20))
    centaur.add_position(BodyPosition("left front leg", "leg", 6))
    centaur.add_position(BodyPosition("right front leg", "leg", 6))
    centaur.add_position(BodyPosition("left rear leg", "leg", 7))
    centaur.add_position(BodyPosition("right rear leg", "leg", 7))
    centaur.add_position(BodyPosition("legs", "legs", 13))
    centaur.add_position(BodyPosition("hooves", "hooves", 8))
    centaur.add_position(BodyPosition("left grip", "held", 0))
    centaur.add_position(BodyPosition("right grip", "held", 0))
    race_config.add_race(centaur)
    
    # Save the default race configuration
    save_race_config()
    mud.log_string("Created default race configuration with test races.")

def create_default_body_config():
    """Create default body configuration with custom types and sizes."""
    global body_config
    
    body_config = BodyConfig()
    
    # Add custom body types that are NOT in C file but used by our races
    body_config.body_types.add_bodypart_type("hands")
    body_config.body_types.add_bodypart_type("legs")
    body_config.body_types.add_bodypart_type("feet")
    body_config.body_types.add_bodypart_type("wings")
    body_config.body_types.add_bodypart_type("hooves")
    
    # Add custom body sizes that are NOT in C file but used by our races
    body_config.body_types.add_bodysize("gigantic")
    
    # Save the default body configuration
    save_body_config()
    mud.log_string("Created default body configuration with custom types and sizes.")

# Configuration file paths
RACE_CONFIG_FILE = "misc/entities-race-config"
BODY_CONFIG_FILE = "misc/entities-body-config"

def load_entity_configs():
    """Load entity configuration from separate storage files."""
    global race_config, body_config
    
    race_file = RACE_CONFIG_FILE
    body_file = BODY_CONFIG_FILE
    import os
    
    # Load race configuration
    if not os.path.exists(race_file):
        create_default_race_config()
    else:
        try:
            storage_set = storage.StorageSet(race_file)
            race_config = RaceConfig.from_storage(storage_set)
            storage_set.close()
            mud.log_string("Race configuration loaded successfully.")
        except Exception as e:
            mud.log_string(f"Error loading race config: {e}. Creating defaults.")
            create_default_race_config()
    
    # Load body configuration
    if not os.path.exists(body_file):
        create_default_body_config()
    else:
        try:
            storage_set = storage.StorageSet(body_file)
            body_config = BodyConfig.from_storage(storage_set)
            storage_set.close()
            mud.log_string("Body configuration loaded successfully.")
        except Exception as e:
            mud.log_string(f"Error loading body config: {e}. Creating defaults.")
            create_default_body_config()
    
    # Register configurations with the world system
    import world
    
    # Register custom body types and sizes FIRST before races
    # Note: With the new string-based body system, custom types are automatically
    # added when bodyAddPositionByName() is called, so we don't need to pre-register them
    added_positions = []
    for bodypart_type in body_config.body_types.bodypart_types:
        try:
            world.add_bodypos_type(bodypart_type)
            added_positions.append(bodypart_type)
        except ValueError:
            # Body position type already exists, skip it
            pass
    
    added_sizes = []
    for bodysize in body_config.body_types.bodysizes:
        try:
            world.add_bodysize(bodysize)
            added_sizes.append(bodysize)
        except ValueError:
            # Body size already exists, skip it
            pass
    
    # Log aggregate messages for added types and sizes
    if added_positions:
        mud.log_string(f"Added body position types: {', '.join(added_positions)}")
    if added_sizes:
        mud.log_string(f"Added body sizes: {', '.join(added_sizes)}")
    
    # Register races AFTER custom body types are registered
    for race in race_config.races.values():
        # Create body template
        body_template = []
        for pos in race.body_positions:
            body_template.append({
                'name': pos.name,
                'type': pos.pos_type,
                'weight': pos.weight
            })
        
        # Add race to world system
        try:
            world.add_race(race.name, race.abbrev, body_template, race.pc_ok)
            mud.log_string(f"Registered race: {race.name}")
        except ValueError as e:
            mud.log_string(f"Failed to register race {race.name}: {e}")
            raise

def get_race_config():
    """Get the global race configuration."""
    return race_config

def get_body_config():
    """Get the global entity configuration object."""
    return body_config

def get_entity_config():
    """Get both configurations for backwards compatibility."""
    class CombinedConfig:
        def __init__(self):
            self.races = race_config.races
            self.body_types = body_config.body_types
    return CombinedConfig()

def save_entity_configs():
    """Save both race and body configurations."""
    save_race_config()
    save_body_config()

def save_race_config():
    """Save race configuration to storage file."""
    global race_config
    
    config_file = RACE_CONFIG_FILE
    try:
        storage_set = storage.StorageSet()
        race_config.store(storage_set)
        storage_set.write(config_file)
        storage_set.close()
        mud.log_string("Race configuration saved successfully.")
    except Exception as e:
        mud.log_string(f"Error saving race configuration: {e}")

def save_body_config():
    """Save body configuration to storage file."""
    global body_config
    
    config_file = BODY_CONFIG_FILE
    try:
        storage_set = storage.StorageSet()
        body_config.store(storage_set)
        storage_set.write(config_file)
        storage_set.close()
        mud.log_string("Body configuration saved successfully.")
    except Exception as e:
        mud.log_string(f"Error saving body configuration: {e}")
