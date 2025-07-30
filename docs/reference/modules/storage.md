---
layout: default
title: storage Module
parent: Modules
grand_parent: API Reference
nav_order: 4
---

# storage Module

The `storage` module provides a key-value data persistence system that allows saving information to disk without directly interacting with files. It offers two main classes: `StorageSet` for key-value pairs and `StorageList` for collections of storage sets.

**Module Type**: Core EFuns (External Functions)  
**Import**: `import storage`

## Overview

The storage system is used throughout NakedMud for:
- Saving character and account data
- Persisting auxiliary data
- Storing world database information
- Maintaining configuration settings
- Preserving game state across restarts

The system provides automatic memory management and handles complex nested data structures.

## Classes

### StorageSet

A `StorageSet` stores key-value pairs and supports multiple data types including strings, integers, floating-point numbers, booleans, and nested storage structures.

#### Constructor

##### StorageSet(filename=None)

Creates a new storage set. If a filename is provided, loads the storage set from the specified file.

**Parameters**:
- `filename` (str, optional): File to load storage set from

**Example**:
```python
import storage

# Create a new empty storage set
set1 = storage.StorageSet()

# Load a storage set from file
set2 = storage.StorageSet("data/player_stats.dat")
```

#### Storage Methods

##### storeString(name, val)

**Returns**: `None`

Stores a string value in the storage set.

**Parameters**:
- `name` (str): The key name
- `val` (str): The string value to store

**Example**:
```python
import storage

set = storage.StorageSet()
set.storeString("player_name", "Gandalf")
set.storeString("description", "A wise wizard with a long grey beard.")
```

##### storeInt(name, val)

**Returns**: `None`

Stores an integer value in the storage set.

**Parameters**:
- `name` (str): The key name
- `val` (int): The integer value to store

**Example**:
```python
set.storeInt("level", 25)
set.storeInt("hit_points", 150)
set.storeInt("experience", 50000)
```

##### storeDouble(name, val)

**Returns**: `None`

Stores a floating-point value in the storage set.

**Parameters**:
- `name` (str): The key name
- `val` (float): The floating-point value to store

**Example**:
```python
set.storeDouble("weight", 75.5)
set.storeDouble("temperature", 98.6)
set.storeDouble("multiplier", 1.25)
```

##### storeBool(name, val)

**Returns**: `None`

Stores a boolean value in the storage set.

**Parameters**:
- `name` (str): The key name
- `val` (bool): The boolean value to store

**Example**:
```python
set.storeBool("is_admin", True)
set.storeBool("can_fly", False)
set.storeBool("invisible", True)
```

##### storeSet(name, val)

**Returns**: `None`

Stores a nested storage set within this storage set.

**Parameters**:
- `name` (str): The key name
- `val` (StorageSet): The storage set to store

**Example**:
```python
# Create nested storage for inventory
inventory_set = storage.StorageSet()
inventory_set.storeString("weapon", "magic sword")
inventory_set.storeInt("gold", 500)

# Store the nested set
character_set.storeSet("inventory", inventory_set)
```

##### storeList(name, val)

**Returns**: `None`

Stores a storage list within this storage set.

**Parameters**:
- `name` (str): The key name
- `val` (StorageList): The storage list to store

**Example**:
```python
# Create a list of spells
spell_list = storage.StorageList()

spell1 = storage.StorageSet()
spell1.storeString("name", "fireball")
spell1.storeInt("level", 3)
spell_list.add(spell1)

spell2 = storage.StorageSet()
spell2.storeString("name", "heal")
spell2.storeInt("level", 2)
spell_list.add(spell2)

# Store the list
character_set.storeList("spells", spell_list)
```

#### Retrieval Methods

##### readString(name)

**Returns**: `str`

Reads a string value from the storage set. Returns an empty string if the key doesn't exist.

**Parameters**:
- `name` (str): The key name to read

**Example**:
```python
player_name = set.readString("player_name")
description = set.readString("description")
```

##### readInt(name)

**Returns**: `int`

Reads an integer value from the storage set. Returns 0 if the key doesn't exist.

**Parameters**:
- `name` (str): The key name to read

**Example**:
```python
level = set.readInt("level")
hit_points = set.readInt("hit_points")
```

##### readDouble(name)

**Returns**: `float`

Reads a floating-point value from the storage set. Returns 0.0 if the key doesn't exist.

**Parameters**:
- `name` (str): The key name to read

**Example**:
```python
weight = set.readDouble("weight")
multiplier = set.readDouble("multiplier")
```

##### readBool(name)

**Returns**: `bool`

Reads a boolean value from the storage set. Returns False if the key doesn't exist.

**Parameters**:
- `name` (str): The key name to read

**Example**:
```python
is_admin = set.readBool("is_admin")
can_fly = set.readBool("can_fly")
```

##### readSet(name)

**Returns**: `StorageSet`

Reads a nested storage set. Returns an empty storage set if the key doesn't exist.

**Parameters**:
- `name` (str): The key name to read

**Example**:
```python
inventory = set.readSet("inventory")
weapon = inventory.readString("weapon")
gold = inventory.readInt("gold")
```

##### readList(name)

**Returns**: `StorageList`

Reads a storage list. Returns an empty storage list if the key doesn't exist.

**Parameters**:
- `name` (str): The key name to read

**Example**:
```python
spells = set.readList("spells")
for spell_set in spells.sets():
    spell_name = spell_set.readString("name")
    spell_level = spell_set.readInt("level")
    print(f"Spell: {spell_name} (Level {spell_level})")
```

#### Utility Methods

##### contains(name)

**Returns**: `bool`

Returns True if the storage set contains an entry with the given name.

**Parameters**:
- `name` (str): The key name to check

**Example**:
```python
if set.contains("player_name"):
    name = set.readString("player_name")
else:
    name = "Unknown"
```

##### \_\_contains\_\_(name)

**Returns**: `bool`

Python magic method that allows using the `in` operator.

**Parameters**:
- `name` (str): The key name to check

**Example**:
```python
if "player_name" in set:
    name = set.readString("player_name")
```

##### write(filename)

**Returns**: `None`

Writes the storage set contents to the specified file.

**Parameters**:
- `filename` (str): The file path to write to

**Example**:
```python
set.write("data/player_data.dat")
```

##### close()

**Returns**: `None`

**CRITICAL**: Recursively closes the storage set and all nested sets and lists. This MUST be called when finished using the storage set, as garbage collection will not automatically delete it.

**Example**:
```python
set = storage.StorageSet()
# ... use the storage set ...
set.close()  # Always call this when done!
```

### StorageList

A `StorageList` holds multiple storage sets in an ordered collection.

#### Constructor

##### StorageList(list=None)

Creates a new storage list. A Python list of storage sets may be supplied to initialize the list.

**Parameters**:
- `list` (list, optional): Python list of StorageSet objects

**Example**:
```python
import storage

# Create empty storage list
list1 = storage.StorageList()

# Create from existing storage sets
existing_sets = [set1, set2, set3]
list2 = storage.StorageList(existing_sets)
```

#### Methods

##### add(storage_set)

**Returns**: `None`

Appends a storage set to the storage list.

**Parameters**:
- `storage_set` (StorageSet): The storage set to add

**Example**:
```python
list = storage.StorageList()

# Add storage sets to the list
item1 = storage.StorageSet()
item1.storeString("name", "sword")
item1.storeInt("damage", 10)
list.add(item1)

item2 = storage.StorageSet()
item2.storeString("name", "shield")
item2.storeInt("defense", 5)
list.add(item2)
```

##### sets()

**Returns**: `list`

Returns a Python list of all storage sets in the storage list.

**Example**:
```python
for item_set in list.sets():
    item_name = item_set.readString("name")
    print(f"Item: {item_name}")
```

## Usage Patterns

### Basic Data Storage

```python
import storage

# Create and populate a storage set
player_data = storage.StorageSet()
player_data.storeString("name", "Aragorn")
player_data.storeInt("level", 20)
player_data.storeInt("hit_points", 180)
player_data.storeBool("is_king", True)

# Save to file
player_data.write("data/aragorn.dat")

# Clean up
player_data.close()
```

### Loading and Reading Data

```python
import storage

# Load from file
player_data = storage.StorageSet("data/aragorn.dat")

# Read data with defaults
name = player_data.readString("name")  # Returns "" if not found
level = player_data.readInt("level")   # Returns 0 if not found
is_king = player_data.readBool("is_king")  # Returns False if not found

# Check if key exists before reading
if player_data.contains("special_ability"):
    ability = player_data.readString("special_ability")

# Clean up
player_data.close()
```

### Complex Nested Structures

```python
import storage

# Create character data with nested structures
character = storage.StorageSet()
character.storeString("name", "Legolas")
character.storeInt("level", 18)

# Create stats sub-structure
stats = storage.StorageSet()
stats.storeInt("strength", 16)
stats.storeInt("dexterity", 20)
stats.storeInt("constitution", 14)
character.storeSet("stats", stats)

# Create inventory list
inventory = storage.StorageList()

# Add bow to inventory
bow = storage.StorageSet()
bow.storeString("name", "Elven Bow")
bow.storeString("type", "weapon")
bow.storeInt("damage", 15)
inventory.add(bow)

# Add arrows to inventory
arrows = storage.StorageSet()
arrows.storeString("name", "Elven Arrows")
arrows.storeString("type", "ammunition")
arrows.storeInt("quantity", 50)
inventory.add(arrows)

character.storeList("inventory", inventory)

# Save the complete structure
character.write("data/legolas.dat")

# Clean up (this will recursively close nested structures)
character.close()
```

### Reading Complex Structures

```python
import storage

# Load complex character data
character = storage.StorageSet("data/legolas.dat")

# Read basic info
name = character.readString("name")
level = character.readInt("level")

# Read nested stats
stats = character.readSet("stats")
strength = stats.readInt("strength")
dexterity = stats.readInt("dexterity")

# Read inventory list
inventory = character.readList("inventory")
print(f"{name}'s inventory:")
for item_set in inventory.sets():
    item_name = item_set.readString("name")
    item_type = item_set.readString("type")
    print(f"  {item_name} ({item_type})")

# Clean up
character.close()
```

### Auxiliary Data Integration

Storage sets are commonly used with auxiliary data:

```python
import storage
import auxiliary

class PlayerStats:
    def __init__(self, storage_set=None):
        if storage_set:
            # Load from storage
            self.strength = storage_set.readInt("strength")
            self.intelligence = storage_set.readInt("intelligence")
            self.dexterity = storage_set.readInt("dexterity")
            
            # Load nested skill data
            skills_set = storage_set.readSet("skills")
            self.sword_skill = skills_set.readInt("sword")
            self.magic_skill = skills_set.readInt("magic")
        else:
            # Default values
            self.strength = 10
            self.intelligence = 10
            self.dexterity = 10
            self.sword_skill = 1
            self.magic_skill = 1
    
    def store(self):
        # Create storage representation
        set = storage.StorageSet()
        set.storeInt("strength", self.strength)
        set.storeInt("intelligence", self.intelligence)
        set.storeInt("dexterity", self.dexterity)
        
        # Store nested skill data
        skills_set = storage.StorageSet()
        skills_set.storeInt("sword", self.sword_skill)
        skills_set.storeInt("magic", self.magic_skill)
        set.storeSet("skills", skills_set)
        
        return set
    
    def copy(self):
        new_stats = PlayerStats()
        new_stats.strength = self.strength
        new_stats.intelligence = self.intelligence
        new_stats.dexterity = self.dexterity
        new_stats.sword_skill = self.sword_skill
        new_stats.magic_skill = self.magic_skill
        return new_stats
    
    def copyTo(self, to):
        to.strength = self.strength
        to.intelligence = self.intelligence
        to.dexterity = self.dexterity
        to.sword_skill = self.sword_skill
        to.magic_skill = self.magic_skill

auxiliary.install("player_stats", PlayerStats, "character")
```

## Best Practices

### Memory Management

Always call `close()` on storage sets when finished:

```python
import storage

def safe_storage_operation():
    set = storage.StorageSet()
    try:
        # Use the storage set
        set.storeString("data", "value")
        set.write("file.dat")
    finally:
        # Always clean up
        set.close()
```

### Error Handling

Handle file operations safely:

```python
import storage

def load_player_data(filename):
    try:
        player_data = storage.StorageSet(filename)
        return player_data
    except:
        # Return default data if file doesn't exist or is corrupted
        default_data = storage.StorageSet()
        default_data.storeString("name", "Unknown")
        default_data.storeInt("level", 1)
        return default_data
```

### Default Values

Use the built-in default return values:

```python
# These methods return safe defaults if keys don't exist
name = set.readString("name")        # Returns ""
level = set.readInt("level")         # Returns 0
weight = set.readDouble("weight")    # Returns 0.0
is_admin = set.readBool("is_admin")  # Returns False

# Or check explicitly
if set.contains("optional_data"):
    data = set.readString("optional_data")
else:
    data = "default_value"
```

### Nested Structure Organization

Organize complex data logically:

```python
# Good: Logical grouping
character.storeSet("stats", stats_set)
character.storeSet("inventory", inventory_set)
character.storeSet("skills", skills_set)

# Avoid: Flat structure for complex data
# character.storeInt("stat_strength", 16)  # Less organized
# character.storeInt("stat_dexterity", 20)
```

## Common Patterns

### Configuration Files

```python
import storage

def save_config(config_dict):
    config_set = storage.StorageSet()
    for key, value in config_dict.items():
        if isinstance(value, str):
            config_set.storeString(key, value)
        elif isinstance(value, int):
            config_set.storeInt(key, value)
        elif isinstance(value, bool):
            config_set.storeBool(key, value)
    
    config_set.write("config/settings.dat")
    config_set.close()

def load_config():
    try:
        config_set = storage.StorageSet("config/settings.dat")
        config = {}
        # Read known configuration keys
        config['server_name'] = config_set.readString("server_name")
        config['max_players'] = config_set.readInt("max_players")
        config['allow_newbies'] = config_set.readBool("allow_newbies")
        config_set.close()
        return config
    except:
        return get_default_config()
```

### Data Migration

```python
import storage

def migrate_old_format(old_filename, new_filename):
    # Load old format
    old_data = storage.StorageSet(old_filename)
    
    # Create new format
    new_data = storage.StorageSet()
    
    # Migrate data with transformations
    new_data.storeString("name", old_data.readString("player_name"))
    new_data.storeInt("level", old_data.readInt("char_level"))
    
    # Add new fields with defaults
    new_data.storeInt("version", 2)
    new_data.storeBool("migrated", True)
    
    # Save new format
    new_data.write(new_filename)
    
    # Clean up
    old_data.close()
    new_data.close()
```

## See Also

- [auxiliary Module](auxiliary.md) - Auxiliary data system that uses storage
- [mudsys Module](mudsys.md) - Core system functions
- [Core Concepts: Data Persistence](../../core-concepts/data-persistence.md)
- [Tutorials: Using Storage](../../tutorials/storage-tutorial.md)