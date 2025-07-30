---
layout: default
title: EFuns (External Functions)
parent: API Reference
nav_order: 2
---

# EFuns (External Functions)

EFuns (External Functions) are C-derived Python functions that provide the core functionality of the NakedMud system. These functions are implemented in C and exposed to Python through the 13 core modules, giving Python scripts access to the underlying MUD engine.

## Overview

EFuns represent the primary interface between Python scripts and the C-based MUD engine. They handle:
- Core system operations
- Game object manipulation
- World database management
- Network communication
- Event scheduling
- Data persistence

## Module Classification

### Core System Modules

#### mudsys Module
**Purpose**: Central hub for system-level operations  
**Key Functions**:
- Account and character management (`create_account`, `load_account`, `get_player`)
- Command system (`add_cmd`, `add_cmd_check`, `remove_cmd`)
- Socket management (`attach_char_socket`, `detach_char_socket`)
- World database operations (`world_add_type`, `world_get_type`)
- Method extension system (`add_char_method`, `add_room_method`)
- System configuration (`sys_getval`, `sys_setval`)

#### auxiliary Module
**Purpose**: Auxiliary data management system  
**Key Functions**:
- `install(name, AuxClass, installs_on)` - Register auxiliary data types

#### event Module
**Purpose**: Delayed and timed function calls  
**Key Functions**:
- `start_event(owner, delay, event_func, data, arg)` - Schedule delayed events
- `interrupt_events_involving(thing)` - Cancel events for specific objects

#### storage Module
**Purpose**: Data persistence and serialization  
**Key Functions**:
- Storage set creation and manipulation
- Data serialization for saving/loading
- Type-safe data storage operations

### Object Management Modules

#### char Module
**Purpose**: Character manipulation and management  
**Key Functions**:
- `char_list()` - Get all characters in game
- `load_mob(proto, room, pos)` - Create NPCs from prototypes
- `count_mobs(keyword, loc)` - Count character instances
- `is_abstract(proto)` - Check if prototype is abstract
- `read(storage_set)` - Load character from storage

#### room Module
**Purpose**: Room and world location management  
**Key Functions**:
- `get_room(key)` - Load room by key
- `instance(room_proto, as_key)` - Create room instances
- `is_loaded(key)` - Check if room exists
- `is_abstract(proto)` - Check if room prototype is abstract

#### obj Module
**Purpose**: Game object and item management  
**Key Functions**:
- `load_obj(prototype, where, equip_to)` - Create objects from prototypes
- `obj_list()` - Get all objects in game
- `count_objs(keyword, loc)` - Count object instances
- `read(storage_set)` - Load object from storage

#### exit Module
**Purpose**: Exit and movement system  
**Key Functions**:
- Exit creation and manipulation
- Direction and movement handling
- Portal and transportation systems

### Network and Communication Modules

#### mudsock Module
**Purpose**: Network socket management  
**Key Functions**:
- Socket creation and management
- Connection handling
- Input/output processing
- Protocol management

#### account Module
**Purpose**: Player account management  
**Key Functions**:
- Account creation and authentication
- Player data management
- Login/logout processing
- Account-level permissions

### System Integration Modules

#### mud Module
**Purpose**: General MUD utility functions  
**Key Functions**:
- Argument parsing (`parse_args`)
- String manipulation utilities
- Game time and calendar functions
- General utility operations

#### hooks Module
**Purpose**: Event-driven programming system  
**Key Functions**:
- `add(type, function)` - Register event hooks
- `remove(type, function)` - Unregister hooks
- `run(hooktypes)` - Execute hooks
- `parse_info(info)` - Parse hook information
- `build_info(format, args)` - Create hook information

#### olc Module
**Purpose**: Online creation tools  
**Key Functions**:
- Editor system functions
- Content creation utilities
- OLC command support
- Template and prototype management

## Function Categories

### Creation and Loading Functions
Functions that create or load game objects:
```python
# Character creation
character = char.load_mob("guard", room)
player = mudsys.create_player("newbie")

# Object creation  
sword = obj.load_obj("longsword", character)
room = room.instance("tavern_template")

# Account creation
account = mudsys.create_account("player1")
```

### Management and Manipulation Functions
Functions that modify or manage existing objects:
```python
# Character management
mudsys.do_save(character)
mudsys.attach_char_socket(character, socket)

# Object manipulation
obj.fromall()  # Remove from current location
character.equip(sword)

# Room management
room.reset()
room.dig("north", destination)
```

### Query and Search Functions
Functions that retrieve information:
```python
# List functions
all_chars = char.char_list()
all_objects = obj.obj_list()

# Search functions
target = char.find_char(looker, char_list, 1, "guard")
item = obj.find_obj(looker, obj_list, 1, "sword")

# Count functions
guard_count = char.count_mobs("guard", room)
sword_count = obj.count_objs("sword")
```

### System Configuration Functions
Functions that manage system settings:
```python
# System variables
value = mudsys.sys_getval("setting_name")
mudsys.sys_setval("setting_name", "value")

# Command system
mudsys.add_cmd("mycommand", "mc", cmd_function, "player", True)
mudsys.add_cmd_check("mycommand", check_function)

# Method extension
mudsys.add_char_method("new_method", method_function)
```

### Event and Timing Functions
Functions that handle delayed actions:
```python
# Event scheduling
event.start_event(character, 10.0, heal_function, heal_amount, "heal")

# Event management
event.interrupt_events_involving(character)
```

### Data Persistence Functions
Functions that handle saving and loading:
```python
# Storage operations
storage_set = character.store()
new_character = char.read(storage_set)

# Auxiliary data
auxiliary.install("player_stats", StatsClass, "character")
stats = character.aux("player_stats")
```

## Usage Patterns

### Object Lifecycle Management
```python
import char, obj, room, mudsys

# Create and set up an NPC
tavern = room.get_room("tavern")
bartender = char.load_mob("bartender", tavern)
bartender.name = "Gruff the Bartender"

# Equip the NPC
apron = obj.load_obj("leather_apron", bartender)
bartender.equip(apron)

# Save the character
mudsys.do_save(bartender)
```

### Command System Integration
```python
import mudsys

def my_command(ch, cmd, arg):
    ch.send(f"You executed {cmd} with argument: {arg}")

def command_check(ch, cmd):
    if ch.position == "sleeping":
        ch.send("You can't do that while sleeping!")
        return False
    return True

# Register command and check
mudsys.add_cmd("mycommand", "mc", my_command, "player", True)
mudsys.add_cmd_check("mycommand", command_check)
```

### Event-Driven Programming
```python
import event, hooks

def heal_over_time(owner, data, arg):
    if owner and not owner.is_dead():
        heal_amount = data
        owner.hit_points += heal_amount
        owner.send(f"You heal for {heal_amount} HP.")
        
        # Continue healing
        event.start_event(owner, 30.0, heal_over_time, heal_amount, arg)

def combat_hook(info):
    parsed = hooks.parse_info(info)
    attacker, defender = parsed[0], parsed[1]
    
    if defender.hit_points < defender.max_hit_points * 0.5:
        # Start healing when below 50% health
        event.start_event(defender, 5.0, heal_over_time, 10, "regen")

hooks.add("combat_hit", combat_hook)
```

### World Database Operations
```python
import mudsys, storage

class CustomData:
    def __init__(self, storage_set=None):
        if storage_set:
            self.value = storage_set.readString("value")
        else:
            self.value = "default"
    
    def store(self):
        set = storage.StorageSet()
        set.storeString("value", self.value)
        return set
    
    def setKey(self, key):
        self.key = key

# Register with world database
mudsys.world_add_type("custom_data", CustomData)

# Store and retrieve data
data = CustomData()
data.value = "custom_value"
mudsys.world_put_type("custom_data", "test_key", data)

retrieved = mudsys.world_get_type("custom_data", "test_key")
```

## Performance Considerations

### Efficient Object Access
```python
# Good: Cache frequently accessed objects
room_cache = {}
def get_cached_room(key):
    if key not in room_cache:
        room_cache[key] = room.get_room(key)
    return room_cache[key]

# Good: Use specific search functions
target = char.find_char(ch, ch.room.chars, 1, "guard")

# Avoid: Iterating through all objects unnecessarily
# for obj in obj.obj_list():  # This is expensive for large games
```

### Memory Management
```python
# Good: Clean up references
def cleanup_character(character):
    event.interrupt_events_involving(character)
    character.fromall()  # Remove from room
    
# Good: Use appropriate data structures
# Store simple data in variables, complex data in auxiliary data
```

### Event System Optimization
```python
# Good: Use appropriate delays
event.start_event(character, 1.0, quick_action, data, "")    # 1 second
event.start_event(character, 60.0, periodic_action, data, "") # 1 minute

# Good: Check object validity in events
def safe_event(owner, data, arg):
    if not owner or owner.is_dead():
        return  # Don't continue if owner is invalid
    
    # Proceed with event logic
```

## See Also

- [EObjs (External Objects)](eobjs.md) - C-defined Python classes
- [SEFuns (System External Functions)](sefuns.md) - Python-defined global functions
- [Module Reference](modules/) - Individual module documentation
- [Core Concepts: Python Integration](../core-concepts/python-integration.md)