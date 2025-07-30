---
layout: default
title: EObjs (External Objects)
parent: API Reference
nav_order: 3
---

# EObjs (External Objects)

EObjs (External Objects) are C-defined Python classes that represent core game entities. These classes provide Python wrappers around C data structures, allowing Python scripts to interact with characters, rooms, objects, and other game entities through a familiar object-oriented interface.

## Overview

EObjs serve as the primary data containers and interfaces for game entities. They provide:
- Object-oriented access to game data
- Method interfaces for entity manipulation
- Property access for entity attributes
- Integration with the auxiliary data system
- Automatic memory management and cleanup

## Core EObj Classes

### PyChar Class
**Module**: `char`  
**Represents**: Player characters and NPCs  
**C Structure**: `CHAR_DATA`

#### Key Properties
```python
# Basic information
character.name          # Character name
character.desc          # Long description
character.keywords      # Search keywords
character.race          # Character race
character.sex           # Character gender

# Status and state
character.position      # Current position (standing, sitting, etc.)
character.hidden        # Visibility level
character.weight        # Character weight

# Location and relationships
character.room          # Current room
character.socket        # Attached socket (for players)
character.on            # Furniture being used

# Inventory and equipment
character.inv           # Inventory list (read-only)
character.eq            # Equipment list (read-only)
character.bodyparts     # Available bodyparts (read-only)

# Identity and permissions
character.is_npc        # True if NPC
character.is_pc         # True if player character
character.uid           # Unique identifier
character.user_groups   # Permission groups
```

#### Key Methods
```python
# Communication
character.send(message, dict=None, newline=True)
character.sendaround(message, dict=None, cansee_only=False)
character.page(text)

# Actions and commands
character.act(command)
character.startAction(delay, on_complete, on_interrupt, data, arg)
character.interrupt()
character.isActing()

# Visibility and perception
character.cansee(thing)
character.see_as(thing)

# Equipment management
character.equip(obj, positions=None, forced=False)
character.get_equip(bodypart)
character.get_slots(obj)

# Data management
character.aux(name)
character.setvar(name, val)
character.getvar(name)
character.hasvar(name)

# Triggers and scripts
character.attach(trigger)
character.detach(trigger)
character.do_trigs(type, **kwargs)

# Utility methods
character.copy()
character.store()
character.isinstance(prototype)
```

### PyRoom Class
**Module**: `room`  
**Represents**: Game locations and areas  
**C Structure**: `ROOM_DATA`

#### Key Properties
```python
# Basic information
room.name               # Room name
room.desc               # Room description
room.terrain            # Terrain type

# Identity and location
room.uid                # Unique identifier
room.proto              # Room prototype key
room.locale             # Zone/area name

# Contents
room.chars              # Characters in room (read-only)
room.contents           # Objects in room (read-only)
room.objs               # Alias for contents

# Exits and connections
room.exnames            # Exit direction names (read-only)

# Settings
room.bits               # Room flags and settings
```

#### Key Methods
```python
# Communication
room.send(message)

# Exit management
room.dig(direction, destination)
room.exit(direction)
room.fill(direction)
room.exdir(exit)

# Room management
room.reset()

# Extra descriptions
room.edesc(keywords, description)

# Commands
room.add_cmd(name, shorthand, cmd_func, user_group, interrupts)
room.add_cmd_check(cmd_name, check_func)

# Data management
room.aux(name)
room.setvar(name, val)
room.getvar(name)
room.hasvar(name)

# Triggers and scripts
room.attach(trigger)
room.detach(trigger)
room.do_trigs(type, **kwargs)

# Utility methods
room.isinstance(prototype)
room.hasBit(name)
```

### PyObj Class
**Module**: `obj`  
**Represents**: Game objects and items  
**C Structure**: `OBJ_DATA`

#### Key Properties
```python
# Basic information
obj.name                # Object name
obj.desc                # Long description
obj.rdesc               # Room description
obj.keywords            # Search keywords

# Multiple item handling
obj.mname               # Multiple name format
obj.mdesc               # Multiple description format

# Physical properties
obj.weight              # Total weight (including contents)
obj.weight_raw          # Raw weight (excluding contents)
obj.hidden              # Visibility level

# Location
obj.room                # Current room
obj.carrier             # Character carrying this
obj.container           # Container holding this
obj.wearer              # Character wearing this

# Contents
obj.contents            # Objects inside this (read-only)
obj.objs                # Alias for contents
obj.chars               # Characters on this furniture (read-only)

# Item type properties
obj.worn_type           # Type of worn item
obj.worn_locs           # Body locations for worn items

# Container properties
obj.container_capacity  # Maximum weight capacity
obj.container_is_closable  # Can be opened/closed
obj.container_is_closed    # Currently closed
obj.container_is_locked    # Currently locked
obj.container_key       # Key prototype for unlocking
obj.container_pick_diff # Lock picking difficulty

# Furniture properties
obj.furniture_type      # Type of furniture ('at' or 'on')
obj.furniture_capacity  # Number of characters it can hold

# Portal properties
obj.portal_dest         # Destination room key
obj.portal_enter_mssg   # Message when entering
obj.portal_leave_mssg   # Message when leaving

# Identity
obj.uid                 # Unique identifier
obj.prototypes          # Inherited prototypes
obj.bits                # Object flags
```

#### Key Methods
```python
# Object management
obj.copy()
obj.fromall()

# Item types
obj.istype(item_type)
obj.settype(item_type)
obj.get_types()
obj.get_type_data(item_type)

# Extra descriptions
obj.edesc(keywords, description)

# Data management
obj.aux(name)
obj.setvar(name, val)
obj.getvar(name)
obj.hasvar(name)

# Triggers and scripts
obj.attach(trigger)
obj.detach(trigger)
obj.do_trigs(type, **kwargs)

# Utility methods
obj.store()
obj.isinstance(prototype)
```

### PyExit Class
**Module**: `exit`  
**Represents**: Connections between rooms  
**C Structure**: `EXIT_DATA`

#### Key Properties
```python
# Basic information
exit.name               # Exit name/direction
exit.desc               # Exit description
exit.keywords           # Search keywords

# Connection
exit.dest               # Destination room
exit.opposite           # Opposite direction exit

# State
exit.is_closed          # Currently closed
exit.is_locked          # Currently locked
exit.is_pickproof       # Cannot be picked
exit.key                # Key prototype for unlocking
exit.pick_diff          # Lock picking difficulty

# Identity
exit.uid                # Unique identifier
```

#### Key Methods
```python
# Data management
exit.aux(name)
exit.setvar(name, val)
exit.getvar(name)
exit.hasvar(name)

# Triggers and scripts
exit.attach(trigger)
exit.detach(trigger)
exit.do_trigs(type, **kwargs)

# Utility methods
exit.isinstance(prototype)
```

### PySocket Class
**Module**: `mudsock`  
**Represents**: Network connections  
**C Structure**: `SOCKET_DATA`

#### Key Properties
```python
# Connection information
socket.addr             # IP address
socket.hostname         # Hostname (if resolved)
socket.port             # Connection port

# State
socket.state            # Connection state
socket.idle             # Idle time in seconds

# Associated entities
socket.account          # Attached account
socket.character        # Attached character

# Communication
socket.outbound_text    # Text being sent to client
socket.inbound_text     # Text received from client

# Identity
socket.uid              # Unique identifier
```

#### Key Methods
```python
# Communication
socket.send(message)
socket.send_raw(message)
socket.page(text)

# Input handling
socket.push_ih(handler, prompt_func)
socket.pop_ih()

# Data management
socket.aux(name)
socket.setvar(name, val)
socket.getvar(name)
socket.hasvar(name)

# Utility methods
socket.close()
```

### PyAccount Class
**Module**: `account`  
**Represents**: Player accounts  
**C Structure**: `ACCOUNT_DATA`

#### Key Properties
```python
# Basic information
account.name            # Account name
account.email           # Email address (if set)

# Characters
account.characters      # List of character names (read-only)

# State
account.socket          # Attached socket

# Permissions
account.user_groups     # Permission groups

# Time information
account.creation_time   # Account creation time
account.last_login      # Last login time

# Identity
account.uid             # Unique identifier
```

#### Key Methods
```python
# Character management
account.add_char(character_name)
account.remove_char(character_name)
account.get_char(character_name)

# Communication
account.send(message)

# Data management
account.aux(name)
account.setvar(name, val)
account.getvar(name)
account.hasvar(name)

# Utility methods
account.store()
```

## Common Usage Patterns

### Character Interaction
```python
import char

# Create and customize an NPC
guard = char.load_mob("guard", room)
guard.name = "a stern city guard"
guard.desc = "This guard watches the area with keen eyes."
guard.keywords = "guard,city,stern"

# Set up communication
guard.send("You are now on duty.")
guard.sendaround("A guard takes up position here.")

# Equipment management
sword = obj.load_obj("longsword")
if guard.equip(sword):
    guard.send("You ready your weapon.")
```

### Room Management
```python
import room

# Create and set up a room
tavern = room.Room("tavern")
tavern.name = "The Prancing Pony"
tavern.desc = "A cozy tavern with a warm fireplace."

# Add exits
street = room.get_room("main_street")
tavern.dig("south", street)

# Add extra descriptions
tavern.edesc("fireplace,fire", "The fire crackles warmly in the stone hearth.")
tavern.edesc("bar,counter", "The wooden bar is polished to a shine.")

# Add room-specific command
def ring_bell(ch, cmd, arg):
    ch.send("You ring the tavern bell!")
    ch.room.send(f"{ch.name} rings the bell.")

tavern.add_cmd("ring", "ri", ring_bell, "player")
```

### Object Creation and Management
```python
import obj

# Create a container
chest = obj.load_obj("treasure_chest")
chest.name = "an ornate treasure chest"
chest.container_capacity = 100.0
chest.container_is_closable = True
chest.container_is_closed = True

# Add contents
gold = obj.load_obj("gold_coins", chest)
gem = obj.load_obj("ruby", chest)

# Set up extra descriptions
chest.edesc("lock,keyhole", "The chest has an intricate brass lock.")
chest.edesc("carvings,ornate", "Elaborate carvings cover the chest's surface.")
```

### Socket and Account Management
```python
import mudsys, account

# Handle new connection
def handle_new_connection(socket):
    socket.send("Welcome to the MUD!")
    
    # Set up login process
    def get_account_name(sock, input_text):
        account_name = input_text.strip()
        
        if mudsys.account_exists(account_name):
            # Load existing account
            acct = mudsys.load_account(account_name)
            mudsys.attach_account_socket(acct, sock)
        else:
            # Create new account
            acct = mudsys.create_account(account_name)
            if acct:
                mudsys.do_register(acct)
                mudsys.attach_account_socket(acct, sock)
    
    def prompt_account_name(sock):
        sock.send_raw("Account name: ")
    
    socket.push_ih(get_account_name, prompt_account_name)
```

## Property Access Patterns

### Read-Only Properties
Many EObj properties are read-only to maintain data integrity:
```python
# These are read-only
character_list = character.inv      # Returns immutable list
room_contents = room.chars          # Returns immutable list
object_contents = obj.contents      # Returns immutable list

# To modify, use appropriate methods
character.equip(weapon)             # Add to equipment
obj.fromall()                       # Remove from current location
```

### Computed Properties
Some properties are computed dynamically:
```python
# These are calculated when accessed
total_weight = obj.weight           # Includes contents
character_age = character.age       # Current age in seconds
is_player = character.is_pc         # Computed from is_npc
```

### Property Relationships
Properties often have relationships:
```python
# Location properties are mutually exclusive
if obj.room:
    assert obj.carrier is None
    assert obj.container is None

if obj.carrier:
    assert obj.room is None
    assert obj.container is None

# Equipment relationships
if obj.wearer:
    assert obj in obj.wearer.eq
    assert obj.carrier == obj.wearer
```

## Method Extension System

EObjs can be extended with custom methods using the mudsys module:
```python
import mudsys

def get_full_name(self):
    """Get character's full name including title"""
    if hasattr(self, 'title') and self.title:
        return f"{self.name} {self.title}"
    return self.name

def is_wealthy(self):
    """Check if character has significant wealth"""
    return self.getvar("gold") > 1000

# Add methods to PyChar class
mudsys.add_char_method("get_full_name", get_full_name)
mudsys.add_char_method("is_wealthy", is_wealthy)

# Now all characters have these methods
character = char.Char()
full_name = character.get_full_name()
wealthy = character.is_wealthy()
```

## Memory Management

EObjs are automatically managed by the C engine:
```python
# Objects are automatically cleaned up when extracted
character.fromall()  # Removes from game world
# Character object becomes invalid after extraction

# Always check validity in delayed operations
def delayed_action(owner, data, arg):
    if not owner:  # Owner was extracted
        return
    
    # Safe to use owner here
    owner.send("Delayed action executed!")
```

## Integration with Auxiliary Data

EObjs integrate seamlessly with the auxiliary data system:
```python
import auxiliary, storage

class CharacterStats:
    def __init__(self, storage_set=None):
        if storage_set:
            self.strength = storage_set.readInt("strength")
            self.intelligence = storage_set.readInt("intelligence")
        else:
            self.strength = 10
            self.intelligence = 10
    
    def store(self):
        set = storage.StorageSet()
        set.storeInt("strength", self.strength)
        set.storeInt("intelligence", self.intelligence)
        return set
    
    def copy(self):
        new_stats = CharacterStats()
        new_stats.strength = self.strength
        new_stats.intelligence = self.intelligence
        return new_stats
    
    def copyTo(self, to):
        to.strength = self.strength
        to.intelligence = self.intelligence

# Install auxiliary data
auxiliary.install("char_stats", CharacterStats, "character")

# Use with EObjs
character = char.Char()
stats = character.aux("char_stats")
if stats:
    stats.strength += 5
    print(f"Strength: {stats.strength}")
```

## See Also

- [EFuns (External Functions)](efuns.md) - C-derived Python functions
- [SEFuns (System External Functions)](sefuns.md) - Python-defined global functions
- [Module Reference](modules/) - Individual module documentation
- [Core Concepts: Auxiliary Data](../core-concepts/auxiliary-data.md)
- [Core Concepts: Prototypes](../core-concepts/prototypes.md)