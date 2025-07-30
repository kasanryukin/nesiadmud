---
layout: default
title: char Module
parent: Modules
grand_parent: API Reference
nav_order: 6
---

# char Module

The `char` module provides the Python wrapper for characters and utilities for searching, storing, and generating NPCs from mob prototypes. It contains both the PyChar class (EObj) and utility functions (EFuns) for character management.

**Module Type**: Core EFuns (External Functions) + EObjs (External Objects)  
**Import**: `import char`

## Overview

The char module is central to character-based operations in NakedMud, providing:
- Character creation and manipulation
- NPC generation from prototypes
- Character searching and listing
- Equipment and inventory management
- Communication and messaging systems
- Action and trigger systems

## PyChar Class (EObj)

The `Char` class represents both player characters and NPCs in the game world.

### Constructor

#### Char()

Creates a new character instance. Characters are typically created through other means (player login, NPC generation) rather than direct instantiation.

### Core Methods

#### act(command)

**Returns**: `None`

Simulates a character typing in a command, processing it through the command system.

**Parameters**:
- `command` (str): The command string to execute

**Example**:
```python
import char

character = char.Char()
character.act("look")
character.act("say Hello, world!")
character.act("north")
```

#### send(mssg, dict=None, newline=True)

**Returns**: `None`

Sends a message to the character. Messages can contain embedded scripts using `[` and `]` brackets.

**Parameters**:
- `mssg` (str): The message to send
- `dict` (dict, optional): Variable dictionary for script evaluation
- `newline` (bool, optional): Whether to append a newline (default: True)

**Example**:
```python
import char

character = char.Char()

# Simple message
character.send("Welcome to the game!")

# Message with script
character.send("Hello, [me.name]!")

# Message with custom variables
vars = {'target': target_char, 'damage': 25}
character.send("You hit [target.name] for [damage] damage!", vars)
```

#### send_raw(mssg)

**Returns**: `None`

Sends a message to the character with no newline appended.

**Parameters**:
- `mssg` (str): The message to send

#### page(text)

**Returns**: `None`

Sends text to the character in paginated form, useful for helpfiles and large blocks of text.

**Parameters**:
- `text` (str): The text to paginate

#### sendaround(mssg, dict=None, cansee_only=False, newline=True)

**Returns**: `None`

Sends a message to everyone in the character's room except the character.

**Parameters**:
- `mssg` (str): The message to send
- `dict` (dict, optional): Variable dictionary for script evaluation
- `cansee_only` (bool, optional): Only send to characters who can see this character
- `newline` (bool, optional): Whether to append a newline

**Example**:
```python
import char

character = char.Char()

# Simple room message
character.sendaround("Bob waves hello.")

# Message with scripts - 'me' refers to character, 'ch' refers to each recipient
character.sendaround("[me.name] says to [ch.name], 'Hello there!'")
```

### Visibility and Perception

#### cansee(thing)

**Returns**: `bool`

Returns whether the character can see the specified object, exit, or other character.

**Parameters**:
- `thing` (PyChar, PyObj, or PyExit): The thing to check visibility for

#### see_as(thing)

**Returns**: `str`

Returns the name by which the character sees the specified object, exit, or other character.

**Parameters**:
- `thing` (PyChar, PyObj, or PyExit): The thing to get the name for

**Example**:
```python
import char

observer = char.Char()
target = char.Char()

if observer.cansee(target):
    name = observer.see_as(target)
    observer.send(f"You see {name}.")
```

### Equipment and Inventory

#### equip(obj, positions=None, forced=False)

**Returns**: `bool`

Attempts to equip an object to the character's body.

**Parameters**:
- `obj` (PyObj): The object to equip
- `positions` (str, optional): Comma-separated list of position names or types
- `forced` (bool, optional): Allow non-worn objects or non-default positions

**Example**:
```python
import char, obj

character = char.Char()
sword = obj.load_obj("longsword")

# Equip to default positions
if character.equip(sword):
    character.send("You equip the sword.")

# Equip to specific positions
shield = obj.load_obj("shield")
character.equip(shield, "left_hand")
```

#### get_equip(bodypart)

**Returns**: `PyObj` or `None`

Returns the object currently equipped to the specified bodypart.

**Parameters**:
- `bodypart` (str): The bodypart name

#### get_slots(obj)

**Returns**: `str`

Returns a comma-separated list of bodypart names currently occupied by the object.

**Parameters**:
- `obj` (PyObj): The equipped object

#### get_slot_types(obj)

**Returns**: `list`

Returns a list of bodypart types currently occupied by the object.

**Parameters**:
- `obj` (PyObj): The equipped object

### Actions and Timing

#### startAction(delay, on_complete, on_interrupt=None, data=None, arg='')

**Returns**: `None`

Begins a new delayed action for the character.

**Parameters**:
- `delay` (float): Delay in seconds
- `on_complete` (function): Function called when action completes
- `on_interrupt` (function, optional): Function called if action is interrupted
- `data` (any, optional): Data to pass to the functions
- `arg` (str, optional): String argument to pass to the functions

**Example**:
```python
import char

def spell_complete(ch, data, arg):
    ch.send(f"You finish casting {arg}!")
    # Apply spell effects here

def spell_interrupted(ch, data, arg):
    ch.send(f"Your {arg} spell is interrupted!")

character = char.Char()
character.startAction(3.0, spell_complete, spell_interrupted, None, "fireball")
```

#### interrupt()

**Returns**: `None`

Cancels any action the character is currently taking.

#### isActing()

**Returns**: `bool`

Returns True if the character is currently taking an action.

### Auxiliary Data and Variables

#### aux(name)

**Returns**: Auxiliary data object or `None`

Alias for `getAuxiliary(name)`. Returns the character's auxiliary data of the specified name.

**Parameters**:
- `name` (str): The auxiliary data name

#### getAuxiliary(name)

**Returns**: Auxiliary data object or `None`

Returns the character's auxiliary data of the specified name.

**Parameters**:
- `name` (str): The auxiliary data name

#### setvar(name, val)

**Returns**: `None`

Sets a special variable for the character. Intended for scripts and triggers.

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

Returns True if the character has the specified special variable.

**Parameters**:
- `name` (str): The variable name

#### deletevar(name)

**Returns**: `None`

Deletes a special variable from the character.

**Parameters**:
- `name` (str): The variable name

#### delvar(name)

**Returns**: `None`

Alias for `deletevar(name)`.

### Triggers and Scripts

#### attach(trigger)

**Returns**: `None`

Attaches a trigger to the character by key name.

**Parameters**:
- `trigger` (str): The trigger key name

#### detach(trigger)

**Returns**: `None`

Detaches a trigger from the character by key name.

**Parameters**:
- `trigger` (str): The trigger key name

#### do_trigs(type, ch=None, obj=None, room=None, exit=None, cmd=None, arg=None, opts=None)

**Returns**: `None`

Runs triggers of the specified type on the character.

**Parameters**:
- `type` (str): The trigger type
- `ch` (PyChar, optional): Character variable for trigger
- `obj` (PyObj, optional): Object variable for trigger
- `room` (PyRoom, optional): Room variable for trigger
- `exit` (PyExit, optional): Exit variable for trigger
- `cmd` (str, optional): Command variable for trigger
- `arg` (str, optional): Argument variable for trigger
- `opts` (dict, optional): Optional variables dictionary

### Aliases

#### get_alias(name)

**Returns**: `str` or `None`

Returns the character's alias by the specified name.

**Parameters**:
- `name` (str): The alias name

#### set_alias(name, value)

**Returns**: `None`

Sets a character's alias.

**Parameters**:
- `name` (str): The alias name
- `value` (str): The alias value

### Look System

#### append_look(text)

**Returns**: `None`

Adds text to the character's current look buffer.

**Parameters**:
- `text` (str): Text to append

#### clear_look()

**Returns**: `None`

Clears the character's current look buffer.

### Utility Methods

#### copy()

**Returns**: `PyChar`

Returns a copy of the character.

#### store()

**Returns**: `StorageSet`

Returns a storage set representing the character.

#### isinstance(prototype)

**Returns**: `bool`

Returns whether the character inherits from the specified mob prototype.

**Parameters**:
- `prototype` (str): The prototype name

#### isInGroup(usergroup)

**Returns**: `bool`

Returns whether the character belongs to the specified user group.

**Parameters**:
- `usergroup` (str): The user group name

#### hasPrefs(char_prefs)

**Returns**: `bool`

Returns whether the character has any of the specified character preferences.

**Parameters**:
- `char_prefs` (str): Comma-separated list of preferences

### Routines

#### set_routine(routine, repeat=False, checks=None)

**Returns**: `None`

Sets a routine for the character. Routines are sequences of commands or functions.

**Parameters**:
- `routine` (list): List of routine steps
- `repeat` (bool, optional): Whether to repeat the routine
- `checks` (list, optional): List of check functions

**Example**:
```python
import char

def patrol_function(ch):
    ch.act("look")

character = char.Char()
routine = [
    "north",
    "look",
    (5.0, patrol_function),  # 5 second delay, then function
    "south"
]
character.set_routine(routine, repeat=True)
```

## Character Properties

### Basic Information

#### name
**Type**: `str`  
The character's name (e.g., "Grunald the Baker").

#### desc
**Type**: `str`  
The character's verbose description when looked at.

#### rdesc
**Type**: `str`  
The character's description when seen in a room (e.g., "Bob is here, baking a cake").

#### keywords
**Type**: `str`  
Comma-separated list of keywords for referencing the character.

#### race
**Type**: `str`  
The character's race.

#### sex
**Type**: `str`  
The character's sex (male, female, or neutral).

#### gender
**Type**: `str`  
Alias for `sex`.

### Pronouns (Read-only)

#### heshe
**Type**: `str` (read-only)  
Returns 'he', 'she', or 'it' based on character's sex.

#### himher
**Type**: `str` (read-only)  
Returns 'him', 'her', or 'it' based on character's sex.

#### hisher
**Type**: `str` (read-only)  
Returns 'his', 'her', or 'its' based on character's sex.

### Status and State

#### position
**Type**: `str`  
The character's current position (e.g., standing, sleeping, sitting).

#### pos
**Type**: `str`  
Alias for `position`.

#### hidden
**Type**: `int`  
Integer value representing how hidden the character is (default: 0).

#### weight
**Type**: `float`  
Floating-point value representing the character's weight.

### Location and Movement

#### room
**Type**: `PyRoom`  
The current room the character is in. Can be set by room or room key.

#### last_room
**Type**: `PyRoom` (read-only)  
The last room the character was in. None if not previously in a room.

#### on
**Type**: `PyObj`  
The furniture the character is sitting on/at. None if not on furniture.

### Inventory and Equipment

#### inv
**Type**: `list` (read-only)  
Immutable list of objects in the character's inventory.

#### objs
**Type**: `list` (read-only)  
Alias for `inv` to be consistent with room and object contents.

#### eq
**Type**: `list` (read-only)  
Immutable list of the character's worn equipment.

#### bodyparts
**Type**: `list` (read-only)  
Immutable list naming all of the character's bodyparts.

### Character Type and Identity

#### is_npc
**Type**: `bool` (read-only)  
True if character is an NPC, False otherwise.

#### is_pc
**Type**: `bool` (read-only)  
Negation of `is_npc`.

#### uid
**Type**: `int` (read-only)  
The character's unique identification number.

### Prototypes and Inheritance

#### mob_class
**Type**: `str` (read-only)  
The main prototype the mobile inherits from.

#### prototypes
**Type**: `str` (read-only)  
Comma-separated list of prototypes the mobile inherits from.

### Networking

#### socket
**Type**: `PySocket` (read-only)  
The current socket this character is attached to. None if no socket exists.

#### sock
**Type**: `PySocket` (read-only)  
Alias for `socket`.

### Permissions

#### user_groups
**Type**: `str` (read-only)  
Comma-separated list of user groups the character belongs to.

### Time Information

#### age
**Type**: `int` (read-only)  
The difference between the character's creation time and current system time.

#### birth
**Type**: `int` (read-only)  
The character's creation time (system time).

### Aliases and Preferences

#### aliases
**Type**: `list` (read-only)  
List of all aliases the character currently has defined.

### Multiple Names

#### mname
**Type**: `str`  
The character's name for describing packs (e.g., "a horde of %d mosquitos").

#### mdesc
**Type**: `str`  
The equivalent of `mname` for room descriptions.

### Editor Integration

#### notepad
**Type**: `object` (read-only)  
Returns the character's notepad, if any.

#### look_buf
**Type**: `str`  
When characters look at something, the description is copied here for processing.

## Module Functions (EFuns)

### Character Management

#### char_list()

**Returns**: `list`

Returns a list of every character currently in the game.

**Example**:
```python
import char

all_chars = char.char_list()
for character in all_chars:
    print(f"Character: {character.name}")
```

#### load_mob(proto, room, pos='standing')

**Returns**: `PyChar`

Generates a new mobile from the specified prototype and adds it to the given room.

**Parameters**:
- `proto` (str): The mob prototype name
- `room` (PyRoom): The room to place the mob in
- `pos` (str, optional): The initial position (default: 'standing')

**Example**:
```python
import char, room

target_room = room.get_room("town_square")
guard = char.load_mob("town_guard", target_room)
guard.send("A guard materializes!")
```

#### count_mobs(keyword, loc=None)

**Returns**: `int`

Counts how many occurrences of a mobile with the specified keyword, UID, or prototype exist at a location.

**Parameters**:
- `keyword` (str): The keyword, UID, or prototype to search for
- `loc` (PyRoom, PyObj, or None): Location to search (None = entire MUD)

**Example**:
```python
import char, room

# Count guards in a specific room
town_square = room.get_room("town_square")
guard_count = char.count_mobs("guard", town_square)

# Count all orcs in the entire MUD
orc_count = char.count_mobs("orc")
```

#### is_abstract(proto)

**Returns**: `bool`

Returns whether a specified mob prototype is abstract. Also returns True if the prototype doesn't exist.

**Parameters**:
- `proto` (str): The prototype name

**Example**:
```python
import char

if not char.is_abstract("town_guard"):
    # Can create instances of this prototype
    pass
```

#### read(storage_set)

**Returns**: `PyChar`

Reads and returns a character from a storage set.

**Parameters**:
- `storage_set` (StorageSet): The storage set to read from

### Deprecated Functions

#### find_char_key(...)

**Deprecated**: Use `mud.parse_args` instead.

## Usage Patterns

### Creating and Managing NPCs

```python
import char, room

# Load a room and create an NPC
tavern = room.get_room("tavern")
bartender = char.load_mob("bartender", tavern)

# Customize the NPC
bartender.name = "Gruff the Bartender"
bartender.rdesc = "Gruff stands behind the bar, cleaning glasses."

# Set up a routine
routine = [
    "say Welcome to my tavern!",
    (10.0, "emote wipes down the bar"),
    "say What can I get you?"
]
bartender.set_routine(routine, repeat=True)
```

### Character Communication

```python
import char

def broadcast_message(message):
    """Send a message to all characters in the game"""
    for character in char.char_list():
        if character.socket:  # Only send to connected players
            character.send(message)

# Usage
broadcast_message("Server restart in 5 minutes!")
```

### Equipment Management

```python
import char, obj

def equip_character_set(character, equipment_list):
    """Equip a character with a set of items"""
    for item_proto in equipment_list:
        item = obj.load_obj(item_proto)
        if character.equip(item):
            character.send(f"You equip {item.name}.")
        else:
            character.send(f"You can't equip {item.name}.")
            item.fromall()  # Remove item if can't equip

# Usage
guard_equipment = ["chainmail", "longsword", "shield"]
guard = char.load_mob("guard", room)
equip_character_set(guard, guard_equipment)
```

### Action System

```python
import char

def start_meditation(character, duration=30):
    """Start a meditation action"""
    def meditation_complete(ch, data, arg):
        ch.send("You finish your meditation feeling refreshed.")
        ch.position = "standing"
    
    def meditation_interrupted(ch, data, arg):
        ch.send("Your meditation is interrupted!")
        ch.position = "standing"
    
    character.position = "sitting"
    character.send("You begin to meditate...")
    character.startAction(duration, meditation_complete, meditation_interrupted)

# Usage
player = char.Char()  # Assume this is a real player
start_meditation(player, 60)  # 60 second meditation
```

## OLC Integration and Extra Code

Most NPC (mobile) creation and editing in NakedMud is done through the OLC system using commands like `medit`, `mlist`, and `mpedit`. Python code is typically added through the **Extra Code** option in mob prototypes.

### Using Python in Mob Extra Code

When editing a mob prototype with `medit`, you can add Python code in the Extra Code section that executes when the mob is created or during events:

```python
# Mob Extra Code Example - executed when mob loads
import event, random, hooks

def setup_mob_behavior(mob):
    """Set up special behavior for this mob"""
    
    def patrol_behavior(owner, data, arg):
        """Make the mob patrol between rooms"""
        if not owner or not owner.room:
            return
        
        # Simple patrol logic
        exits = owner.room.exnames
        if exits:
            direction = random.choice(exits)
            owner.act(direction)
        
        # Schedule next patrol
        delay = random.randint(30, 120)  # 30 seconds to 2 minutes
        event.start_event(owner, delay, patrol_behavior, None, "patrol")
    
    # Start patrol behavior
    if mob.room:  # Only if mob is in a room
        initial_delay = random.randint(10, 30)
        event.start_event(mob, initial_delay, patrol_behavior, None, "patrol")

def setup_combat_hooks(mob):
    """Set up combat-specific behavior"""
    
    def mob_combat_hook(info):
        """Handle combat events for this mob"""
        parsed = hooks.parse_info(info)
        attacker, defender = parsed[0], parsed[1]
        
        if defender == mob:  # This mob is being attacked
            # Special combat behavior
            if mob.hit_points < mob.max_hit_points * 0.3:  # Below 30% health
                mob.act("say You'll never defeat me!")
                # Maybe cast a spell or call for help
    
    hooks.add("combat_hit", mob_combat_hook)

# Execute setup when mob loads
setup_mob_behavior(me)  # 'me' refers to the current mob in Extra Code
setup_combat_hooks(me)
```

### NPC Prototype Integration

Mob prototypes created with `medit` can include sophisticated Python behavior:

```python
# Example: Shopkeeper with dynamic pricing
import mud, obj

def setup_shopkeeper_behavior(shopkeeper):
    """Set up shopkeeper-specific behavior"""
    
    # Store base prices in mob variables
    if not shopkeeper.hasvar("base_prices_set"):
        shopkeeper.setvar("sword_price", 100)
        shopkeeper.setvar("shield_price", 75)
        shopkeeper.setvar("potion_price", 25)
        shopkeeper.setvar("base_prices_set", 1)
    
    def adjust_prices_hourly(owner, data, arg):
        """Adjust prices based on time of day"""
        if not owner:
            return
        
        hour = mud.get_hour()
        
        # Higher prices during peak hours (evening)
        if 18 <= hour <= 22:
            price_multiplier = 1.2
            owner.setvar("price_message", "Prices are higher during peak hours.")
        # Lower prices during off-hours (night/early morning)
        elif hour <= 6 or hour >= 23:
            price_multiplier = 0.8
            owner.setvar("price_message", "Night-time discount prices!")
        else:
            price_multiplier = 1.0
            owner.setvar("price_message", "Standard prices.")
        
        # Update current prices
        base_sword = 100
        base_shield = 75
        base_potion = 25
        
        owner.setvar("current_sword_price", int(base_sword * price_multiplier))
        owner.setvar("current_shield_price", int(base_shield * price_multiplier))
        owner.setvar("current_potion_price", int(base_potion * price_multiplier))
        
        # Schedule next price update
        event.start_event(owner, 3600, adjust_prices_hourly, None, "price_update")
    
    # Start price adjustment system
    adjust_prices_hourly(shopkeeper, None, None)

def add_shopkeeper_commands(shopkeeper):
    """Add shopkeeper-specific commands"""
    
    def list_command(ch, cmd, arg):
        """List items for sale"""
        if ch.room != shopkeeper.room:
            return
        
        ch.send(f"{shopkeeper.name} says, 'Here's what I have for sale:'")
        ch.send(f"Sword: {shopkeeper.getvar('current_sword_price')} gold")
        ch.send(f"Shield: {shopkeeper.getvar('current_shield_price')} gold")
        ch.send(f"Potion: {shopkeeper.getvar('current_potion_price')} gold")
        
        price_msg = shopkeeper.getvar("price_message")
        if price_msg:
            ch.send(f"{shopkeeper.name} says, '{price_msg}'")
    
    def buy_command(ch, cmd, arg):
        """Handle buying items"""
        if ch.room != shopkeeper.room:
            return
        
        if not arg:
            ch.send(f"{shopkeeper.name} says, 'What would you like to buy?'")
            return
        
        item = arg.lower().strip()
        price_var = f"current_{item}_price"
        
        if not shopkeeper.hasvar(price_var):
            ch.send(f"{shopkeeper.name} says, 'I don't sell that.'")
            return
        
        price = shopkeeper.getvar(price_var)
        if ch.gold < price:
            ch.send(f"{shopkeeper.name} says, 'You need {price} gold for that.'")
            return
        
        # Create and give the item
        new_item = obj.load_obj(item, ch)
        if new_item:
            ch.gold -= price
            ch.send(f"You buy {new_item.name} for {price} gold.")
            shopkeeper.send(f"{ch.name} buys {new_item.name}.")
        else:
            ch.send(f"{shopkeeper.name} says, 'Sorry, I'm out of stock.'")
    
    # Add commands to the shopkeeper's room
    if shopkeeper.room:
        shopkeeper.room.add_cmd("list", "l", list_command, "player")
        shopkeeper.room.add_cmd("buy", "b", buy_command, "player")

# Execute setup when mob loads
setup_shopkeeper_behavior(me)
add_shopkeeper_commands(me)
```

### Working with OLC Commands

- **`medit <mob_key>`** - Edit or create a mob prototype
- **`mlist [zone]`** - List mob prototypes in a zone  
- **`mpedit <mob_key>`** - Edit mob programs (triggers)
- **`load mob <mob_key>`** - Load a mob for testing

The Python code in mob Extra Code sections has access to:
- **`me`** - The current mob object
- All character properties and methods
- Full module import capabilities
- Event system for timed behaviors
- Hook system for responding to game events

## See Also

- [room Module](room.md) - Room management and PyRoom class
- [obj Module](obj.md) - Object management and PyObj class
- [mudsys Module](mudsys.md) - Core system functions
- [auxiliary Module](auxiliary.md) - Auxiliary data system
- [olc Module](olc.md) - Online creation system
- [hooks Module](hooks.md) - Hook system for mob behaviors
- [event Module](event.md) - Event system for timed actions
- [Core Concepts: Prototypes](../../core-concepts/prototypes.md)
- [Tutorials: Creating NPCs](../../tutorials/creating-npcs.md)