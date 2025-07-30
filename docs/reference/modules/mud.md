---
layout: default
title: mud Module
parent: Modules
grand_parent: API Reference
nav_order: 11
---

# mud Module

The `mud` module provides miscellaneous MUD utilities and system functions. It contains a collection of general-purpose functions for text processing, global variables, time management, messaging, and various utility operations.

**Module Type**: Core EFuns (External Functions)  
**Import**: `import mud`

## Overview

The mud module handles:
- Text formatting and expansion
- Global variable management
- In-game time and date functions
- Message formatting and sending
- Object extraction and cleanup
- Argument parsing and validation
- Race and system information
- Logging and debugging utilities

## Text Processing

### expand_text(text, dict={}, newline=False)

**Returns**: `str`

Takes text with embedded Python statements and expands them. Statements are embedded between `[` and `]` brackets.

**Parameters**:
- `text` (str): Text containing embedded Python statements
- `dict` (dict, optional): Variables to add to the scripting environment
- `newline` (bool, optional): Whether to add newlines for readability

**Example**:
```python
import mud

# Simple variable expansion
text = "Hello, [name]!"
result = mud.expand_text(text, {'name': 'World'})
print(result)  # "Hello, World!"

# Complex expressions
text = "You have [gold] gold coins ([gold * 2] silver equivalent)."
result = mud.expand_text(text, {'gold': 50})
print(result)  # "You have 50 gold coins (100 silver equivalent)."

# Using character data
text = "Welcome, [ch.name]! You are level [ch.level]."
result = mud.expand_text(text, {'ch': character})
```

### format_string(text, indent=True, width=80)

**Returns**: `str`

Formats a block of text to be of the specified width, with optional paragraph indentation.

**Parameters**:
- `text` (str): The text to format
- `indent` (bool, optional): Whether to indent paragraphs (default: True)
- `width` (int, optional): Maximum line width (default: 80)

**Example**:
```python
import mud

long_text = "This is a very long line of text that needs to be wrapped to fit within the specified width limit for better readability."

formatted = mud.format_string(long_text, indent=True, width=60)
print(formatted)
# Output will be wrapped to 60 characters with paragraph indentation
```

## Global Variables

### set_global(name, val)

**Returns**: `None`

Sets a non-persistent global variable. The value can be of any type.

**Parameters**:
- `name` (str): The variable name
- `val` (any): The value to store

### get_global(name)

**Returns**: `any` or `None`

Returns a non-persistent global variable, or None if it doesn't exist.

**Parameters**:
- `name` (str): The variable name

### erase_global(name)

**Returns**: `None`

Deletes a value from the global variable table.

**Parameters**:
- `name` (str): The variable name to delete

**Example**:
```python
import mud

# Set global variables
mud.set_global("server_start_time", time.time())
mud.set_global("maintenance_mode", False)
mud.set_global("player_count", 0)

# Retrieve global variables
start_time = mud.get_global("server_start_time")
maintenance = mud.get_global("maintenance_mode")

# Delete a global variable
mud.erase_global("temporary_data")

# Global variables are useful for:
# - Server-wide settings
# - Temporary data sharing between scripts
# - Event coordination
# - Statistics tracking
```

## Time and Date Functions

### get_time()

**Returns**: `str`

Returns the current time of day as a string (morning, afternoon, evening, night).

### get_hour()

**Returns**: `int`

Returns the current in-game hour of day (0-23).

### is_morning()

**Returns**: `bool`

Returns True if it is currently morning in the game world.

### is_afternoon()

**Returns**: `bool`

Returns True if it is currently afternoon in the game world.

### is_evening()

**Returns**: `bool`

Returns True if it is currently evening in the game world.

### is_night()

**Returns**: `bool`

Returns True if it is currently night in the game world.

**Example**:
```python
import mud

# Get current game time
current_time = mud.get_time()
current_hour = mud.get_hour()

print(f"It is {current_time} (hour {current_hour})")

# Time-based logic
if mud.is_night():
    # Nighttime events
    spawn_nocturnal_creatures()
elif mud.is_morning():
    # Morning events
    open_shops()

# Time-based descriptions
def get_time_description():
    if mud.is_morning():
        return "The morning sun casts long shadows across the land."
    elif mud.is_afternoon():
        return "The afternoon sun beats down warmly."
    elif mud.is_evening():
        return "The evening light begins to fade."
    else:
        return "Darkness blankets the world under a starry sky."
```

## Messaging System

### send(list, mssg, dict=None, newline=True)

**Returns**: `None`

Sends a message to a list of characters. Messages can have scripts embedded using `[` and `]` brackets.

**Parameters**:
- `list` (list): List of characters to send to
- `mssg` (str): The message to send
- `dict` (dict, optional): Variable dictionary for script evaluation
- `newline` (bool, optional): Whether to append newlines

**Example**:
```python
import mud, char

# Get all online players
players = [ch for ch in char.char_list() if ch.socket]

# Send announcement to all players
mud.send(players, "Server announcement: Maintenance in 10 minutes!")

# Send personalized messages
mud.send(players, "Welcome, [ch.name]! You have [ch.gold] gold.")

# Send with custom variables
event_data = {'event_name': 'Dragon Festival', 'reward': '100 gold'}
mud.send(players, "The [event_name] begins! Participate to win [reward]!", event_data)
```

### message(ch, vict, obj, vobj, show_invis, range, mssg)

**Returns**: `None`

Sends a message via the MUD messaging system using advanced expansions.

**Parameters**:
- `ch` (PyChar): The character performing the action
- `vict` (PyChar): The victim/target character
- `obj` (PyObj): The object involved
- `vobj` (PyObj): The victim's object
- `show_invis` (bool): Whether to show invisible characters
- `range` (str): Message range - 'to_room', 'to_char', 'to_vict', or 'to_world'
- `mssg` (str): The message with special expansions

**Example**:
```python
import mud

# Combat message
mud.message(attacker, defender, weapon, None, True, 'to_room',
           "$n attacks $N with $p!")

# The message system will expand:
# $n -> attacker's name (to others) / "You" (to attacker)
# $N -> defender's name
# $p -> weapon's name
```

## Object Management

### extract(thing)

**Returns**: `None`

Extracts an object, character, or room from the game, removing it completely.

**Parameters**:
- `thing` (PyChar, PyObj, or PyRoom): The thing to extract

**Example**:
```python
import mud, obj

# Create a temporary object
temp_obj = obj.load_obj("temporary_item")

# Use it for something...

# Clean up by extracting it
mud.extract(temp_obj)

# The object is now completely removed from the game
```

## Argument Parsing

### parse_args(ch, show_usage_errors, cmd, args, format)

**Returns**: `tuple`

Equivalent to the C parse_args function. Parses command arguments according to a format string.

**Parameters**:
- `ch` (PyChar): The character issuing the command
- `show_usage_errors` (bool): Whether to show usage errors to the character
- `cmd` (str): The command name
- `args` (str): The argument string
- `format` (str): The parsing format

**Example**:
```python
import mud

def give_command(ch, cmd, arg):
    """Give an object to another character"""
    # Parse: give <object> <character>
    parsed = mud.parse_args(ch, True, cmd, arg, "obj.inv ch.room")
    
    if not parsed:
        return  # Error message already shown
    
    obj_to_give, target_char = parsed
    
    if obj_to_give and target_char:
        obj_to_give.carrier = target_char
        ch.send(f"You give {obj_to_give.name} to {target_char.name}.")
        target_char.send(f"{ch.name} gives you {obj_to_give.name}.")
```

## Race System

### is_race(name)

**Returns**: `bool`

Returns True if the string is a valid race name.

**Parameters**:
- `name` (str): The race name to check

### list_races(player_only=False)

**Returns**: `list`

Returns a list of available races.

**Parameters**:
- `player_only` (bool, optional): If True, list only races available to players

**Example**:
```python
import mud

# Check if a race is valid
if mud.is_race("elf"):
    print("Elf is a valid race")

# Get all races
all_races = mud.list_races()
print("Available races:", ", ".join(all_races))

# Get only player races
player_races = mud.list_races(player_only=True)
print("Player races:", ", ".join(player_races))
```

## System Information

### get_greeting()

**Returns**: `str`

Returns the MUD's connection greeting message.

### get_motd()

**Returns**: `str`

Returns the MUD's message of the day.

**Example**:
```python
import mud

# Display system messages
greeting = mud.get_greeting()
motd = mud.get_motd()

print("Greeting:", greeting)
print("MOTD:", motd)
```

## Utility Functions

### ite(logic_statement, if_statement, else_statement=None)

**Returns**: `any`

A functional form of if/then/else. Returns `if_statement` if `logic_statement` is true, otherwise returns `else_statement`.

**Parameters**:
- `logic_statement` (bool): The condition to test
- `if_statement` (any): Value to return if condition is true
- `else_statement` (any, optional): Value to return if condition is false

**Example**:
```python
import mud

# Simple conditional
result = mud.ite(player.level > 10, "experienced", "novice")

# With function calls
message = mud.ite(mud.is_night(), 
                 "The stars shine brightly overhead.",
                 "The sun illuminates the landscape.")

# Nested conditions
status = mud.ite(player.hp > 50,
                mud.ite(player.hp > 80, "healthy", "wounded"),
                "critically injured")
```

### keys_equal(key1, key2)

**Returns**: `bool`

Returns whether two world database keys are equal, relative to the locale (if any) that the current script is running in.

**Parameters**:
- `key1` (str): First key to compare
- `key2` (str): Second key to compare

**Example**:
```python
import mud

# Compare room keys
if mud.keys_equal("tavern", "myzone@tavern"):
    print("Keys refer to the same room")
```

### log_string(mssg)

**Returns**: `None`

Sends a message to the MUD's log file.

**Parameters**:
- `mssg` (str): The message to log

**Example**:
```python
import mud

# Log important events
mud.log_string("Player 'Gandalf' reached level 50")
mud.log_string("Server maintenance completed")

# Log errors
try:
    risky_operation()
except Exception as e:
    mud.log_string(f"Error in risky_operation: {str(e)}")
```

## Deprecated Functions

### generic_find(...)

**Deprecated**: Use `mud.parse_args` instead.

This function has been replaced by the more robust `parse_args` function.

## Usage Patterns

### Dynamic Message System

```python
import mud, char

def create_dynamic_message_system():
    """Create a system for dynamic, context-aware messages"""
    
    def send_contextual_message(characters, base_message, context=None):
        """Send messages that adapt to context"""
        if not context:
            context = {}
        
        # Add time-based context
        context['time_of_day'] = mud.get_time()
        context['hour'] = mud.get_hour()
        
        # Add weather context (example)
        context['weather'] = mud.get_global('current_weather') or 'clear'
        
        # Expand and send
        expanded_message = mud.expand_text(base_message, context)
        mud.send(characters, expanded_message)
    
    return send_contextual_message

# Usage
send_contextual = create_dynamic_message_system()

players = [ch for ch in char.char_list() if ch.socket]
message = "The [weather] [time_of_day] sky stretches overhead. (Hour: [hour])"

send_contextual(players, message)
```

### Global State Management

```python
import mud, event

class GlobalStateManager:
    """Manage global MUD state"""
    
    @staticmethod
    def set_server_state(state, data=None):
        """Set server state with optional data"""
        mud.set_global('server_state', state)
        if data:
            mud.set_global('server_state_data', data)
        mud.log_string(f"Server state changed to: {state}")
    
    @staticmethod
    def get_server_state():
        """Get current server state"""
        return mud.get_global('server_state') or 'normal'
    
    @staticmethod
    def is_maintenance_mode():
        """Check if server is in maintenance mode"""
        return GlobalStateManager.get_server_state() == 'maintenance'
    
    @staticmethod
    def start_maintenance(duration_minutes=30):
        """Start maintenance mode"""
        GlobalStateManager.set_server_state('maintenance', {
            'start_time': time.time(),
            'duration': duration_minutes * 60
        })
        
        # Notify all players
        players = [ch for ch in char.char_list() if ch.socket]
        mud.send(players, f"Server entering maintenance mode for {duration_minutes} minutes.")
        
        # Schedule end of maintenance
        def end_maintenance(owner, data, arg):
            GlobalStateManager.set_server_state('normal')
            remaining_players = [ch for ch in char.char_list() if ch.socket]
            mud.send(remaining_players, "Maintenance complete. Server is back to normal.")
        
        event.start_event(None, duration_minutes * 60, end_maintenance, None, "maintenance_end")

# Usage
state_manager = GlobalStateManager()

# Start maintenance
state_manager.start_maintenance(15)  # 15 minutes

# Check state in other scripts
if state_manager.is_maintenance_mode():
    # Restrict certain operations
    pass
```

### Time-Based Event System

```python
import mud, event

class TimeBasedEvents:
    """Handle events that occur at specific times"""
    
    def __init__(self):
        self.scheduled_events = {}
    
    def schedule_at_time(self, hour, event_func, data=None, daily=False):
        """Schedule an event to occur at a specific hour"""
        event_id = f"time_event_{hour}_{id(event_func)}"
        
        def time_check(owner, event_data, arg):
            current_hour = mud.get_hour()
            target_hour, func, func_data, is_daily = event_data
            
            if current_hour == target_hour:
                # Execute the event
                func(func_data)
                
                if is_daily:
                    # Reschedule for tomorrow (24 hours later)
                    event.start_event(None, 86400, time_check, event_data, arg)
            else:
                # Check again in an hour
                event.start_event(None, 3600, time_check, event_data, arg)
        
        # Start checking
        event_data = (hour, event_func, data, daily)
        event.start_event(None, 60, time_check, event_data, event_id)
        
        self.scheduled_events[event_id] = event_data
    
    def schedule_at_time_of_day(self, time_period, event_func, data=None):
        """Schedule event for morning, afternoon, evening, or night"""
        def time_period_check(owner, event_data, arg):
            period, func, func_data = event_data
            
            current_period = mud.get_time()
            if current_period == period:
                func(func_data)
                # Reschedule for next occurrence (6 hours later)
                event.start_event(None, 21600, time_period_check, event_data, arg)
            else:
                # Check again in an hour
                event.start_event(None, 3600, time_period_check, event_data, arg)
        
        event_data = (time_period, event_func, data)
        event.start_event(None, 60, time_period_check, event_data, f"period_{time_period}")

# Usage
time_events = TimeBasedEvents()

def morning_announcement(data):
    """Morning server announcement"""
    players = [ch for ch in char.char_list() if ch.socket]
    mud.send(players, "Good morning! A new day begins in the realm.")

def midnight_maintenance(data):
    """Midnight maintenance tasks"""
    mud.log_string("Running midnight maintenance tasks")
    # Perform cleanup, backups, etc.

# Schedule events
time_events.schedule_at_time(0, midnight_maintenance, daily=True)  # Midnight daily
time_events.schedule_at_time_of_day("morning", morning_announcement)
```

### Advanced Text Processing

```python
import mud, re

class TextProcessor:
    """Advanced text processing utilities"""
    
    @staticmethod
    def colorize_text(text, color_codes=None):
        """Add color codes to text"""
        if not color_codes:
            color_codes = {
                'red': '\033[31m',
                'green': '\033[32m',
                'yellow': '\033[33m',
                'blue': '\033[34m',
                'reset': '\033[0m'
            }
        
        # Replace color tags with codes
        for color, code in color_codes.items():
            text = text.replace(f'<{color}>', code)
        
        # Ensure reset at end
        if '\033[' in text and not text.endswith(color_codes['reset']):
            text += color_codes['reset']
        
        return text
    
    @staticmethod
    def create_table(headers, rows, width=80):
        """Create a formatted table"""
        if not headers or not rows:
            return ""
        
        # Calculate column widths
        col_count = len(headers)
        col_width = (width - (col_count + 1)) // col_count
        
        # Create header
        header_line = "|" + "|".join(h.center(col_width) for h in headers) + "|"
        separator = "+" + "+".join("-" * col_width for _ in headers) + "+"
        
        # Create rows
        table_rows = []
        for row in rows:
            row_line = "|" + "|".join(str(cell)[:col_width].ljust(col_width) for cell in row) + "|"
            table_rows.append(row_line)
        
        # Combine all parts
        table = [separator, header_line, separator] + table_rows + [separator]
        return "\n".join(table)
    
    @staticmethod
    def wrap_with_expansion(text, variables, width=80):
        """Wrap text while preserving expansion variables"""
        # First expand the text
        expanded = mud.expand_text(text, variables)
        
        # Then format it
        return mud.format_string(expanded, width=width)

# Usage
processor = TextProcessor()

# Create a player status table
headers = ["Name", "Level", "Race", "Status"]
rows = [
    ["Gandalf", "50", "Human", "Online"],
    ["Legolas", "45", "Elf", "Away"],
    ["Gimli", "48", "Dwarf", "Online"]
]

table = processor.create_table(headers, rows)
print(table)

# Colorized messages
colored_msg = processor.colorize_text("<red>Warning:</red> <yellow>Low health!</yellow>")

# Advanced text with expansion
template = "Welcome [name]! Your [class] is level [level]."
variables = {'name': 'Hero', 'class': 'Warrior', 'level': 25}
formatted = processor.wrap_with_expansion(template, variables, 60)
```

## See Also

- [mudsys Module](mudsys.md) - Core system functions
- [char Module](char.md) - Character manipulation
- [event Module](event.md) - Event system
- [hooks Module](hooks.md) - Hook system
- [Core Concepts: Scripting Best Practices](../../core-concepts/scripting-best-practices.md)
- [Tutorials: Utility Functions](../../tutorials/utility-functions.md)