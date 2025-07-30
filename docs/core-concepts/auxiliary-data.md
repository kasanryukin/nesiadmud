---
title: Auxiliary Data System
layout: default
nav_order: 1
parent: Core Concepts
description: "Understanding NakedMud's extensible data attachment system"
---

# Auxiliary Data System

The auxiliary data system is NakedMud's solution for extending core game objects (characters, rooms, objects, accounts, sockets, and zones) with additional data without modifying the core C code. This system allows modules to attach custom data to any game object in a clean, modular way.

## Overview

When developing MUD modules, you often need to store additional information with game objects. Rather than modifying the core data structures directly, NakedMud provides an auxiliary data system that allows you to:

- Attach custom data to characters, rooms, objects, accounts, sockets, and zones
- Automatically handle data persistence (saving/loading)
- Manage data lifecycle (creation, copying, deletion)
- Keep modules completely separate from core code

## The Problem Auxiliary Data Solves

Traditional MUD development often requires modifying core data structures to add new features. For example, if you want to add a "hunger" system to characters, you might be tempted to add a `hunger_level` field directly to the character structure. This approach has several problems:

1. **Core Modification**: You must modify the core MUD code, making upgrades difficult
2. **Coupling**: Your module becomes tightly coupled to specific core versions
3. **Conflicts**: Multiple modules adding fields can cause naming conflicts
4. **Maintenance**: Changes to core structures require updating all dependent modules

The auxiliary data system solves these problems by providing a clean, modular way to extend game objects without touching core code.

## How Auxiliary Data Works Internally

The auxiliary data system operates through a sophisticated registration and management mechanism:

### Registration Process

When you install auxiliary data, several things happen:

1. **Function Registration**: Your data class methods are registered with the auxiliary system
2. **Type Association**: The data is associated with specific object types (character, room, etc.)
3. **Lifecycle Hooks**: The system sets up automatic creation, copying, and deletion
4. **Persistence Integration**: Storage and loading functions are integrated with the save system

### Data Storage

Each game object maintains a hash table of auxiliary data:

```c
// In the C code, each character has:
AUX_TABLE *auxiliary_data;  // Hash table of auxiliary data

// When you call ch.getAuxiliary("my_data"), it:
// 1. Looks up "my_data" in the character's auxiliary table
// 2. Returns the Python wrapper for that data
// 3. Creates new data if it doesn't exist
```

### Automatic Management

The auxiliary system automatically handles:

- **Creation**: New auxiliary data is created when objects are created
- **Copying**: Data is properly copied when objects are duplicated
- **Persistence**: Data is saved and loaded with the parent object
- **Cleanup**: Memory is freed when objects are destroyed

## Understanding Data Lifecycle

Auxiliary data follows a predictable lifecycle that mirrors its parent object:

### 1. Installation Phase
```python
# During module initialization
auxiliary.install("quest_data", QuestAuxData, "character")
```

This registers your data class with the auxiliary system. From this point forward, all characters will have quest data available.

### 2. Creation Phase
```python
# Character creation happens through the account system:
# 1. Player connects and logs into account (account_handler.py)
# 2. Player chooses to create new character
# 3. Character generation process begins (char_gen.py)
# 4. mudsys.create_player(name) is called
# 5. C code creates the character structure
# 6. Auxiliary system automatically creates all registered auxiliary data
#    instances for characters and attaches them to the new character

# Example from char_gen.py:
ch = mudsys.create_player(name)  # Creates character with all auxiliary data
```

### 3. Access Phase
```python
# During gameplay
aux = ch.getAuxiliary("quest_data")  # Returns existing instance
aux.current_quest = "find_the_sword"  # Modify data
```

### 4. Persistence Phase
```python
# When character is saved
# Auxiliary system automatically calls aux.store()
# Data is serialized and saved with character
```

### 5. Loading Phase
```python
# When character is loaded
# Auxiliary system calls QuestAuxData.__init__(storage_set)
# Data is restored from saved state
```

### 6. Cleanup Phase
```python
# When character is destroyed
# Auxiliary system automatically cleans up all auxiliary data
# Memory is properly freed
```

## How Auxiliary Data Works

The auxiliary data system uses a hash table-based approach where each game object maintains a table of auxiliary data keyed by name. When you install auxiliary data, you provide:

1. **A unique name** - Used as the key to access the data
2. **A data class** - Defines the structure and behavior of your data
3. **Target types** - Which object types (character, room, etc.) can use this data

## Core Concepts

### Data Types

Auxiliary data can be attached to these object types:

- **AUXILIARY_TYPE_CHAR** - Character data (players and NPCs)
- **AUXILIARY_TYPE_ROOM** - Room/location data
- **AUXILIARY_TYPE_OBJ** - Object/item data
- **AUXILIARY_TYPE_ACCOUNT** - Player account data
- **AUXILIARY_TYPE_SOCKET** - Connection/socket data
- **AUXILIARY_TYPE_ZONE** - Zone/area data

### Required Methods

Every auxiliary data class must implement these methods:

- **`__init__(self, storage_set=None)`** - Constructor that can create new data or load from storage
- **`copy(self)`** - Returns a complete copy of the data
- **`copyTo(self, to)`** - Copies data to another instance
- **`store(self)`** - Returns a storage set for persistence (or empty set if not persistent)

## Creating Auxiliary Data

### Step 1: Define Your Data Class

```python
import auxiliary, storage

class MyAuxData:
    def __init__(self, set=None):
        # Initialize your data
        self.my_value = 0
        self.my_list = []
        
        # If loading from storage, parse the data here
        if set:
            self.my_value = storage.read_int(set, "my_value")
            # ... load other data
    
    def copy(self):
        """Create a complete copy of this data"""
        newdata = MyAuxData()
        self.copyTo(newdata)
        return newdata
    
    def copyTo(self, to):
        """Copy this data to another instance"""
        to.my_value = self.my_value
        to.my_list = [x for x in self.my_list]  # Deep copy lists
    
    def store(self):
        """Save data to a storage set"""
        set = storage.StorageSet()
        storage.store_int(set, "my_value", self.my_value)
        # ... store other data
        return set
```

### Step 2: Install the Auxiliary Data

```python
# Install the auxiliary data for characters
auxiliary.install("my_data", MyAuxData, "character")

# Install for multiple types
auxiliary.install("shared_data", MyAuxData, "character room object")
```

### Step 3: Access the Data

```python
def some_function(ch):
    # Get the auxiliary data
    aux = ch.getAuxiliary("my_data")
    
    # Use the data
    aux.my_value += 1
    aux.my_list.append("new item")
    
    # The data is automatically saved when the character is saved
```

## Complete Example: Routine System

Here's a real example from NakedMud's routine system that allows NPCs to follow scripted behaviors:

```python
import auxiliary, storage, event

class RoutineAuxData:
    """Holds character data related to character routines."""
    
    def __init__(self, set=None):
        self.routine = None   # the routine steps to follow
        self.repeat = False   # repeat after finishing?
        self.step = None      # current step number
        self.checks = None    # pre-step validation checks
    
    def copyTo(self, to):
        # Deep copy lists to avoid reference sharing
        if isinstance(self.routine, list):
            to.routine = [x for x in self.routine]
        else:
            to.routine = None
            
        if isinstance(self.checks, list):
            to.checks = [x for x in self.checks]
        else:
            to.checks = None
            
        to.repeat = self.repeat
        to.step = self.step
    
    def copy(self):
        newdata = RoutineAuxData()
        self.copyTo(newdata)
        return newdata
    
    def store(self):
        # This routine data is not persistent
        return storage.StorageSet()

# Install the auxiliary data
auxiliary.install("routine_data", RoutineAuxData, "character")

# Usage example
def set_routine(ch, routine, repeat=False):
    """Set a routine for a character to follow"""
    aux = ch.getAuxiliary("routine_data")
    aux.routine = [x for x in routine] if routine else None
    aux.repeat = repeat
    aux.step = 0 if routine else None
    
    if routine:
        start_routine_event(ch)

def get_routine_step(ch):
    """Get the current routine step for a character"""
    aux = ch.getAuxiliary("routine_data")
    if aux.routine and aux.step is not None:
        return aux.routine[aux.step]
    return None
```

## Common Patterns

### Non-Persistent Data

For temporary data that doesn't need to be saved:

```python
def store(self):
    return storage.StorageSet()  # Empty set = not saved
```

### Persistent Data

For data that should be saved with the object:

```python
def store(self):
    set = storage.StorageSet()
    storage.store_string(set, "name", self.name)
    storage.store_int(set, "value", self.value)
    storage.store_list(set, "items", self.items)
    return set

def __init__(self, set=None):
    if set:
        self.name = storage.read_string(set, "name")
        self.value = storage.read_int(set, "value") 
        self.items = storage.read_list(set, "items")
    else:
        # Default values for new instances
        self.name = ""
        self.value = 0
        self.items = []
```

### Complex Data Structures

For nested or complex data:

```python
class ComplexAuxData:
    def __init__(self, set=None):
        self.nested_dict = {}
        self.object_list = []
        
        if set:
            # Load complex data from storage
            nested_set = storage.read_set(set, "nested_dict")
            # ... parse nested data
    
    def copyTo(self, to):
        # Deep copy complex structures
        import copy
        to.nested_dict = copy.deepcopy(self.nested_dict)
        to.object_list = copy.deepcopy(self.object_list)
```

## Best Practices

### Naming Conventions

- Use descriptive names: `"quest_data"` not `"qd"`
- Include your module name: `"mymodule_player_data"`
- Be consistent across your module

### Data Management

- Always implement deep copying for mutable data (lists, dicts)
- Initialize all attributes in `__init__`
- Handle None values gracefully
- Keep data structures simple when possible

### Performance Considerations

- Auxiliary data is loaded when objects are loaded
- Large data structures impact memory usage
- Consider lazy loading for expensive data
- Use non-persistent storage for temporary data

### Error Handling

```python
def safe_get_aux_data(obj, aux_name, default_value=None):
    """Safely get auxiliary data with fallback"""
    try:
        aux = obj.getAuxiliary(aux_name)
        return aux if aux else default_value
    except:
        return default_value
```

## Integration with Core Objects

Auxiliary data is automatically integrated into all core objects:

- **Characters**: `ch.getAuxiliary("name")`
- **Rooms**: `room.getAuxiliary("name")`
- **Objects**: `obj.getAuxiliary("name")`
- **Accounts**: `account.getAuxiliary("name")`
- **Sockets**: `sock.getAuxiliary("name")`

The data is automatically:
- Created when objects are created
- Saved when objects are saved
- Loaded when objects are loaded
- Copied when objects are copied
- Deleted when objects are deleted

## Troubleshooting

### Common Issues

**Data not persisting**: Check that your `store()` method returns a proper storage set with data.

**Copy errors**: Ensure `copyTo()` performs deep copies of mutable objects.

**Installation errors**: Verify the auxiliary data name is unique and the target type is valid.

**Access errors**: Make sure the auxiliary data is installed before trying to access it.

### Debugging Tips

```python
# Check if auxiliary data exists
aux = ch.getAuxiliary("my_data")
if aux is None:
    print("Auxiliary data 'my_data' not found!")

# List all auxiliary data on an object
# (This would require additional debugging functions)
```

## See Also

- [Storage System](../reference/modules/storage.md) - For data persistence
- [Python Integration](python-integration.md) - How Python and C interact
- [Module Development](../tutorials/creating-modules.md) - Building complete modules