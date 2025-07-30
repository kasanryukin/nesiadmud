---
layout: default
title: obj Module
parent: Modules
grand_parent: API Reference
nav_order: 8
---

# obj Module

The `obj` module contains the Python wrapper for game objects and utilities for listing, storing, and generating objects from prototypes. It provides both the PyObj class (EObj) and utility functions (EFuns) for comprehensive object management.

**Module Type**: Core EFuns (External Functions) + EObjs (External Objects)  
**Import**: `import obj`

## Overview

The obj module handles all aspects of game objects, including:
- Item creation and manipulation
- Container functionality
- Equipment and worn items
- Furniture and interactive objects
- Portal objects for transportation
- Object type systems and behaviors

## PyObj Class (EObj)

The `Obj` class represents all physical items in the game world, from simple objects to complex interactive items.

### Constructor

Objects are typically created through `obj.load_obj()` rather than direct instantiation.

### Core Methods

#### copy()

**Returns**: `PyObj`

Returns a copy of the object.

**Example**:
```python
import obj

original = obj.load_obj("longsword")
duplicate = original.copy()
```

#### fromall()

**Returns**: `None`

Removes the object from whichever room, character, or container it is currently in.

**Example**:
```python
import obj

sword = obj.load_obj("longsword")
# ... sword gets placed somewhere ...
sword.fromall()  # Remove from current location
```

### Item Types

#### istype(item_type)

**Returns**: `bool`

Returns True if the object is of the specified item type.

**Parameters**:
- `item_type` (str): The item type to check

#### settype(item_type)

**Returns**: `None`

Makes the object be the specified item type.

**Parameters**:
- `item_type` (str): The item type to set

#### get_types()

**Returns**: `str`

Returns a comma-separated list of item types this object has.

#### get_type_data(item_type)

**Returns**: Type data object or `None`

Returns Python item type data if it exists.

**Parameters**:
- `item_type` (str): The item type

**Example**:
```python
import obj

chest = obj.load_obj("treasure_chest")

# Check and set item types
if chest.istype("container"):
    print("This is a container")

# Add furniture functionality
chest.settype("furniture")

# Get all types
types = chest.get_types()  # e.g., "container,furniture"
```

### Extra Descriptions

#### edesc(keywords, desc)

**Returns**: `None`

Creates an extra description for the object, accessible via keywords when players examine specific features.

**Parameters**:
- `keywords` (str): Comma-separated list of keywords
- `desc` (str): The description text

**Example**:
```python
import obj

sword = obj.load_obj("ornate_sword")
sword.edesc("blade,steel", "The blade is forged from the finest steel, with intricate runes etched along its length.")
sword.edesc("hilt,handle", "The hilt is wrapped in supple leather, worn smooth by countless hands.")
```

### Auxiliary Data and Variables

#### aux(name)

**Returns**: Auxiliary data object or `None`

Alias for `getAuxiliary(name)`. Returns the object's auxiliary data of the specified name.

**Parameters**:
- `name` (str): The auxiliary data name

#### getAuxiliary(name)

**Returns**: Auxiliary data object or `None`

Returns the object's auxiliary data of the specified name.

**Parameters**:
- `name` (str): The auxiliary data name

#### setvar(name, val)

**Returns**: `None`

Sets a special variable for the object. Intended for scripts and triggers.

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

Returns True if the object has the specified special variable.

**Parameters**:
- `name` (str): The variable name

#### deletevar(name)

**Returns**: `None`

Deletes a special variable from the object.

**Parameters**:
- `name` (str): The variable name

#### delvar(name)

**Returns**: `None`

Alias for `deletevar(name)`.

### Triggers and Scripts

#### attach(trigger)

**Returns**: `None`

Attaches a trigger to the object by key name.

**Parameters**:
- `trigger` (str): The trigger key name

#### detach(trigger)

**Returns**: `None`

Detaches a trigger from the object by key name.

**Parameters**:
- `trigger` (str): The trigger key name

#### do_trigs(type, ch=None, obj=None, room=None, exit=None, cmd=None, arg=None, opts=None)

**Returns**: `None`

Runs triggers of the specified type on the object.

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

#### store()

**Returns**: `StorageSet`

Returns a storage set representing the object.

#### isinstance(prototype)

**Returns**: `bool`

Returns whether the object inherits from the specified object prototype.

**Parameters**:
- `prototype` (str): The prototype name

## Object Properties

### Basic Information

#### name
**Type**: `str`  
The object's name (e.g., "a longsword").

#### desc
**Type**: `str`  
The object's verbose description when looked at.

#### rdesc
**Type**: `str`  
The object's description when seen in a room (e.g., "a longsword is here, gleaming in the sun").

#### keywords
**Type**: `str`  
Comma-separated list of keywords for referencing the object.

### Multiple Item Names

#### mname
**Type**: `str`  
The object's name for describing packs (e.g., "a stack of %d linen towels"). The number should be replaced by %d or omitted.

#### mdesc
**Type**: `str`  
The equivalent of `mname` for room descriptions.

### Physical Properties

#### weight
**Type**: `float`  
The object's weight including contents. When setting, sets raw weight (minus contents).

#### weight_raw
**Type**: `float`  
The object's weight excluding contents.

#### hidden
**Type**: `int`  
Integer value representing how hard this object is to see.

### Location

#### room
**Type**: `PyRoom`  
The room this object is currently in, or None.

#### carrier
**Type**: `PyChar`  
The character whose inventory this object is in, or None.

#### container
**Type**: `PyObj`  
The container this object is currently in, or None.

#### wearer
**Type**: `PyChar`  
The character who is currently wearing this object, or None.

### Contents

#### contents
**Type**: `list` (read-only)  
List of other objects contained within this one. Immutable.

#### objs
**Type**: `list` (read-only)  
Alias for `contents`.

#### chars
**Type**: `list` (read-only)  
List of characters currently sitting/riding this object (for furniture). Immutable.

### Container Properties

#### container_capacity
**Type**: `float`  
The maximum amount of weight a container can hold.

#### container_is_closable
**Type**: `bool`  
True if the container can be closed.

#### container_is_closed
**Type**: `bool`  
True if the container is closed.

#### container_is_locked
**Type**: `bool`  
True if the container is locked.

#### container_key
**Type**: `str`  
An object prototype that acts as a key for this container.

#### container_pick_diff
**Type**: `int`  
Integer representing how difficult the container's lock is to pick.

### Worn Item Properties

#### worn_type
**Type**: `str`  
The type of worn item this is.

#### worn_locs
**Type**: `str` (read-only)  
The position names this worn type must be equipped to.

### Furniture Properties

#### furniture_type
**Type**: `str`  
The type of furniture: 'at' or 'on' (e.g., tables vs. couches).

#### furniture_capacity
**Type**: `int`  
The number of characters a furniture object can accommodate.

### Portal Properties

#### portal_dest
**Type**: `str`  
String key specifying the destination of the portal. Can be set by string or actual room.

#### portal_enter_mssg
**Type**: `str`  
Message shown to the destination room when a character enters the portal.

#### portal_leave_mssg
**Type**: `str`  
Message shown to a room after a character leaves it via the portal.

### Identity and Inheritance

#### uid
**Type**: `int` (read-only)  
The object's unique identification number.

#### prototypes
**Type**: `str` (read-only)  
Comma-separated list of prototypes this object inherits from.

#### bits
**Type**: `str`  
Comma-separated list of bits currently toggled for this object.

### Time Information

#### age
**Type**: `int` (read-only)  
The difference between the object's creation time and current system time.

#### birth
**Type**: `int` (read-only)  
The object's creation time (system time).

## Module Functions (EFuns)

### Object Management

#### load_obj(prototype, where=None, equip_to='')

**Returns**: `PyObj`

Generates a new object from the specified prototype.

**Parameters**:
- `prototype` (str): The object prototype name
- `where` (PyRoom, PyChar, or PyObj, optional): Where to place the object
- `equip_to` (str, optional): Comma-separated list of bodypart names for equipment

**Example**:
```python
import obj, char, room

# Create object in room
tavern = room.Room("tavern")
table = obj.load_obj("wooden_table", tavern)

# Create object in character's inventory
player = char.Char()
sword = obj.load_obj("longsword", player)

# Create and equip object
armor = obj.load_obj("chainmail", player, "torso")
```

#### obj_list()

**Returns**: `list`

Returns a list containing every object in the game.

**Example**:
```python
import obj

all_objects = obj.obj_list()
for object in all_objects:
    print(f"Object: {object.name} (UID: {object.uid})")
```

#### count_objs(keyword, loc=None)

**Returns**: `int`

Counts how many occurrences of an object with the specified keyword, UID, or prototype exist at a location.

**Parameters**:
- `keyword` (str): The keyword, UID, or prototype to search for
- `loc` (PyRoom, PyChar, PyObj, or None): Location to search (None = entire MUD)

**Example**:
```python
import obj, room

# Count swords in a specific room
armory = room.Room("armory")
sword_count = obj.count_objs("sword", armory)

# Count all gold coins in the entire MUD
gold_count = obj.count_objs("gold_coin")
```

#### read(storage_set)

**Returns**: `PyObj`

Reads and returns an object from a storage set.

**Parameters**:
- `storage_set` (StorageSet): The storage set to read from

### Deprecated Functions

#### find_obj(...)

**Deprecated**: Use `mud.parse_args` instead.

#### find_obj_key(...)

**Deprecated**: Use `mud.parse_args` instead.

## Usage Patterns

### Creating and Managing Containers

```python
import obj, char

def create_treasure_chest():
    """Create a locked treasure chest with contents"""
    chest = obj.load_obj("treasure_chest")
    
    # Set container properties
    chest.name = "an ornate treasure chest"
    chest.desc = "This chest is made of dark oak and bound with iron. Intricate carvings cover its surface."
    chest.container_capacity = 100.0
    chest.container_is_closable = True
    chest.container_is_closed = True
    chest.container_is_locked = True
    chest.container_key = "brass_key"
    chest.container_pick_diff = 20
    
    # Add treasure inside
    gold = obj.load_obj("gold_coins", chest)
    gold.setvar("amount", 500)
    
    gem = obj.load_obj("ruby", chest)
    gem.name = "a flawless ruby"
    
    return chest

# Usage
chest = create_treasure_chest()
```

### Equipment System

```python
import obj, char

def equip_character_set(character, equipment_dict):
    """Equip a character with a complete set of gear"""
    for slot, item_proto in equipment_dict.items():
        if item_proto:
            item = obj.load_obj(item_proto)
            if character.equip(item, slot):
                print(f"Equipped {item.name} to {slot}")
            else:
                print(f"Failed to equip {item.name}")
                item.fromall()  # Clean up failed equipment

# Usage
knight_equipment = {
    "torso": "plate_armor",
    "head": "great_helm",
    "right_hand": "longsword",
    "left_hand": "kite_shield",
    "feet": "steel_boots"
}

knight = char.load_mob("knight", room)
equip_character_set(knight, knight_equipment)
```

### Furniture and Interactive Objects

```python
import obj, room

def create_interactive_furniture(room_key, furniture_type="chair"):
    """Create furniture with special interactions"""
    target_room = room.Room(room_key)
    
    if furniture_type == "chair":
        chair = obj.load_obj("wooden_chair", target_room)
        chair.furniture_type = "on"
        chair.furniture_capacity = 1
        chair.desc = "A comfortable wooden chair with a padded seat."
        
        # Add special interaction
        def sit_message(owner, data, arg):
            if owner.chars:
                for ch in owner.chars:
                    ch.send("The chair creaks softly as you settle into it.")
        
        chair.attach("sit_trigger")
        
    elif furniture_type == "table":
        table = obj.load_obj("wooden_table", target_room)
        table.furniture_type = "at"
        table.furniture_capacity = 4
        table.desc = "A sturdy oak table with room for several people."
        
        # Add container functionality for items on the table
        table.settype("container")
        table.container_capacity = 50.0
    
    return furniture

# Usage
tavern_chair = create_interactive_furniture("tavern", "chair")
tavern_table = create_interactive_furniture("tavern", "table")
```

### Portal Objects

```python
import obj, room

def create_magical_portal(from_room_key, to_room_key, portal_name="magical portal"):
    """Create a portal object for transportation"""
    from_room = room.Room(from_room_key)
    to_room = room.Room(to_room_key)
    
    portal = obj.load_obj("portal_base", from_room)
    portal.name = f"a {portal_name}"
    portal.desc = f"A shimmering {portal_name} hovers in the air, crackling with magical energy."
    portal.keywords = "portal,magical,gateway"
    
    # Set portal properties
    portal.settype("portal")
    portal.portal_dest = to_room_key
    portal.portal_enter_mssg = f"emerges from the {portal_name}"
    portal.portal_leave_mssg = f"steps into the {portal_name} and vanishes"
    
    # Add extra descriptions
    portal.edesc("energy,magic,crackling", 
        "Magical energy dances around the portal's edges, creating an otherworldly display.")
    
    return portal

# Create bidirectional portals
wizard_tower = "wizard_tower"
elemental_plane = "plane_of_fire"

portal1 = create_magical_portal(wizard_tower, elemental_plane, "fire portal")
portal2 = create_magical_portal(elemental_plane, wizard_tower, "return portal")
```

### Object Transformation System

```python
import obj, event

def create_transforming_object(base_proto, transform_proto, trigger_condition, delay=10):
    """Create an object that transforms under certain conditions"""
    base_obj = obj.load_obj(base_proto)
    
    def check_transform(owner, data, arg):
        """Check if transformation conditions are met"""
        base_obj, transform_proto, condition = data
        
        if not base_obj or not base_obj.room:
            return  # Object no longer exists or isn't in a room
        
        # Check condition (simplified example)
        if condition == "moonlight" and base_obj.room.terrain == "outdoor":
            # Transform the object
            new_obj = obj.load_obj(transform_proto, base_obj.room)
            new_obj.name = f"transformed {base_obj.name}"
            
            # Notify room
            base_obj.room.send(f"The {base_obj.name} shimmers and transforms!")
            
            # Remove old object
            base_obj.fromall()
            
            # Schedule reverse transformation
            event.start_event(new_obj, delay * 2, reverse_transform, 
                            (new_obj, base_proto), "reverse")
        else:
            # Check again later
            event.start_event(None, delay, check_transform, data, arg)
    
    def reverse_transform(owner, data, arg):
        """Transform back to original form"""
        current_obj, original_proto = data
        if current_obj and current_obj.room:
            original = obj.load_obj(original_proto, current_obj.room)
            current_obj.room.send(f"The {current_obj.name} reverts to its original form.")
            current_obj.fromall()
    
    # Start the transformation cycle
    event.start_event(None, delay, check_transform, 
                    (base_obj, transform_proto, trigger_condition), "transform")
    
    return base_obj

# Usage
werewolf_amulet = create_transforming_object(
    "silver_amulet", 
    "cursed_amulet", 
    "moonlight", 
    30  # Check every 30 seconds
)
```

### Container Management System

```python
import obj

def manage_container_contents(container, action, item=None):
    """Utility for managing container contents"""
    if not container.istype("container"):
        return "This is not a container."
    
    if action == "list":
        if not container.contents:
            return "The container is empty."
        
        items = []
        for item in container.contents:
            items.append(item.name)
        return f"Contents: {', '.join(items)}"
    
    elif action == "add" and item:
        if container.container_is_closed:
            return "The container is closed."
        
        current_weight = sum(obj.weight for obj in container.contents)
        if current_weight + item.weight > container.container_capacity:
            return "The container is too full."
        
        item.container = container
        return f"Added {item.name} to the container."
    
    elif action == "remove" and item:
        if container.container_is_closed:
            return "The container is closed."
        
        if item in container.contents:
            item.fromall()
            return f"Removed {item.name} from the container."
        else:
            return "That item is not in the container."
    
    elif action == "open":
        if not container.container_is_closable:
            return "This container cannot be opened or closed."
        if not container.container_is_closed:
            return "The container is already open."
        if container.container_is_locked:
            return "The container is locked."
        
        container.container_is_closed = False
        return "You open the container."
    
    elif action == "close":
        if not container.container_is_closable:
            return "This container cannot be opened or closed."
        if container.container_is_closed:
            return "The container is already closed."
        
        container.container_is_closed = True
        return "You close the container."
    
    return "Invalid action."

# Usage in commands
def container_command(ch, cmd, arg):
    """Handle container manipulation commands"""
    # This would be integrated with the command system
    pass
```

## OLC Integration and Extra Code

Most object creation and editing in NakedMud is done through the OLC system using commands like `oedit`, `olist`, and `opedit`. Python code is typically added through the **Extra Code** option in object prototypes.

### Using Python in Object Extra Code

When editing an object prototype with `oedit`, you can add Python code in the Extra Code section that executes when the object is created or during events:

```python
# Object Extra Code Example - executed when object loads
import event, hooks, random

def setup_magical_weapon(weapon):
    """Set up special behavior for a magical weapon"""
    
    def weapon_combat_hook(info):
        """Handle combat events when this weapon is used"""
        parsed = hooks.parse_info(info)
        attacker, defender, weapon_used = parsed[0], parsed[1], parsed[2]
        
        if weapon_used == weapon and attacker:
            # 10% chance for special effect
            if random.randint(1, 100) <= 10:
                attacker.send("Your weapon glows with magical energy!")
                attacker.sendaround(f"{attacker.name}'s weapon flares with power!")
                
                # Add bonus damage or special effect
                if defender:
                    defender.send("You feel the sting of magical energy!")
    
    hooks.add("combat_hit", weapon_combat_hook)

def setup_degrading_item(item):
    """Set up an item that degrades over time"""
    
    def degrade_item(owner, data, arg):
        """Gradually degrade the item"""
        if not item or not hasattr(item, 'room') and not hasattr(item, 'carrier'):
            return  # Item no longer exists or isn't in game
        
        # Get current condition
        condition = item.getvar("condition") or 100
        condition -= random.randint(1, 5)
        item.setvar("condition", condition)
        
        # Update item description based on condition
        if condition > 75:
            condition_desc = "excellent"
        elif condition > 50:
            condition_desc = "good"
        elif condition > 25:
            condition_desc = "worn"
        else:
            condition_desc = "poor"
        
        # Update the item's description
        base_name = item.getvar("base_name") or item.name
        item.name = f"{base_name} ({condition_desc} condition)"
        
        if condition <= 0:
            # Item breaks
            if item.carrier:
                item.carrier.send(f"Your {base_name} crumbles to dust!")
            elif item.room:
                item.room.send(f"The {base_name} crumbles to dust!")
            
            # Remove the item
            import mud
            mud.extract(item)
        else:
            # Schedule next degradation
            delay = random.randint(3600, 7200)  # 1-2 hours
            event.start_event(item, delay, degrade_item, None, "degrade")
    
    # Initialize condition if not set
    if not item.hasvar("condition"):
        item.setvar("condition", 100)
        item.setvar("base_name", item.name)
    
    # Start degradation cycle
    initial_delay = random.randint(1800, 3600)  # 30-60 minutes
    event.start_event(item, initial_delay, degrade_item, None, "degrade")

# Execute setup when object loads
setup_magical_weapon(me)  # 'me' refers to the current object in Extra Code
setup_degrading_item(me)
```

### Interactive Object Prototypes

Objects created with `oedit` can include sophisticated interaction systems:

```python
# Example: Magical crystal with multiple uses
import mud, event, random

def setup_magic_crystal(crystal):
    """Set up a magical crystal with various powers"""
    
    # Initialize crystal properties
    if not crystal.hasvar("charges"):
        crystal.setvar("charges", 10)
        crystal.setvar("last_used", 0)
    
    def crystal_use_hook(info):
        """Handle when someone tries to use the crystal"""
        parsed = hooks.parse_info(info)
        character, command, argument = parsed
        
        if character.carrier == crystal or crystal in character.inv:
            if command == "use" and "crystal" in argument.lower():
                
                charges = crystal.getvar("charges")
                if charges <= 0:
                    character.send("The crystal is drained of power.")
                    return
                
                # Check cooldown (5 minutes between uses)
                import time
                current_time = int(time.time())
                last_used = crystal.getvar("last_used")
                
                if current_time - last_used < 300:
                    remaining = 300 - (current_time - last_used)
                    character.send(f"The crystal needs {remaining} more seconds to recharge.")
                    return
                
                # Use the crystal
                crystal.setvar("charges", charges - 1)
                crystal.setvar("last_used", current_time)
                
                # Random magical effect
                effect = random.choice(["heal", "teleport", "light", "detect"])
                
                if effect == "heal":
                    character.send("The crystal glows warmly, healing your wounds!")
                    # Add healing logic here
                elif effect == "teleport":
                    character.send("The crystal flashes and you feel disoriented!")
                    # Add teleport logic here
                elif effect == "light":
                    character.send("The crystal blazes with brilliant light!")
                    character.room.send(f"{character.name} is surrounded by brilliant light!")
                elif effect == "detect":
                    character.send("The crystal reveals hidden things...")
                    # Add detection logic here
                
                # Update crystal description
                remaining_charges = crystal.getvar("charges")
                if remaining_charges > 5:
                    crystal.desc = "A brilliant crystal pulsing with magical energy."
                elif remaining_charges > 2:
                    crystal.desc = "A crystal with dimming magical energy."
                else:
                    crystal.desc = "A nearly drained crystal with faint magical energy."
    
    hooks.add("player_command", crystal_use_hook)

def setup_container_behavior(container):
    """Set up special container behavior"""
    
    def container_interaction_hook(info):
        """Handle container interactions"""
        parsed = hooks.parse_info(info)
        character, obj, action = parsed
        
        if obj == container:
            if action == "open":
                # Check if container is locked with a puzzle
                if container.container_is_locked:
                    character.send("The container is sealed with a magical lock.")
                    character.send("You notice symbols that might be a puzzle...")
                    
                    # Start puzzle mini-game
                    def puzzle_prompt(sock):
                        sock.send_raw("Enter the magic word: ")
                    
                    def puzzle_handler(sock, input_text):
                        if input_text.strip().lower() == "mellon":  # LOTR reference
                            container.container_is_locked = False
                            character.send("The magical lock dissolves!")
                            character.room.send(f"{character.name} solves the puzzle!")
                        else:
                            character.send("That's not the right word.")
                        sock.pop_ih()  # Remove input handler
                    
                    if character.socket:
                        character.socket.push_ih(puzzle_handler, puzzle_prompt)
    
    hooks.add("obj_interact", container_interaction_hook)

# Execute setup when object loads
setup_magic_crystal(me)
setup_container_behavior(me)
```

### Working with OLC Commands

- **`oedit <obj_key>`** - Edit or create an object prototype
- **`olist [zone]`** - List object prototypes in a zone
- **`opedit <obj_key>`** - Edit object programs (triggers)
- **`load obj <obj_key>`** - Load an object for testing

The Python code in object Extra Code sections has access to:
- **`me`** - The current object
- All object properties and methods
- Full module import capabilities
- Event system for timed behaviors
- Hook system for responding to interactions

### Item Type Integration

Objects can be assigned item types through `oedit`, and the Extra Code can work with these:

```python
# Example: Weapon type with special abilities
if me.istype("weapon"):
    weapon_data = me.get_type_data("weapon")
    if weapon_data:
        # Access weapon-specific properties
        damage = weapon_data.get("damage", 10)
        weapon_type = weapon_data.get("type", "sword")
        
        # Set up type-specific behavior
        if weapon_type == "magic_sword":
            setup_magical_weapon(me)
```

## See Also

- [char Module](char.md) - Character manipulation for equipment
- [room Module](room.md) - Room management for object placement
- [mudsys Module](mudsys.md) - Core system functions
- [auxiliary Module](auxiliary.md) - Auxiliary data system
- [olc Module](olc.md) - Online creation system
- [hooks Module](hooks.md) - Hook system for object interactions
- [event Module](event.md) - Event system for timed object behaviors
- [Core Concepts: Prototypes](../../core-concepts/prototypes.md)
- [Tutorials: Creating Objects](../../tutorials/creating-objects.md)