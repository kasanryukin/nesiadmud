---
layout: default
title: auxiliary Module
parent: Modules
grand_parent: API Reference
nav_order: 2
---

# auxiliary Module

The `auxiliary` module provides the framework for installing and managing auxiliary data on game objects. Auxiliary data allows you to extend characters, objects, rooms, accounts, and sockets with custom data structures without modifying the core C code.

**Module Type**: Core EFuns (External Functions)  
**Import**: `import auxiliary`

## Overview

Auxiliary data is a powerful system that allows developers to attach custom data structures to core game objects. This system is used extensively throughout NakedMud for features like:

- Editor data for online creation tools
- Trigger and script data
- Custom character attributes
- Room-specific behaviors
- Socket state information

## Core Function

### install(name, AuxClass, installs_on)

**Returns**: `None`

Registers new auxiliary data with the specified name that can be installed on the given object types.

**Parameters**:
- `name` (str): The unique name for this auxiliary data type
- `AuxClass` (class): The auxiliary data class (see requirements below)
- `installs_on` (str): Comma-separated list of object types: "character", "object", "room", "account", "socket"

**Example**:
```python
import auxiliary

class PlayerStats:
    def __init__(self, storage_set=None):
        if storage_set:
            self.strength = storage_set.readInt("strength")
            self.intelligence = storage_set.readInt("intelligence")
            self.dexterity = storage_set.readInt("dexterity")
        else:
            self.strength = 10
            self.intelligence = 10
            self.dexterity = 10
    
    def copy(self):
        new_stats = PlayerStats()
        new_stats.strength = self.strength
        new_stats.intelligence = self.intelligence
        new_stats.dexterity = self.dexterity
        return new_stats
    
    def copyTo(self, to):
        to.strength = self.strength
        to.intelligence = self.intelligence
        to.dexterity = self.dexterity
    
    def store(self):
        import storage
        set = storage.StorageSet()
        set.storeInt("strength", self.strength)
        set.storeInt("intelligence", self.intelligence)
        set.storeInt("dexterity", self.dexterity)
        return set

# Install the auxiliary data on characters
auxiliary.install("player_stats", PlayerStats, "character")
```

## Auxiliary Data Class Requirements

All auxiliary data classes must implement the following methods:

### \_\_init\_\_(self, storage_set=None)

The constructor must be able to handle two scenarios:
1. **Fresh Creation**: When `storage_set` is `None`, create a new instance with default values
2. **Loading from Storage**: When `storage_set` is provided, read data from the storage set

**Parameters**:
- `storage_set` (StorageSet or None): Storage set to load data from, or None for fresh creation

### copy(self)

**Returns**: New instance of the auxiliary data class

Creates and returns a complete copy of the auxiliary data instance.

### copyTo(self, to)

**Returns**: `None`

Copies all data from this instance to another instance of the same class.

**Parameters**:
- `to` (AuxClass): The target instance to copy data to

### store(self)

**Returns**: `StorageSet`

Returns a storage set representation of the auxiliary data. If the data is not persistent, an empty storage set can be returned.

## Usage Patterns

### Accessing Auxiliary Data

Once auxiliary data is installed, it can be accessed on the appropriate objects using the auxiliary data name:

```python
import char
import auxiliary

# Assuming PlayerStats is installed as "player_stats"
character = char.Char()

# Access the auxiliary data
stats = character.aux("player_stats")
if stats:
    print(f"Strength: {stats.strength}")
    stats.strength += 1
```

### Persistent vs Non-Persistent Data

Auxiliary data can be either persistent (saved to disk) or temporary:

**Persistent Data Example**:
```python
class PersistentData:
    def __init__(self, storage_set=None):
        if storage_set:
            self.value = storage_set.readString("value")
        else:
            self.value = "default"
    
    def store(self):
        import storage
        set = storage.StorageSet()
        set.storeString("value", self.value)
        return set  # Returns data to be saved
```

**Non-Persistent Data Example**:
```python
class TemporaryData:
    def __init__(self, storage_set=None):
        self.temp_value = 0  # Always starts fresh
    
    def store(self):
        import storage
        return storage.StorageSet()  # Returns empty set - not saved
```

### Complex Data Structures

Auxiliary data can contain complex nested structures:

```python
import auxiliary
import storage

class ComplexData:
    def __init__(self, storage_set=None):
        if storage_set:
            self.simple_value = storage_set.readString("simple")
            self.number_list = []
            list_data = storage_set.readList("numbers")
            for set in list_data.sets():
                self.number_list.append(set.readInt("value"))
            
            self.nested_data = storage_set.readSet("nested")
        else:
            self.simple_value = ""
            self.number_list = []
            self.nested_data = storage.StorageSet()
    
    def copy(self):
        new_data = ComplexData()
        new_data.simple_value = self.simple_value
        new_data.number_list = self.number_list[:]  # Copy list
        # Note: nested_data copying would need custom logic
        return new_data
    
    def copyTo(self, to):
        to.simple_value = self.simple_value
        to.number_list = self.number_list[:]
        # Copy nested data as needed
    
    def store(self):
        set = storage.StorageSet()
        set.storeString("simple", self.simple_value)
        
        # Store list of numbers
        number_list = storage.StorageList()
        for num in self.number_list:
            num_set = storage.StorageSet()
            num_set.storeInt("value", num)
            number_list.add(num_set)
        set.storeList("numbers", number_list)
        
        # Store nested data
        set.storeSet("nested", self.nested_data)
        return set

auxiliary.install("complex_data", ComplexData, "character,room")
```

## Installation Targets

Auxiliary data can be installed on the following object types:

### character
- Installed on player characters and NPCs
- Accessed via `character.aux("aux_name")`
- Commonly used for: stats, skills, quest data, preferences

### object
- Installed on game objects/items
- Accessed via `object.aux("aux_name")`
- Commonly used for: special item properties, enchantments, custom behaviors

### room
- Installed on rooms/locations
- Accessed via `room.aux("aux_name")`
- Commonly used for: special room behaviors, environmental data, triggers

### account
- Installed on player accounts
- Accessed via `account.aux("aux_name")`
- Commonly used for: account preferences, global player data, login information

### socket
- Installed on network connections
- Accessed via `socket.aux("aux_name")`
- Commonly used for: connection state, editor data, temporary session information

## Best Practices

### Naming Conventions
- Use descriptive names that won't conflict with other modules
- Consider prefixing with your module name: `"mymodule_stats"`
- Use lowercase with underscores: `"player_statistics"`

### Memory Management
- Keep auxiliary data lightweight when possible
- Use lazy loading for expensive computations
- Clean up references in the `copyTo` method

### Error Handling
```python
class SafeAuxData:
    def __init__(self, storage_set=None):
        try:
            if storage_set:
                self.value = storage_set.readString("value")
            else:
                self.value = "default"
        except:
            self.value = "default"  # Fallback on error
    
    def store(self):
        try:
            import storage
            set = storage.StorageSet()
            set.storeString("value", self.value)
            return set
        except:
            import storage
            return storage.StorageSet()  # Return empty set on error
```

### Multiple Installation Targets
```python
# Install on multiple object types
auxiliary.install("universal_data", MyAuxClass, "character,object,room")

# Different classes for different targets
auxiliary.install("char_data", CharSpecificClass, "character")
auxiliary.install("room_data", RoomSpecificClass, "room")
```

## Common Use Cases

### Character Statistics System
```python
class CharacterStats:
    def __init__(self, storage_set=None):
        if storage_set:
            self.level = storage_set.readInt("level")
            self.experience = storage_set.readInt("experience")
            self.hit_points = storage_set.readInt("hit_points")
            self.max_hit_points = storage_set.readInt("max_hit_points")
        else:
            self.level = 1
            self.experience = 0
            self.hit_points = 100
            self.max_hit_points = 100
    
    def gain_experience(self, amount):
        self.experience += amount
        if self.experience >= self.level * 1000:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.max_hit_points += 20
        self.hit_points = self.max_hit_points
        self.experience = 0

auxiliary.install("char_stats", CharacterStats, "character")
```

### Room Trigger System
```python
class RoomTriggers:
    def __init__(self, storage_set=None):
        if storage_set:
            self.enter_message = storage_set.readString("enter_message")
            self.exit_message = storage_set.readString("exit_message")
            self.special_action = storage_set.readString("special_action")
        else:
            self.enter_message = ""
            self.exit_message = ""
            self.special_action = ""
    
    def on_enter(self, character):
        if self.enter_message:
            character.send(self.enter_message)
        if self.special_action == "heal":
            character.hit_points = character.max_hit_points

auxiliary.install("room_triggers", RoomTriggers, "room")
```

## See Also

- [storage Module](storage.md) - Storage system for persistent data
- [Core Concepts: Auxiliary Data](../../core-concepts/auxiliary-data.md) - Detailed auxiliary data concepts
- [mudsys Module](mudsys.md) - Core system functions
- [Tutorials: Using Auxiliary Data](../../tutorials/auxiliary-data-tutorial.md)