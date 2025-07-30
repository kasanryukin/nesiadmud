---
layout: default
title: exit Module
parent: Modules
grand_parent: API Reference
nav_order: 9
---

# exit Module

The `exit` module provides the PyExit class for managing connections between rooms, including doors, locks, and special movement messages. Exits are the pathways that allow characters to move between different locations in the game world.

**Module Type**: EObjs (External Objects)  
**Import**: `import exit`

## Overview

The exit module handles:
- Room-to-room connections and pathways
- Door creation and management
- Lock and key systems
- Hidden and special exits
- Custom movement messages
- Exit visibility and access control

## PyExit Class (EObj)

The `Exit` class represents a pathway from one room to another, with optional door, lock, and visibility features.

### Constructor

Exits are typically created through the `room.Room.dig()` method rather than direct instantiation.

### Door Management

#### makedoor(name=None, keywords=None, opposite=None, closed=False, locked=False)

**Returns**: `None`

Creates a door for the exit with specified properties.

**Parameters**:
- `name` (str, optional): The door's name
- `keywords` (str, optional): Comma-separated keywords for the door
- `opposite` (str, optional): Direction name for the return exit
- `closed` (bool, optional): Whether the door starts closed
- `locked` (bool, optional): Whether the door starts locked

**Example**:
```python
import room

tavern = room.Room("tavern")
cellar = room.Room("cellar")

# Create exit with door
down_exit = tavern.dig("down", cellar)
down_exit.makedoor(
    name="heavy wooden door",
    keywords="door,wooden,heavy",
    opposite="up",
    closed=True,
    locked=False
)
```

#### filldoor()

**Returns**: `None`

Removes a door that was on the exit, making it a simple open passage.

**Example**:
```python
# Remove the door from an exit
exit.filldoor()
```

### Door State Control

#### open()

**Returns**: `None`

Opens the exit's door if it exists. Also unlocks the door.

#### close()

**Returns**: `None`

Closes the exit's door if it exists.

#### lock()

**Returns**: `None`

Locks the exit's door if it exists. Also closes the door.

#### unlock()

**Returns**: `None`

Unlocks the exit's door if it exists.

**Example**:
```python
import room

# Get an exit and manipulate its door
tavern = room.Room("tavern")
cellar_exit = tavern.exit("down")

if cellar_exit and cellar_exit.is_closable:
    cellar_exit.close()
    cellar_exit.lock()
    
    # Later...
    cellar_exit.unlock()
    cellar_exit.open()
```

## Exit Properties

### Basic Information

#### desc
**Type**: `str`  
The verbose description of the exit when it is looked at.

**Example**:
```python
exit.desc = "A narrow stone stairway leads down into darkness."
```

### Destination

#### dest
**Type**: `PyRoom`  
The room that this exit leads to. Can be set by assigning a world room key or an actual room object.

**Example**:
```python
import room

tavern = room.Room("tavern")
street = room.Room("main_street")

exit = tavern.exit("south")
exit.dest = street  # Set by room object
# or
exit.dest = "main_street"  # Set by room key
```

#### destproto
**Type**: `str` (read-only)  
The world room key of the destination.

### Door Properties

#### name
**Type**: `str`  
The name of the door for this exit, if any.

#### keywords
**Type**: `str`  
Comma-separated string of the door's keywords for player interaction.

#### opposite
**Type**: `str`  
If the exit is special, a direction name for the exit that leads back to this exit's room.

### Door State

#### is_closable
**Type**: `bool` (read-only)  
True if the exit can be closed (has a door).

#### is_closed
**Type**: `bool` (read-only)  
True if the exit is currently closed.

#### is_locked
**Type**: `bool` (read-only)  
True if the exit is currently locked.

### Security

#### key
**Type**: `str`  
An object prototype name that can be used to unlock this exit. Can be set by assigning a prototype name or an actual object.

**Example**:
```python
# Set key by prototype name
exit.key = "brass_key"

# Set key by object (will use its prototype)
import obj
key_obj = obj.load_obj("brass_key")
exit.key = key_obj
```

#### pick_diff
**Type**: `int`  
Integer value representing how hard the exit's lock is to pick.

### Visibility

#### spot_diff
**Type**: `int`  
Integer value representing how hard the exit is to see.

#### hidden
**Type**: `int`  
Alias for `spot_diff`.

### Movement Messages

#### enter_mssg
**Type**: `str`  
A message displayed when a character enters the destination room via this exit.

#### leave_mssg
**Type**: `str`  
A message displayed when a character leaves the current room via this exit.

**Example**:
```python
# Set up custom movement messages
portal_exit = room.exit("portal")
portal_exit.enter_mssg = "emerges from a swirling magical portal"
portal_exit.leave_mssg = "steps into a swirling magical portal and vanishes"

# When a character uses this exit:
# Other players in origin room see: "Bob steps into a swirling magical portal and vanishes."
# Other players in destination room see: "Bob emerges from a swirling magical portal."
```

### Identity

#### uid
**Type**: `int` (read-only)  
The exit's universal identification number.

#### room
**Type**: `PyRoom` (read-only)  
The room this exit is attached to.

## Usage Patterns

### Creating Basic Exits

```python
import room

# Create two rooms
tavern = room.Room("tavern")
street = room.Room("main_street")

# Create bidirectional connection
south_exit = tavern.dig("south", street)
north_exit = street.dig("north", tavern)

# Add descriptions
south_exit.desc = "The main street of the town lies to the south."
north_exit.desc = "The warm glow of the tavern beckons to the north."
```

### Creating Doors with Locks

```python
import room

# Create rooms
house = room.Room("house_interior")
yard = room.Room("front_yard")

# Create exit with locked door
front_door = house.dig("out", yard)
front_door.makedoor(
    name="sturdy oak door",
    keywords="door,oak,front",
    opposite="in",
    closed=True,
    locked=True
)

# Set door properties
front_door.desc = "A well-crafted oak door with iron hinges."
front_door.key = "house_key"
front_door.pick_diff = 15

# Create the return exit
back_door = yard.dig("in", house)
back_door.makedoor(
    name="sturdy oak door",
    keywords="door,oak,front",
    opposite="out",
    closed=True,
    locked=True
)
back_door.key = "house_key"
```

### Hidden and Secret Exits

```python
import room

# Create a room with a hidden exit
library = room.Room("library")
secret_room = room.Room("secret_chamber")

# Create hidden exit
secret_exit = library.dig("secret", secret_room)
secret_exit.desc = "A narrow passage hidden behind the bookshelf."
secret_exit.spot_diff = 20  # Hard to notice
secret_exit.keywords = "passage,bookshelf,shelf"

# Players would need to "search" or have high perception to find it
# The exit won't show up in normal room descriptions
```

### Special Movement Messages

```python
import room

# Create magical transportation
tower = room.Room("wizard_tower")
dimension = room.Room("pocket_dimension")

# Create portal with special messages
portal = tower.dig("portal", dimension)
portal.desc = "A shimmering magical portal hovers in the air."
portal.enter_mssg = "materializes from a burst of magical energy"
portal.leave_mssg = "steps through the portal and disappears in a flash of light"

# Create return portal
return_portal = dimension.dig("portal", tower)
return_portal.desc = "A shimmering portal back to the material plane."
return_portal.enter_mssg = "steps out of the dimensional portal"
return_portal.leave_mssg = "enters the portal and fades from view"
```

### Conditional Access Exits

```python
import room

def create_guild_entrance(guild_room_key, public_room_key, required_guild):
    """Create an exit that only guild members can use"""
    
    guild_room = room.Room(guild_room_key)
    public_room = room.Room(public_room_key)
    
    # Create the exit
    guild_exit = public_room.dig("guild", guild_room)
    guild_exit.desc = f"The entrance to the {required_guild} guild hall."
    
    # Add a door that's always locked
    guild_exit.makedoor(
        name="guild hall door",
        keywords="door,guild,entrance",
        closed=True,
        locked=True
    )
    
    # Set impossible pick difficulty (requires special access)
    guild_exit.pick_diff = 999
    
    # The actual access control would be handled by movement commands
    # or triggers that check guild membership
    
    return guild_exit

# Usage
mage_entrance = create_guild_entrance("mage_guild", "town_square", "Mages")
```

### Timed Doors

```python
import room, event

def create_timed_door(room1_key, room2_key, direction, open_duration=300):
    """Create a door that automatically closes after a time"""
    
    room1 = room.Room(room1_key)
    room2 = room.Room(room2_key)
    
    # Create exits in both directions
    exit1 = room1.dig(direction, room2)
    
    # Determine opposite direction (simplified)
    opposite_dirs = {
        "north": "south", "south": "north",
        "east": "west", "west": "east",
        "up": "down", "down": "up"
    }
    opposite = opposite_dirs.get(direction, "out")
    exit2 = room2.dig(opposite, room1)
    
    # Create doors
    for exit in [exit1, exit2]:
        exit.makedoor(
            name="heavy stone door",
            keywords="door,stone,heavy",
            closed=True,
            locked=False
        )
    
    def auto_close_door(owner, data, arg):
        """Automatically close and lock the doors"""
        exit1, exit2 = data
        if exit1 and exit2:
            exit1.close()
            exit1.lock()
            exit2.close()
            exit2.lock()
            
            # Notify rooms
            if exit1.room:
                exit1.room.send("The heavy stone door grinds shut and locks.")
            if exit2.room:
                exit2.room.send("The heavy stone door grinds shut and locks.")
    
    def open_timed_door():
        """Open the doors and start the timer"""
        exit1.unlock()
        exit1.open()
        exit2.unlock()
        exit2.open()
        
        # Notify rooms
        exit1.room.send("The heavy stone door grinds open.")
        exit2.room.send("The heavy stone door grinds open.")
        
        # Start close timer
        event.start_event(None, open_duration, auto_close_door, (exit1, exit2), "auto_close")
    
    return exit1, exit2, open_timed_door

# Usage
vault_exit1, vault_exit2, open_vault = create_timed_door("bank", "vault", "vault")

# The vault doors can be opened by a special mechanism
def vault_lever_command(ch, cmd, arg):
    ch.send("You pull the heavy lever.")
    ch.room.send(f"{ch.name} pulls a heavy lever.")
    open_vault()

# Add the lever command to the bank room
bank = room.Room("bank")
bank.add_cmd("pull", "pu", vault_lever_command, "player")
```

### Exit State Management

```python
import room

def manage_door_state(room_key, direction, action):
    """Utility function to manage door states"""
    target_room = room.Room(room_key)
    exit = target_room.exit(direction)
    
    if not exit:
        return f"No exit found in direction '{direction}'"
    
    if not exit.is_closable:
        return "This exit has no door"
    
    if action == "open":
        if not exit.is_closed:
            return "The door is already open"
        exit.open()
        return "You open the door"
    
    elif action == "close":
        if exit.is_closed:
            return "The door is already closed"
        exit.close()
        return "You close the door"
    
    elif action == "lock":
        if exit.is_locked:
            return "The door is already locked"
        exit.lock()
        return "You lock the door"
    
    elif action == "unlock":
        if not exit.is_locked:
            return "The door is already unlocked"
        exit.unlock()
        return "You unlock the door"
    
    return "Invalid action"

# Usage in commands
def door_command(ch, cmd, arg):
    """Handle door manipulation commands"""
    if not arg:
        ch.send("Usage: door <open|close|lock|unlock> <direction>")
        return
    
    parts = arg.split()
    if len(parts) != 2:
        ch.send("Usage: door <open|close|lock|unlock> <direction>")
        return
    
    action, direction = parts
    result = manage_door_state(ch.room.proto, direction, action)
    ch.send(result)
```

## OLC Integration and Extra Code

Most exit creation and management in NakedMud is done through the room editor (`redit`) where exits are created using the `dig` command or through the room editing interface. Python code for exits is typically added through room Extra Code since exits belong to rooms.

### Using Python with Exits in Room Extra Code

When editing a room with `redit`, you can add Python code that manipulates exits:

```python
# Room Extra Code Example - working with exits
import hooks, event, random

def setup_exit_behaviors(room):
    """Set up special behaviors for exits in this room"""
    
    # Get the north exit (if it exists)
    north_exit = room.exit("north")
    if north_exit:
        # Make it a timed door that closes automatically
        def auto_close_door(owner, data, arg):
            """Automatically close the north door"""
            if north_exit.is_closable and not north_exit.is_closed:
                north_exit.close()
                room.send("The heavy door slowly swings shut.")
        
        # Set up a hook to auto-close when someone passes through
        def exit_hook(info):
            parsed = hooks.parse_info(info)
            character, from_room, to_room, direction = parsed
            
            if from_room == room and direction == "north":
                # Door will close in 10 seconds
                event.start_event(None, 10, auto_close_door, None, "auto_close")
        
        hooks.add("char_move", exit_hook)

def setup_secret_exit(room):
    """Set up a secret exit that appears randomly"""
    
    def reveal_secret_exit(owner, data, arg):
        """Temporarily reveal a secret exit"""
        if not room.exit("secret"):
            # Create temporary exit to hidden room
            secret_exit = room.dig("secret", "hidden_chamber")
            secret_exit.desc = "A shimmering portal has appeared in the wall!"
            secret_exit.spot_diff = 0  # Easy to see when active
            
            room.send("Reality shimmers and a secret passage becomes visible!")
            
            # Hide it again after 5 minutes
            def hide_secret_exit(owner, data, arg):
                if room.exit("secret"):
                    room.fill("secret")  # Remove the exit
                    room.send("The secret passage fades from view.")
            
            event.start_event(None, 300, hide_secret_exit, None, "hide_secret")
        
        # Schedule next random appearance (30-60 minutes)
        next_reveal = random.randint(1800, 3600)
        event.start_event(None, next_reveal, reveal_secret_exit, None, "reveal_secret")
    
    # Start the secret exit cycle
    initial_delay = random.randint(600, 1800)  # 10-30 minutes
    event.start_event(None, initial_delay, reveal_secret_exit, None, "reveal_secret")

# Execute setup when room loads
setup_exit_behaviors(me)  # 'me' refers to the current room
setup_secret_exit(me)
```

### Exit Manipulation in Room Code

Exits are typically managed through room prototypes:

```python
# Example: Puzzle room with changing exits
import mud, random

def setup_puzzle_room(room):
    """Set up a room where exits change based on conditions"""
    
    def rotate_exits(owner, data, arg):
        """Rotate the available exits"""
        # Remove all current exits except 'out'
        for direction in ["north", "south", "east", "west"]:
            if room.exit(direction):
                room.fill(direction)
        
        # Add new random exits
        possible_destinations = ["forest_1", "forest_2", "forest_3", "forest_4"]
        directions = ["north", "south", "east", "west"]
        
        # Randomly assign 2 exits
        chosen_dirs = random.sample(directions, 2)
        chosen_dests = random.sample(possible_destinations, 2)
        
        for direction, destination in zip(chosen_dirs, chosen_dests):
            new_exit = room.dig(direction, destination)
            new_exit.desc = f"A path leads {direction} through the shifting forest."
        
        room.send("The forest paths shift and change around you!")
        
        # Schedule next rotation (10 minutes)
        event.start_event(None, 600, rotate_exits, None, "rotate")
    
    # Start the rotation system
    event.start_event(None, 60, rotate_exits, None, "rotate")

def setup_conditional_exit(room):
    """Set up an exit that only appears under certain conditions"""
    
    def check_exit_conditions(owner, data, arg):
        """Check if conditions are met to reveal exit"""
        # Example: Exit only appears at night
        if mud.is_night():
            if not room.exit("hidden"):
                night_exit = room.dig("hidden", "night_realm")
                night_exit.desc = "A shadowy passage that only exists in darkness."
                night_exit.enter_mssg = "emerges from the shadows"
                night_exit.leave_mssg = "melts into the darkness"
                room.send("As darkness falls, a shadowy passage becomes visible.")
        else:
            if room.exit("hidden"):
                room.fill("hidden")
                room.send("The shadowy passage fades with the coming of light.")
        
        # Check again in an hour
        event.start_event(None, 3600, check_exit_conditions, None, "condition_check")
    
    # Start condition checking
    check_exit_conditions(None, None, None)

# Execute setup when room loads
setup_puzzle_room(me)
setup_conditional_exit(me)
```

### Working with Doors in Extra Code

```python
# Example: Interactive door system
import hooks

def setup_interactive_door(room):
    """Set up a door with special interaction requirements"""
    
    # Get the east exit (assuming it has a door)
    east_exit = room.exit("east")
    if east_exit and east_exit.is_closable:
        
        def door_interaction_hook(info):
            """Handle attempts to open the door"""
            parsed = hooks.parse_info(info)
            character, command, argument = parsed
            
            if character.room == room and command in ["open", "unlock"]:
                if "east" in argument.lower() or "door" in argument.lower():
                    # Check if character has the right item
                    has_key = False
                    for item in character.inv:
                        if "crystal key" in item.name.lower():
                            has_key = True
                            break
                    
                    if has_key:
                        if east_exit.is_locked:
                            east_exit.unlock()
                            character.send("The crystal key glows and the door unlocks!")
                            room.send(f"{character.name}'s key glows brightly.")
                        if east_exit.is_closed:
                            east_exit.open()
                            character.send("The ancient door creaks open.")
                    else:
                        character.send("The door requires a special key to open.")
                        character.send("You notice a crystal-shaped keyhole.")
        
        hooks.add("player_command", door_interaction_hook)

# Execute setup when room loads
setup_interactive_door(me)
```

### Working with OLC Commands

- **`redit <room_key>`** - Edit room and its exits
- **`dig <direction> <destination>`** - Create an exit (within redit)
- **`fill <direction>`** - Remove an exit (within redit)
- **`goto <room_key>`** - Go to a room to test exits

Exit properties are typically set through the room editor interface, but can be modified through Python code in the room's Extra Code section.

## See Also

- [room Module](room.md) - Room management and PyRoom class
- [char Module](char.md) - Character manipulation for movement
- [obj Module](obj.md) - Objects that can serve as keys
- [mudsys Module](mudsys.md) - Movement command registration
- [olc Module](olc.md) - Online creation system
- [event Module](event.md) - Event system for timed door behaviors
- [hooks Module](hooks.md) - Hook system for exit interactions
- [Core Concepts: World Building](../../core-concepts/world-building.md)
- [Tutorials: Creating Exits and Doors](../../tutorials/exits-and-doors.md)