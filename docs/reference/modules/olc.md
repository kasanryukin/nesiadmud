---
layout: default
title: olc Module
parent: Modules
grand_parent: API Reference
nav_order: 13
---

# olc Module

The `olc` module provides the Python wrapper for the Online Creation (OLC) system. OLC allows users to create and edit game content (rooms, objects, NPCs, etc.) while online, providing a menu-driven interface for builders and administrators.

**Module Type**: Core EFuns (External Functions)  
**Import**: `import olc`

## Overview

The OLC module handles:
- Menu-driven editing interfaces
- Data validation and parsing
- Prototype creation and modification
- Extensible editing systems
- Item type-specific editors
- Integration with the world database

OLC is essential for world building, allowing authorized users to create and modify game content without needing to edit files directly or restart the server.

## Core Functions

### do_olc(sock, menu_func, chooser_func, parse_func, saver_func, data, autosave=False)

**Returns**: `None`

Entry point to the OLC system. Sets up a complete editing session with menu display, choice handling, parsing, and saving.

**Parameters**:
- `sock` (PySocket): The socket of the user doing the editing
- `menu_func` (function): Function to display the menu
- `chooser_func` (function): Function to handle menu choices
- `parse_func` (function): Function to parse user input
- `saver_func` (function): Function to save the data
- `data` (any): The data being edited
- `autosave` (bool, optional): Whether to automatically save changes

**Function Signatures**:
- `menu_func(socket, data)` - Display the editing menu
- `chooser_func(socket, data, choice)` - Handle menu choice, return choice code
- `parse_func(socket, data, choice, input)` - Parse input for a choice
- `saver_func(socket, data)` - Save the edited data

**Example**:
```python
import olc, mudsock

def edit_simple_data(socket, data_dict):
    """Edit a simple data dictionary"""
    
    def show_menu(sock, data):
        """Display the editing menu"""
        sock.send("=== Simple Data Editor ===")
        sock.send(f"1. Name: {data.get('name', 'None')}")
        sock.send(f"2. Description: {data.get('desc', 'None')}")
        sock.send(f"3. Value: {data.get('value', 0)}")
        sock.send("S. Save and exit")
        sock.send("Q. Quit without saving")
        sock.send_raw("Choice: ")
    
    def handle_choice(sock, data, choice):
        """Handle menu choices"""
        choice = choice.lower().strip()
        
        if choice == '1':
            sock.send("Enter new name:")
            return 1
        elif choice == '2':
            sock.send("Enter new description:")
            return 2
        elif choice == '3':
            sock.send("Enter new value:")
            return 3
        elif choice == 's':
            return olc.MENU_CHOICE_OK  # Save and exit
        elif choice == 'q':
            return olc.MENU_CHOICE_INVALID  # Quit without saving
        else:
            sock.send("Invalid choice.")
            return olc.MENU_NOCHOICE
    
    def parse_input(sock, data, choice, input_text):
        """Parse user input for each choice"""
        input_text = input_text.strip()
        
        if choice == 1:  # Name
            if input_text:
                data['name'] = input_text
                sock.send(f"Name set to: {input_text}")
            else:
                sock.send("Name cannot be empty.")
        
        elif choice == 2:  # Description
            data['desc'] = input_text
            sock.send("Description updated.")
        
        elif choice == 3:  # Value
            try:
                value = int(input_text)
                data['value'] = value
                sock.send(f"Value set to: {value}")
            except ValueError:
                sock.send("Please enter a valid number.")
    
    def save_data(sock, data):
        """Save the edited data"""
        sock.send("Data saved successfully!")
        # Here you would save to database, file, etc.
        return True
    
    # Start the OLC session
    olc.do_olc(socket, show_menu, handle_choice, parse_input, save_data, data_dict)

# Usage
socket = mudsock.Mudsock()  # Assume this is a real socket
data = {'name': 'Test Item', 'desc': 'A test item', 'value': 100}
edit_simple_data(socket, data)
```

### extend(olc_type, optname, menu_func, chooser_func, parse_func=None, fromproto_func=None, toproto_func=None)

**Returns**: `None`

Registers a new OLC menu extender for existing editors (medit, redit, oedit).

**Parameters**:
- `olc_type` (str): The OLC type - "medit", "redit", or "oedit"
- `optname` (str): The option name to add to the menu
- `menu_func` (function): Function to display the extended menu option
- `chooser_func` (function): Function to handle the choice
- `parse_func` (function, optional): Function to parse input
- `fromproto_func` (function, optional): Function to load data from prototype
- `toproto_func` (function, optional): Function to save data to prototype

**Example**:
```python
import olc

def add_room_atmosphere_editor():
    """Add atmosphere editing to room editor"""
    
    def show_atmosphere_option(sock, room):
        """Show atmosphere option in room menu"""
        atmosphere = getattr(room, 'atmosphere', 'None')
        sock.send(f"A. Atmosphere: {atmosphere}")
    
    def handle_atmosphere_choice(sock, room, choice):
        """Handle atmosphere choice"""
        if choice.lower() == 'a':
            sock.send("Enter room atmosphere:")
            return ord('a')  # Return choice code
        return olc.MENU_NOCHOICE
    
    def parse_atmosphere_input(sock, room, choice, input_text):
        """Parse atmosphere input"""
        if choice == ord('a'):
            room.atmosphere = input_text.strip()
            sock.send(f"Atmosphere set to: {input_text}")
    
    def load_atmosphere_from_proto(room, proto_data):
        """Load atmosphere from prototype"""
        room.atmosphere = proto_data.get('atmosphere', '')
    
    def save_atmosphere_to_proto(room, proto_data):
        """Save atmosphere to prototype"""
        proto_data['atmosphere'] = getattr(room, 'atmosphere', '')
    
    # Register the extender
    olc.extend("redit", "atmosphere", 
              show_atmosphere_option, 
              handle_atmosphere_choice,
              parse_atmosphere_input,
              load_atmosphere_from_proto,
              save_atmosphere_to_proto)

# Add the atmosphere editor
add_room_atmosphere_editor()
```

### item_add_olc(itemtype, menu_func, chooser_func, parse_func, fromproto_func, toproto_func)

**Returns**: `None`

Registers a new OLC handler for a specific item type.

**Parameters**:
- `itemtype` (str): The item type name
- `menu_func` (function): Function to display the item type menu
- `chooser_func` (function): Function to handle menu choices
- `parse_func` (function): Function to parse input
- `fromproto_func` (function): Function to load from prototype
- `toproto_func` (function): Function to save to prototype

**Example**:
```python
import olc

def add_weapon_editor():
    """Add weapon item type editor"""
    
    def show_weapon_menu(sock, weapon_data):
        """Display weapon editing menu"""
        sock.send("=== Weapon Editor ===")
        sock.send(f"1. Damage: {weapon_data.get('damage', 0)}")
        sock.send(f"2. Weapon Type: {weapon_data.get('weapon_type', 'sword')}")
        sock.send(f"3. Hit Bonus: {weapon_data.get('hit_bonus', 0)}")
        sock.send(f"4. Critical Chance: {weapon_data.get('crit_chance', 5)}%")
    
    def handle_weapon_choice(sock, weapon_data, choice):
        """Handle weapon menu choices"""
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= 4:
                return choice_num
        except ValueError:
            pass
        
        sock.send("Invalid choice.")
        return olc.MENU_NOCHOICE
    
    def parse_weapon_input(sock, weapon_data, choice, input_text):
        """Parse weapon input"""
        input_text = input_text.strip()
        
        if choice == 1:  # Damage
            try:
                damage = int(input_text)
                weapon_data['damage'] = max(1, damage)
                sock.send(f"Damage set to: {weapon_data['damage']}")
            except ValueError:
                sock.send("Please enter a valid number.")
        
        elif choice == 2:  # Weapon Type
            valid_types = ['sword', 'axe', 'mace', 'dagger', 'bow', 'staff']
            if input_text.lower() in valid_types:
                weapon_data['weapon_type'] = input_text.lower()
                sock.send(f"Weapon type set to: {input_text}")
            else:
                sock.send(f"Valid types: {', '.join(valid_types)}")
        
        elif choice == 3:  # Hit Bonus
            try:
                bonus = int(input_text)
                weapon_data['hit_bonus'] = bonus
                sock.send(f"Hit bonus set to: {bonus}")
            except ValueError:
                sock.send("Please enter a valid number.")
        
        elif choice == 4:  # Critical Chance
            try:
                crit = int(input_text)
                weapon_data['crit_chance'] = max(0, min(100, crit))
                sock.send(f"Critical chance set to: {weapon_data['crit_chance']}%")
            except ValueError:
                sock.send("Please enter a valid percentage (0-100).")
    
    def load_weapon_from_proto(weapon_data, proto):
        """Load weapon data from prototype"""
        weapon_data['damage'] = proto.get('damage', 10)
        weapon_data['weapon_type'] = proto.get('weapon_type', 'sword')
        weapon_data['hit_bonus'] = proto.get('hit_bonus', 0)
        weapon_data['crit_chance'] = proto.get('crit_chance', 5)
    
    def save_weapon_to_proto(weapon_data, proto):
        """Save weapon data to prototype"""
        proto['damage'] = weapon_data.get('damage', 10)
        proto['weapon_type'] = weapon_data.get('weapon_type', 'sword')
        proto['hit_bonus'] = weapon_data.get('hit_bonus', 0)
        proto['crit_chance'] = weapon_data.get('crit_chance', 5)
    
    # Register the weapon editor
    olc.item_add_olc("weapon", 
                    show_weapon_menu,
                    handle_weapon_choice, 
                    parse_weapon_input,
                    load_weapon_from_proto,
                    save_weapon_to_proto)

# Add the weapon editor
add_weapon_editor()
```

## Constants

### MENU_CHOICE_INVALID
**Value**: `-1`

Returned by chooser functions to indicate an invalid choice that should exit the editor without saving.

### MENU_CHOICE_OK
**Value**: `-2`

Returned by chooser functions to indicate the user wants to save and exit the editor.

### MENU_NOCHOICE
**Value**: `0`

Returned by chooser functions to indicate no valid choice was made (redisplay menu).

## Usage Patterns

### Custom Data Editor

```python
import olc, auxiliary, storage

class CustomDataEditor:
    """Generic editor for custom data structures"""
    
    def __init__(self, title, fields):
        """
        Initialize editor
        
        Args:
            title: Editor title
            fields: List of field definitions
                   Each field: {'name': str, 'type': str, 'default': any, 'validator': func}
        """
        self.title = title
        self.fields = fields
    
    def edit_data(self, socket, data):
        """Start editing session"""
        
        def show_menu(sock, edit_data):
            """Display the editing menu"""
            sock.send(f"=== {self.title} ===")
            
            for i, field in enumerate(self.fields, 1):
                field_name = field['name']
                current_value = edit_data.get(field_name, field.get('default', 'None'))
                sock.send(f"{i}. {field_name.title()}: {current_value}")
            
            sock.send("S. Save and exit")
            sock.send("Q. Quit without saving")
            sock.send_raw("Choice: ")
        
        def handle_choice(sock, edit_data, choice):
            """Handle menu choices"""
            choice = choice.strip().lower()
            
            if choice == 's':
                return olc.MENU_CHOICE_OK
            elif choice == 'q':
                return olc.MENU_CHOICE_INVALID
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.fields):
                    field = self.fields[choice_num - 1]
                    sock.send(f"Enter new {field['name']}:")
                    return choice_num
            except ValueError:
                pass
            
            sock.send("Invalid choice.")
            return olc.MENU_NOCHOICE
        
        def parse_input(sock, edit_data, choice, input_text):
            """Parse user input"""
            if 1 <= choice <= len(self.fields):
                field = self.fields[choice - 1]
                field_name = field['name']
                field_type = field.get('type', 'string')
                
                # Type conversion
                try:
                    if field_type == 'int':
                        value = int(input_text.strip())
                    elif field_type == 'float':
                        value = float(input_text.strip())
                    elif field_type == 'bool':
                        value = input_text.strip().lower() in ['true', 'yes', '1', 'on']
                    else:  # string
                        value = input_text.strip()
                    
                    # Validation
                    validator = field.get('validator')
                    if validator and not validator(value):
                        sock.send("Invalid value.")
                        return
                    
                    # Set value
                    edit_data[field_name] = value
                    sock.send(f"{field_name.title()} set to: {value}")
                
                except ValueError:
                    sock.send(f"Please enter a valid {field_type}.")
        
        def save_data(sock, edit_data):
            """Save the data"""
            sock.send("Data saved successfully!")
            return True
        
        # Start OLC session
        olc.do_olc(socket, show_menu, handle_choice, parse_input, save_data, data)

# Example usage
def create_npc_stats_editor():
    """Create an NPC stats editor"""
    
    def validate_stat(value):
        """Validate stat values"""
        return 1 <= value <= 100
    
    def validate_name(value):
        """Validate name"""
        return len(value) >= 3 and value.isalpha()
    
    fields = [
        {'name': 'name', 'type': 'string', 'default': 'Unnamed', 'validator': validate_name},
        {'name': 'strength', 'type': 'int', 'default': 10, 'validator': validate_stat},
        {'name': 'intelligence', 'type': 'int', 'default': 10, 'validator': validate_stat},
        {'name': 'dexterity', 'type': 'int', 'default': 10, 'validator': validate_stat},
        {'name': 'hit_points', 'type': 'int', 'default': 100},
        {'name': 'is_aggressive', 'type': 'bool', 'default': False}
    ]
    
    return CustomDataEditor("NPC Stats Editor", fields)

# Usage
npc_editor = create_npc_stats_editor()
npc_data = {'name': 'Goblin', 'strength': 8, 'intelligence': 6}
# npc_editor.edit_data(socket, npc_data)
```

### Advanced Room Editor Extension

```python
import olc, room, auxiliary, storage

class RoomEnvironment:
    """Environmental data for rooms"""
    
    def __init__(self, storage_set=None):
        if storage_set:
            self.temperature = storage_set.readInt("temperature")
            self.humidity = storage_set.readInt("humidity")
            self.light_level = storage_set.readInt("light_level")
            self.air_quality = storage_set.readString("air_quality")
            self.sounds = storage_set.readString("sounds")
            self.smells = storage_set.readString("smells")
        else:
            self.temperature = 20  # Celsius
            self.humidity = 50     # Percentage
            self.light_level = 5   # 1-10 scale
            self.air_quality = "fresh"
            self.sounds = ""
            self.smells = ""
    
    def store(self):
        set = storage.StorageSet()
        set.storeInt("temperature", self.temperature)
        set.storeInt("humidity", self.humidity)
        set.storeInt("light_level", self.light_level)
        set.storeString("air_quality", self.air_quality)
        set.storeString("sounds", self.sounds)
        set.storeString("smells", self.smells)
        return set
    
    def copy(self):
        new_env = RoomEnvironment()
        new_env.temperature = self.temperature
        new_env.humidity = self.humidity
        new_env.light_level = self.light_level
        new_env.air_quality = self.air_quality
        new_env.sounds = self.sounds
        new_env.smells = self.smells
        return new_env
    
    def copyTo(self, to):
        to.temperature = self.temperature
        to.humidity = self.humidity
        to.light_level = self.light_level
        to.air_quality = self.air_quality
        to.sounds = self.sounds
        to.smells = self.smells

# Install the auxiliary data
auxiliary.install("room_environment", RoomEnvironment, "room")

def add_environment_editor():
    """Add environmental editing to room editor"""
    
    def show_environment_menu(sock, room_obj):
        """Show environment editing menu"""
        env = room_obj.aux("room_environment")
        if not env:
            sock.send("E. Environment: Not set")
            return
        
        sock.send("=== Environment Settings ===")
        sock.send(f"1. Temperature: {env.temperature}°C")
        sock.send(f"2. Humidity: {env.humidity}%")
        sock.send(f"3. Light Level: {env.light_level}/10")
        sock.send(f"4. Air Quality: {env.air_quality}")
        sock.send(f"5. Sounds: {env.sounds or 'None'}")
        sock.send(f"6. Smells: {env.smells or 'None'}")
        sock.send("0. Return to main menu")
    
    def handle_environment_choice(sock, room_obj, choice):
        """Handle environment menu choices"""
        if choice.lower() == 'e':
            # Enter environment submenu
            return ord('e')
        
        # Handle submenu choices
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return olc.MENU_CHOICE_OK  # Return to main menu
            elif 1 <= choice_num <= 6:
                prompts = {
                    1: "Enter temperature (-50 to 50°C):",
                    2: "Enter humidity (0-100%):",
                    3: "Enter light level (1-10):",
                    4: "Enter air quality (fresh/stale/toxic/smoky):",
                    5: "Enter ambient sounds:",
                    6: "Enter ambient smells:"
                }
                sock.send(prompts[choice_num])
                return choice_num
        except ValueError:
            pass
        
        sock.send("Invalid choice.")
        return olc.MENU_NOCHOICE
    
    def parse_environment_input(sock, room_obj, choice, input_text):
        """Parse environment input"""
        env = room_obj.aux("room_environment")
        if not env:
            return
        
        input_text = input_text.strip()
        
        if choice == 1:  # Temperature
            try:
                temp = int(input_text)
                if -50 <= temp <= 50:
                    env.temperature = temp
                    sock.send(f"Temperature set to {temp}°C")
                else:
                    sock.send("Temperature must be between -50 and 50°C")
            except ValueError:
                sock.send("Please enter a valid number.")
        
        elif choice == 2:  # Humidity
            try:
                humidity = int(input_text)
                if 0 <= humidity <= 100:
                    env.humidity = humidity
                    sock.send(f"Humidity set to {humidity}%")
                else:
                    sock.send("Humidity must be between 0 and 100%")
            except ValueError:
                sock.send("Please enter a valid number.")
        
        elif choice == 3:  # Light Level
            try:
                light = int(input_text)
                if 1 <= light <= 10:
                    env.light_level = light
                    sock.send(f"Light level set to {light}/10")
                else:
                    sock.send("Light level must be between 1 and 10")
            except ValueError:
                sock.send("Please enter a valid number.")
        
        elif choice == 4:  # Air Quality
            valid_qualities = ['fresh', 'stale', 'toxic', 'smoky', 'humid', 'dry']
            if input_text.lower() in valid_qualities:
                env.air_quality = input_text.lower()
                sock.send(f"Air quality set to: {input_text}")
            else:
                sock.send(f"Valid qualities: {', '.join(valid_qualities)}")
        
        elif choice == 5:  # Sounds
            env.sounds = input_text
            sock.send("Ambient sounds updated.")
        
        elif choice == 6:  # Smells
            env.smells = input_text
            sock.send("Ambient smells updated.")
    
    # Register the environment editor extension
    olc.extend("redit", "environment",
              show_environment_menu,
              handle_environment_choice,
              parse_environment_input)

# Add the environment editor
add_environment_editor()
```

### Batch Editing System

```python
import olc, room, obj, char

class BatchEditor:
    """System for batch editing multiple objects"""
    
    def __init__(self):
        self.edit_queue = []
        self.current_index = 0
    
    def add_to_queue(self, objects):
        """Add objects to the editing queue"""
        self.edit_queue.extend(objects)
    
    def start_batch_edit(self, socket, edit_type):
        """Start batch editing session"""
        if not self.edit_queue:
            socket.send("No objects in edit queue.")
            return
        
        self.current_index = 0
        self.edit_current_object(socket, edit_type)
    
    def edit_current_object(self, socket, edit_type):
        """Edit the current object in the queue"""
        if self.current_index >= len(self.edit_queue):
            socket.send("Batch editing complete!")
            self.edit_queue = []
            return
        
        current_obj = self.edit_queue[self.current_index]
        socket.send(f"Editing object {self.current_index + 1} of {len(self.edit_queue)}")
        
        def show_batch_menu(sock, obj):
            """Show batch editing menu"""
            sock.send(f"=== Batch Edit: {obj.name} ===")
            sock.send("1. Edit name")
            sock.send("2. Edit description")
            sock.send("3. Skip this object")
            sock.send("4. Save and next")
            sock.send("5. Cancel batch edit")
        
        def handle_batch_choice(sock, obj, choice):
            """Handle batch editing choices"""
            try:
                choice_num = int(choice.strip())
                
                if choice_num == 1:
                    sock.send(f"Current name: {obj.name}")
                    sock.send("Enter new name (or press enter to keep current):")
                    return 1
                elif choice_num == 2:
                    sock.send(f"Current description: {obj.desc}")
                    sock.send("Enter new description (or press enter to keep current):")
                    return 2
                elif choice_num == 3:
                    # Skip to next object
                    self.current_index += 1
                    self.edit_current_object(sock, edit_type)
                    return olc.MENU_CHOICE_OK
                elif choice_num == 4:
                    # Save and next
                    self.current_index += 1
                    self.edit_current_object(sock, edit_type)
                    return olc.MENU_CHOICE_OK
                elif choice_num == 5:
                    # Cancel batch edit
                    self.edit_queue = []
                    return olc.MENU_CHOICE_INVALID
            except ValueError:
                pass
            
            sock.send("Invalid choice.")
            return olc.MENU_NOCHOICE
        
        def parse_batch_input(sock, obj, choice, input_text):
            """Parse batch editing input"""
            input_text = input_text.strip()
            
            if choice == 1 and input_text:  # Name
                obj.name = input_text
                sock.send(f"Name changed to: {input_text}")
            elif choice == 2 and input_text:  # Description
                obj.desc = input_text
                sock.send("Description updated.")
        
        def save_batch_data(sock, obj):
            """Save batch editing data"""
            # Objects are modified in place
            return True
        
        # Start OLC for current object
        olc.do_olc(socket, show_batch_menu, handle_batch_choice, 
                  parse_batch_input, save_batch_data, current_obj, autosave=True)

# Usage example
def batch_edit_command(ch, cmd, arg):
    """Command to start batch editing"""
    if not ch.isInGroup("builder"):
        ch.send("You don't have permission to use batch editing.")
        return
    
    if not arg:
        ch.send("Usage: batchedit <room|inventory>")
        return
    
    batch_editor = BatchEditor()
    
    if arg == "room":
        # Edit all objects in the current room
        if ch.room and ch.room.contents:
            batch_editor.add_to_queue(ch.room.contents)
            batch_editor.start_batch_edit(ch.socket, "object")
        else:
            ch.send("No objects in this room to edit.")
    
    elif arg == "inventory":
        # Edit all objects in inventory
        if ch.inv:
            batch_editor.add_to_queue(ch.inv)
            batch_editor.start_batch_edit(ch.socket, "object")
        else:
            ch.send("No objects in your inventory to edit.")
    
    else:
        ch.send("Usage: batchedit <room|inventory>")
```

## See Also

- [mudsock Module](mudsock.md) - Socket handling for OLC interfaces
- [auxiliary Module](auxiliary.md) - Auxiliary data system for extending editors
- [storage Module](storage.md) - Data persistence for OLC data
- [mudsys Module](mudsys.md) - Core system functions
- [Core Concepts: World Building](../../core-concepts/world-building.md)
- [Tutorials: Using OLC](../../tutorials/using-olc.md)
- [Reference: OLC For Dummies](../../reference/olc-for-dummies.md)