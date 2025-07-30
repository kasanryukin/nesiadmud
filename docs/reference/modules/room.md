---
layout: default
title: room Module
parent: Modules
grand_parent: API Reference
nav_order: 7
---

# room Module

The `room` module contains the Python wrapper for rooms and utilities for loading and instancing rooms. It provides both the PyRoom class (EObj) and utility functions (EFuns) for room management and world building.

**Module Type**: Core EFuns (External Functions) + EObjs (External Objects)  
**Import**: `import room`

## Overview

The room module is essential for world building and location management, providing:
- Room creation and manipulation
- Room instancing from prototypes
- Exit and connection management
- Room-specific commands and triggers
- Environmental messaging and effects

## PyRoom Class (EObj)

The `Room` class represents locations in the game world where characters and objects can exist.

### Constructor

#### Room(uid_or_string_key)

Creates a new Python reference to a room by UID or string key.

**Parameters**:
- `uid_or_string_key` (int or str): Room UID or database key

**Behavior**:
- If a string key is provided, first tries to generate a room from a room prototype of the same name
- If no prototype exists, creates a new blank room in the room table with the given key

**Example**:
```python
import room

# Create room by key (will use prototype if exists)
tavern = room.Room("tavern")

# Create room with specific key
my_room = room.Room("custom_room_001")
```

### Core Methods

#### send(mssg)

**Returns**: `None`

Sends a message to all characters in the room.

**Parameters**:
- `mssg` (str): The message to send

**Example**:
```python
import room

tavern = room.Room("tavern")
tavern.send("The fire crackles warmly in the hearth.")
```

#### reset()

**Returns**: `None`

Runs the room's reset commands and reset hooks, typically used to respawn NPCs and objects.

**Example**:
```python
import room

dungeon_room = room.Room("dungeon_entrance")
dungeon_room.reset()  # Respawn monsters and treasure
```

### Exit Management

#### dig(dir, dest)

**Returns**: `PyExit`

Links the room to another room via the specified direction. Creates a new exit or modifies an existing one.

**Parameters**:
- `dir` (str): The direction name (e.g., "north", "up", "portal")
- `dest` (PyRoom or str): The destination room or room key

**Example**:
```python
import room

tavern = room.Room("tavern")
street = room.Room("main_street")

# Create exit from tavern to street
exit_south = tavern.dig("south", street)

# Create exit using room key
tavern.dig("upstairs", "tavern_upper")
```

#### exit(dir)

**Returns**: `PyExit` or `None`

Returns an exit for the specified direction.

**Parameters**:
- `dir` (str): The direction name

**Example**:
```python
import room

tavern = room.Room("tavern")
south_exit = tavern.exit("south")
if south_exit:
    print(f"South leads to: {south_exit.dest.name}")
```

#### fill(dir)

**Returns**: `None`

Erases an exit in the specified direction.

**Parameters**:
- `dir` (str): The direction to remove

**Example**:
```python
import room

tavern = room.Room("tavern")
tavern.fill("north")  # Remove north exit
```

#### exdir(exit)

**Returns**: `str` or `None`

Returns the direction for a specified exit.

**Parameters**:
- `exit` (PyExit): The exit object

### Extra Descriptions

#### edesc(keywords, desc)

**Returns**: `None`

Creates an extra description for the room, accessible via keywords when players examine specific things.

**Parameters**:
- `keywords` (str): Comma-separated list of keywords
- `desc` (str): The description text

**Example**:
```python
import room

tavern = room.Room("tavern")
tavern.edesc("bar,counter", "The wooden bar is scarred from years of use. Bottles line the shelves behind it.")
tavern.edesc("fireplace,fire", "A warm fire crackles in the stone fireplace, casting dancing shadows on the walls.")
```

### Room Commands

#### add_cmd(name, shorthand, cmd_func, user_group, interrupts=False)

**Returns**: `None`

Adds a new player command specific to this room.

**Parameters**:
- `name` (str): The command name
- `shorthand` (str): Preferred shorthand (or None)
- `cmd_func` (function): Command function taking (character, command_name, argument)
- `user_group` (str): Required user group
- `interrupts` (bool, optional): Whether command interrupts actions

**Example**:
```python
import room

def ring_bell(ch, cmd, arg):
    ch.send("You ring the tavern bell loudly!")
    ch.room.send(f"{ch.name} rings the bell behind the bar.")

tavern = room.Room("tavern")
tavern.add_cmd("ring", "ri", ring_bell, "player", True)
```

#### add_cmd_check(cmd_name, check_func)

**Returns**: `None`

Adds a command check function specific to this room.

**Parameters**:
- `cmd_name` (str): The command name
- `check_func` (function): Check function taking (character, command_name)

### Auxiliary Data and Variables

#### aux(name)

**Returns**: Auxiliary data object or `None`

Alias for `getAuxiliary(name)`. Returns the room's auxiliary data of the specified name.

**Parameters**:
- `name` (str): The auxiliary data name

#### getAuxiliary(name)

**Returns**: Auxiliary data object or `None`

Returns the room's auxiliary data of the specified name.

**Parameters**:
- `name` (str): The auxiliary data name

#### setvar(name, val)

**Returns**: `None`

Sets a special variable for the room. Intended for scripts and triggers.

**Parameters**:
- `name` (str): The variable name
- `val` (str or number): The variable value

#### getvar(name)

**Returns**: `str` or `number`

Returns the value of a special variable. Returns 0 if not set.

**Parameters**:
- `name` (str): The variable name

#### hasvar(name)

**Returns**: `bool`

Returns True if the room has the specified special variable.

**Parameters**:
- `name` (str): The variable name

#### deletevar(name)

**Returns**: `None`

Deletes a special variable from the room.

**Parameters**:
- `name` (str): The variable name

#### delvar(name)

**Returns**: `None`

Alias for `deletevar(name)`.

### Triggers and Scripts

#### attach(trigger)

**Returns**: `None`

Attaches a trigger to the room by key name.

**Parameters**:
- `trigger` (str): The trigger key name

#### detach(trigger)

**Returns**: `None`

Detaches a trigger from the room by key name.

**Parameters**:
- `trigger` (str): The trigger key name

#### do_trigs(type, ch=None, obj=None, room=None, exit=None, cmd=None, arg=None, opts=None)

**Returns**: `None`

Runs triggers of the specified type on the room.

**Parameters**:
- `type` (str): The trigger type
- `ch` (PyChar, optional): Character variable for trigger
- `obj` (PyObj, optional): Object variable for trigger
- `room` (PyRoom, optional): Room variable for trigger
- `exit` (PyExit, optional): Exit variable for trigger
- `cmd` (str, optional): Command variable for trigger
- `arg` (str, optional): Argument variable for trigger
- `opts` (dict, optional): Optional variables dictionary

### Utility Methods

#### isinstance(prototype)

**Returns**: `bool`

Returns whether the room inherits from the specified room prototype.

**Parameters**:
- `prototype` (str): The prototype name

#### hasBit(name)

**Returns**: `bool`

Returns whether the room has a specific bit toggled.

**Parameters**:
- `name` (str): The bit name

## Room Properties

### Basic Information

#### name
**Type**: `str`  
The room's name (e.g., "Town Square").

#### desc
**Type**: `str`  
The room's description when looked at.

#### terrain
**Type**: `str`  
The current terrain type of the room.

### Location and Identity

#### uid
**Type**: `int` (read-only)  
The room's unique identification number.

#### proto
**Type**: `str` (read-only)  
The room's unique identifier key. For non-instanced rooms, equivalent to the main room prototype inherited from.

#### protoname
**Type**: `str` (read-only)  
The first half of the room's unique identifier key.

#### locale
**Type**: `str` (read-only)  
The zone the room belongs to.

### Prototypes and Inheritance

#### protos
**Type**: `str` (read-only)  
Comma-separated list of room prototypes this room inherits from.

### Contents

#### chars
**Type**: `list` (read-only)  
List of all characters in the room. Immutable.

#### contents
**Type**: `list` (read-only)  
List of objects in the room. Immutable.

#### objs
**Type**: `list` (read-only)  
Alias for `contents`.

### Exits

#### exnames
**Type**: `list` (read-only)  
List of the room's exits by direction. Immutable.

### Settings

#### bits
**Type**: `str`  
Comma-separated list of setting bits currently toggled on the room.

## Module Functions (EFuns)

### Room Management

#### get_room(key)

**Returns**: `PyRoom` or `None`

Takes a room key/locale and returns the matching room.

**Parameters**:
- `key` (str): The room key or locale

**Example**:
```python
import room

tavern = room.get_room("tavern")
if tavern:
    tavern.send("Welcome to the tavern!")
```

#### instance(room_proto, as_key=None)

**Returns**: `PyRoom`

Creates an instanced copy of a room from a room prototype.

**Parameters**:
- `room_proto` (str): The room prototype name
- `as_key` (str, optional): Custom key for the instanced room

**Example**:
```python
import room

# Create instance with auto-generated key
dungeon_room = room.instance("generic_dungeon_room")

# Create instance with specific key
boss_room = room.instance("boss_chamber", "dragon_lair_001")
```

#### is_loaded(key)

**Returns**: `bool`

Returns whether a room with the given key currently exists in the game.

**Parameters**:
- `key` (str): The room key

**Example**:
```python
import room

if room.is_loaded("secret_chamber"):
    secret = room.get_room("secret_chamber")
    secret.send("Someone has discovered this place!")
```

#### is_abstract(proto)

**Returns**: `bool`

Returns whether a specified room prototype is abstract. Also returns True if the prototype doesn't exist.

**Parameters**:
- `proto` (str): The prototype name

**Example**:
```python
import room

if not room.is_abstract("tavern_template"):
    # Can create instances of this prototype
    new_tavern = room.instance("tavern_template")
```

## Usage Patterns

### Creating Connected Areas

```python
import room

# Create a series of connected rooms
entrance = room.Room("dungeon_entrance")
entrance.name = "Dungeon Entrance"
entrance.desc = "A dark opening leads into the depths of the earth."

corridor = room.Room("dungeon_corridor")
corridor.name = "Dark Corridor"
corridor.desc = "A narrow stone corridor stretches into darkness."

chamber = room.Room("treasure_chamber")
chamber.name = "Treasure Chamber"
chamber.desc = "Gold and jewels glitter in the torchlight."

# Connect the rooms
entrance.dig("north", corridor)
corridor.dig("south", entrance)
corridor.dig("east", chamber)
chamber.dig("west", corridor)
```

### Room-Specific Commands

```python
import room

def pray_command(ch, cmd, arg):
    """Special pray command for temple rooms"""
    ch.send("You kneel and offer a prayer to the gods.")
    ch.sendaround(f"{ch.name} kneels in prayer.")
    
    # Give blessing effect
    ch.setvar("blessed", 1)
    ch.send("You feel blessed by divine favor.")

def check_in_temple(ch, cmd):
    """Check if character is worthy to pray"""
    if ch.getvar("cursed"):
        ch.send("The gods will not hear your prayers while you are cursed.")
        return False
    return True

# Set up temple room
temple = room.Room("temple")
temple.add_cmd("pray", "pr", pray_command, "player")
temple.add_cmd_check("pray", check_in_temple)
```

### Environmental Effects

```python
import room, event

def setup_atmospheric_room(room_key, messages, delay_range=(60, 180)):
    """Set up a room with atmospheric messages"""
    target_room = room.get_room(room_key)
    if not target_room:
        return
    
    def atmospheric_message(owner, data, arg):
        if owner and owner.chars:  # Only if room has characters
            import random
            message = random.choice(data)
            owner.send(message)
            
            # Schedule next message
            next_delay = random.randint(*delay_range)
            event.start_event(owner, next_delay, atmospheric_message, data, arg)
    
    # Start the atmospheric system
    import random
    initial_delay = random.randint(*delay_range)
    event.start_event(target_room, initial_delay, atmospheric_message, messages, "atmosphere")

# Usage
forest_messages = [
    "A gentle breeze rustles through the leaves overhead.",
    "You hear the distant call of a bird.",
    "Sunlight filters through the forest canopy.",
    "A small animal scurries through the underbrush."
]

setup_atmospheric_room("enchanted_forest", forest_messages)
```

### Room Instancing for Dynamic Content

```python
import room, char, obj

def create_private_chamber(player, chamber_type="meditation"):
    """Create a private instanced room for a player"""
    # Create unique key for this player's room
    room_key = f"{chamber_type}_{player.name}_{player.uid}"
    
    # Instance the room
    private_room = room.instance(f"{chamber_type}_template", room_key)
    
    # Customize for the player
    private_room.name = f"{player.name}'s {chamber_type.title()} Chamber"
    private_room.desc = f"A private {chamber_type} chamber created for {player.name}."
    
    # Add special exit back to player's original location
    private_room.dig("out", player.room)
    
    # Move player to the private room
    player.room = private_room
    player.send(f"You enter your private {chamber_type} chamber.")
    
    return private_room

# Usage in a command
def meditate_command(ch, cmd, arg):
    if ch.room.proto == "meditation_template":
        ch.send("You are already in a meditation chamber.")
        return
    
    private_chamber = create_private_chamber(ch, "meditation")
    
    # Set up automatic cleanup after 30 minutes
    def cleanup_chamber(owner, data, arg):
        if owner and owner.chars:
            for character in owner.chars:
                character.room = data  # Return to original room
                character.send("The meditation chamber fades away.")
    
    event.start_event(private_chamber, 1800, cleanup_chamber, ch.room, "cleanup")
```

### Room Reset Systems

```python
import room, char, obj, event

def setup_room_reset(room_key, reset_interval=3600):
    """Set up automatic room reset system"""
    target_room = room.get_room(room_key)
    if not target_room:
        return
    
    def room_reset_event(owner, data, arg):
        if owner:
            # Announce reset to players in room
            if owner.chars:
                owner.send("The area shimmers as magical forces restore it.")
            
            # Perform the reset
            owner.reset()
            
            # Schedule next reset
            event.start_event(owner, data, room_reset_event, data, arg)
    
    # Start the reset cycle
    event.start_event(target_room, reset_interval, room_reset_event, reset_interval, "auto_reset")

# Set up various rooms with different reset intervals
setup_room_reset("goblin_cave", 1800)    # 30 minutes
setup_room_reset("treasure_vault", 7200)  # 2 hours
setup_room_reset("boss_chamber", 86400)   # 24 hours
```

### Extra Description Management

```python
import room

def setup_detailed_room(room_key):
    """Set up a room with rich extra descriptions"""
    target_room = room.get_room(room_key)
    if not target_room:
        return
    
    # Main room description
    target_room.name = "The Royal Library"
    target_room.desc = """
    Towering bookshelves stretch from floor to ceiling, filled with ancient tomes
    and scrolls. A large oak desk sits in the center of the room, while comfortable
    reading chairs are scattered about. Sunlight streams through tall windows,
    illuminating motes of dust dancing in the air.
    """
    
    # Add extra descriptions for examinable features
    target_room.edesc("shelves,books,tomes", 
        "The shelves are packed with books on every conceivable subject. "
        "Many appear to be centuries old, their leather bindings cracked with age.")
    
    target_room.edesc("desk,oak", 
        "The massive oak desk is covered with open books, scrolls, and writing "
        "implements. Ink stains and burn marks tell of long hours of study.")
    
    target_room.edesc("chairs,chair", 
        "Plush velvet chairs are positioned near the windows for optimal reading "
        "light. They look incredibly comfortable.")
    
    target_room.edesc("windows,window,sunlight", 
        "Tall arched windows let in streams of golden sunlight. Through them, "
        "you can see the castle gardens below.")

# Usage
setup_detailed_room("royal_library")
```

## OLC Integration and Extra Code

Most room creation and editing in NakedMud is done through the Online Creation (OLC) system using commands like `redit`, `rlist`, and `zlist`. Python code is typically added through the **Extra Code** option in room prototypes.

### Using Python in Room Extra Code

When editing a room prototype with `redit`, you can add Python code in the Extra Code section that will be executed when the room is loaded or during specific events:

```python
# Room Extra Code Example - executed when room loads
import event, random

def setup_atmospheric_effects(room):
    """Add atmospheric messages to this room"""
    messages = [
        "A gentle breeze stirs the air.",
        "You hear distant sounds echoing.",
        "The atmosphere feels charged with energy."
    ]
    
    def atmospheric_event(owner, data, arg):
        if owner and owner.chars:
            message = random.choice(data)
            owner.send(message)
            # Schedule next atmospheric message
            delay = random.randint(120, 300)  # 2-5 minutes
            event.start_event(owner, delay, atmospheric_event, data, arg)
    
    # Start the atmospheric system
    initial_delay = random.randint(60, 180)
    event.start_event(room, initial_delay, atmospheric_event, messages, "atmosphere")

# Execute setup when room loads
setup_atmospheric_effects(me)  # 'me' refers to the current room in Extra Code
```

### Room Prototype Integration

Room prototypes created with `redit` can include Python functionality:

```python
# Example: Room with special enter/exit behavior
import hooks

def room_enter_hook(info):
    """Handle characters entering this room"""
    parsed = hooks.parse_info(info)
    character, room = parsed[0], parsed[1]
    
    if character and room and room == me:  # 'me' is this room
        if character.is_pc:
            character.send("You feel a strange energy as you enter this place.")
            # Add temporary effect, modify stats, etc.

def room_exit_hook(info):
    """Handle characters leaving this room"""
    parsed = hooks.parse_info(info)
    character, room = parsed[0], parsed[1]
    
    if character and room and room == me:
        if character.is_pc:
            character.send("The strange energy fades as you leave.")

# Register hooks for this specific room
hooks.add("char_enter_room", room_enter_hook)
hooks.add("char_leave_room", room_exit_hook)
```

### Room Commands and Interactions

Add room-specific commands through Extra Code:

```python
# Room-specific command example
import mudsys

def examine_altar_command(ch, cmd, arg):
    """Special examine command for altar in this room"""
    if ch.room != me:  # Only works in this room
        return
    
    ch.send("You examine the ancient altar closely...")
    ch.send("Strange runes glow faintly along its surface.")
    
    # Maybe trigger a quest or give information
    if not ch.getvar("altar_examined"):
        ch.setvar("altar_examined", 1)
        ch.send("You feel you've learned something important.")

# Add the command to this room only
me.add_cmd("examine", "ex", examine_altar_command, "player")
```

### Working with OLC Commands

- **`redit <room_key>`** - Edit or create a room prototype
- **`rlist [zone]`** - List room prototypes in a zone
- **`zlist`** - List all zones
- **`goto <room_key>`** - Go to a specific room for testing

The Python code in Extra Code sections has access to:
- **`me`** - The current room object
- All imported modules (import statements work normally)
- Full access to the room's properties and methods
- Ability to modify room behavior dynamically

## See Also

- [char Module](char.md) - Character manipulation and PyChar class
- [exit Module](exit.md) - Exit system and PyExit class
- [obj Module](obj.md) - Object management and PyObj class
- [mudsys Module](mudsys.md) - Core system functions
- [olc Module](olc.md) - Online creation system
- [Core Concepts: Prototypes](../../core-concepts/prototypes.md)
- [Tutorials: Building Rooms](../../tutorials/building-rooms.md)