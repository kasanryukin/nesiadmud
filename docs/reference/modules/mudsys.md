---
layout: default
title: mudsys Module
parent: Modules
grand_parent: API Reference
nav_order: 1
---

# mudsys Module

The `mudsys` module provides core MUD system utilities and functions. It serves as the central hub for system-level operations, command management, account handling, and world database interactions.

**Module Type**: Core EFuns (External Functions)  
**Import**: `import mudsys`

## Overview

The mudsys module contains functions for:
- Account and character management
- Command registration and handling
- World database operations
- System configuration
- Help system management
- Movement and visibility checks

## Account Management

### account_creating(name)

**Returns**: `bool`

Returns whether an account with the specified name is currently being created.

**Parameters**:
- `name` (str): The account name to check

**Example**:
```python
import mudsys

if mudsys.account_creating("newplayer"):
    # Account is in creation process
    pass
```

### account_exists(name)

**Returns**: `bool`

Returns whether an account with the specified name exists in the system.

**Parameters**:
- `name` (str): The account name to check

**Example**:
```python
import mudsys

if mudsys.account_exists("player1"):
    # Account exists
    pass
```

### create_account(acctname)

**Returns**: `PyAccount` or `None`

Creates a new account with the specified name. Returns None if an account with that name already exists or is being created.

**Parameters**:
- `acctname` (str): The name for the new account

**Example**:
```python
import mudsys

new_account = mudsys.create_account("newplayer")
if new_account:
    # Account created successfully
    mudsys.do_register(new_account)
```

**Note**: After account creation, `mudsys.do_register(acct)` must be called to complete the registration process.

### load_account(name)

**Returns**: `PyAccount` or `None`

Loads and returns a saved account by the specified name.

**Parameters**:
- `name` (str): The account name to load

**Example**:
```python
import mudsys

account = mudsys.load_account("existingplayer")
if account:
    # Account loaded successfully
    pass
```

### do_register(char_or_account)

**Returns**: `None`

Registers a player character or account for the first time. Should be called after creation.

**Parameters**:
- `char_or_account` (PyChar or PyAccount): The character or account to register

**Example**:
```python
import mudsys

new_account = mudsys.create_account("newplayer")
if new_account:
    mudsys.do_register(new_account)
```

### do_save(char_or_account)

**Returns**: `None`

Saves a character or account's information to disk.

**Parameters**:
- `char_or_account` (PyChar or PyAccount): The character or account to save

**Example**:
```python
import mudsys

# Save a character
mudsys.do_save(character)

# Save an account
mudsys.do_save(account)
```

## Character Management

### create_player(name)

**Returns**: `PyChar` or `None`

Creates a new player character. Alias for `mudsys.create_account` for player characters.

**Parameters**:
- `name` (str): The character name

### get_player(name)

**Returns**: `PyChar` or `None`

Returns a saved character by the specified name.

**Parameters**:
- `name` (str): The character name to load

**Example**:
```python
import mudsys

character = mudsys.get_player("hero")
if character:
    # Character loaded successfully
    pass
```

### load_char(name)

**Returns**: `PyChar` or `None`

Alias for `mudsys.get_player(name)`.

### player_creating(name)

**Returns**: `bool`

Returns whether a player with the specified name is currently being created.

**Parameters**:
- `name` (str): The player name to check

### player_exists(name)

**Returns**: `bool`

Returns whether a player with the specified name exists.

**Parameters**:
- `name` (str): The player name to check

## Command System

### add_cmd(name, shorthand, cmd_func, user_group, interrupts_action)

**Returns**: `None`

Adds a new command to the master command table.

**Parameters**:
- `name` (str): The command name
- `shorthand` (str or None): Preferred shorthand (e.g., 'n' for 'north')
- `cmd_func` (function): Command function taking (character, command_name, argument)
- `user_group` (str): Required user group to use the command
- `interrupts_action` (bool): Whether the command interrupts character actions

**Example**:
```python
import mudsys

def my_command(ch, cmd, arg):
    ch.send("You executed the command with argument: " + arg)

mudsys.add_cmd("mycommand", "mc", my_command, "player", True)
```

### add_cmd_check(name, check_func)

**Returns**: `None`

Adds a command check to a registered command. Check functions should return False and send an error message if the check fails.

**Parameters**:
- `name` (str): The command name
- `check_func` (function): Check function taking (character, command_name)

**Example**:
```python
import mudsys

def check_alive(ch, cmd):
    if ch.is_dead():
        ch.send("You can't do that while dead!")
        return False
    return True

mudsys.add_cmd_check("mycommand", check_alive)
```

### remove_cmd(name)

**Returns**: `None`

Removes a command from the master command table.

**Parameters**:
- `name` (str): The command name to remove

## Socket and Connection Management

### attach_account_socket(acct, sock)

**Returns**: `None`

Links a loaded account to a connected socket.

**Parameters**:
- `acct` (PyAccount): The account to attach
- `sock` (PySocket): The socket to attach to

### attach_char_socket(ch, sock)

**Returns**: `None`

Links a loaded character to a connected socket.

**Parameters**:
- `ch` (PyChar): The character to attach
- `sock` (PySocket): The socket to attach to

### detach_char_socket(ch)

**Returns**: `None`

Unlinks a character from its attached socket.

**Parameters**:
- `ch` (PyChar): The character to detach

### do_disconnect(ch)

**Returns**: `None`

Calls `detach_char_socket`, then closes the socket.

**Parameters**:
- `ch` (PyChar): The character to disconnect

### do_quit(ch)

**Returns**: `None`

Extracts a character from the game world.

**Parameters**:
- `ch` (PyChar): The character to quit

### try_enter_game(ch)

**Returns**: `bool`

Attempts to add a character to the game world.

**Parameters**:
- `ch` (PyChar): The character to enter

## System Operations

### do_copyover()

**Returns**: `None`

Performs a copyover on the MUD, preserving player connections while restarting the server.

### do_shutdown()

**Returns**: `None`

Shuts down the MUD server.

### next_uid()

**Returns**: `int`

Returns the next available universal identification number.

### sys_getval(name)

**Returns**: `str`

Returns a value registered in the system settings.

**Parameters**:
- `name` (str): The setting name

### sys_setval(name, val)

**Returns**: `None`

Sets a value in the system settings.

**Parameters**:
- `name` (str): The setting name
- `val` (str): The value to set

### sys_getvar(name)

**Returns**: `str`

Alias for `mudsys.sys_getval`.

### sys_setvar(name, val)

**Returns**: `None`

Alias for `mudsys.sys_setval`.

## Method Extension System

### add_char_method(name, method)

**Returns**: `None`

Adds a function or property to the PyChar class, extending character functionality.

**Parameters**:
- `name` (str): The method name
- `method` (function): The method to add

**Example**:
```python
import mudsys

def get_full_name(self):
    return self.name + " the " + self.title

mudsys.add_char_method("get_full_name", get_full_name)

# Now all characters have the get_full_name method
# character.get_full_name()
```

### add_acct_method(name, method)

**Returns**: `None`

Adds a function or property to the PyAccount class.

### add_room_method(name, method)

**Returns**: `None`

Adds a function or property to the PyRoom class.

### add_obj_method(name, method)

**Returns**: `None`

Adds a function or property to the PyObj class.

### add_exit_method(name, method)

**Returns**: `None`

Adds a function or property to the PyExit class.

### add_sock_method(name, method)

**Returns**: `None`

Adds a function or property to the PySocket class.

## World Database Operations

### world_add_type(typename, class_data)

**Returns**: `None`

Registers a new type to the world database (e.g., mob, obj, room prototypes).

**Parameters**:
- `typename` (str): The type name
- `class_data` (class): Class with store() and setKey() methods

**Requirements**: The class must have:
- `store()` method returning a storage set
- `setKey()` method
- `__init__()` method accepting optional storage set parameter

### world_get_type(typename, key)

**Returns**: `object` or `None`

Returns a registered entry of the specified type from the world database.

**Parameters**:
- `typename` (str): The type name
- `key` (str): The entry key

### world_put_type(typename, key, data)

**Returns**: `None`

Puts and saves an entry of the specified type to the world database.

**Parameters**:
- `typename` (str): The type name
- `key` (str): The entry key
- `data` (object): The data to store

### world_remove_type(typename, key)

**Returns**: `object` or `None`

Removes and returns an entry from the world database.

**Parameters**:
- `typename` (str): The type name
- `key` (str): The entry key

### world_save_type(typename, key)

**Returns**: `None`

Saves an entry in the world database if it exists.

**Parameters**:
- `typename` (str): The type name
- `key` (str): The entry key

## Help System

### add_help(keywords, info, user_groups='', related='')

**Returns**: `None`

Adds a new, non-persistent helpfile to the MUD's help database.

**Parameters**:
- `keywords` (str): Space-separated keywords for the help entry
- `info` (str): The help text content
- `user_groups` (str, optional): Comma-separated list of user groups that can access this help
- `related` (str, optional): Related help topics

**Example**:
```python
import mudsys

help_text = """
This is a sample help entry explaining how to use a custom command.

Usage: mycommand <argument>

The command does something useful with the provided argument.
"""

mudsys.add_help("mycommand custom", help_text, "player", "commands help")
```

### get_help(keyword)

**Returns**: `tuple` or `None`

Returns a tuple of (keywords, info, user_groups, related) for a helpfile, or None if not found.

**Parameters**:
- `keyword` (str): The help keyword to search for

### list_help(keyword='')

**Returns**: `list`

Returns a list of helpfiles matching the specified keyword. If no keyword is supplied, returns all helpfiles.

**Parameters**:
- `keyword` (str, optional): Keyword to filter help entries

## Movement and Visibility

### register_move_check(check_func)

**Returns**: `None`

Registers a check to perform for movement commands.

**Parameters**:
- `check_func` (function): Check function taking (character, command_name)

### register_dflt_move_cmd(cmdname)

**Returns**: `None`

Registers a new default movement command (e.g., "north").

**Parameters**:
- `cmdname` (str): The movement command name

### set_cmd_move(cmd_func)

**Returns**: `None`

Registers a player command for handling all default movement commands.

**Parameters**:
- `cmd_func` (function): Movement command function

### register_char_cansee(check_function)

**Returns**: `None`

Registers a check for whether one character can see another.

**Parameters**:
- `check_function` (function): Function taking (observer, observee) and returning bool

### register_obj_cansee(check_function)

**Returns**: `None`

Same as `register_char_cansee` but for objects.

### register_exit_cansee(check_function)

**Returns**: `None`

Same as `register_char_cansee` but for exits.

## Zone and Permission Management

### can_edit_zone(ch, zone)

**Returns**: `bool`

Returns True or False if a character has permission to edit a zone.

**Parameters**:
- `ch` (PyChar): The character to check
- `zone` (str): The zone name

### list_zone_contents(zone, type)

**Returns**: `list`

Returns a list of content keys of the given type for the specified zone.

**Parameters**:
- `zone` (str): The zone name
- `type` (str): The content type (e.g., "room", "mob", "obj")

## Item and Equipment System

### add_worn_type(type, postypes)

**Returns**: `None`

Registers a new type of worn item.

**Parameters**:
- `type` (str): The worn item type name
- `postypes` (str): Comma-separated list of body position types

**Example**:
```python
import mudsys

# Register a shirt that goes on torso and both arms
mudsys.add_worn_type("shirt", "torso,arm,arm")
```

### item_add_type(name, type_data)

**Returns**: `None`

Registers a new item type and its data.

**Parameters**:
- `name` (str): The item type name
- `type_data` (object): The type data object

## Utility Functions

### handle_cmd_input(sock, cmd)

**Returns**: `None`

Processes command input from a socket. Equivalent to `char.Char.act(cmd)`.

**Parameters**:
- `sock` (PySocket): The socket receiving input
- `cmd` (str): The command string

### show_prompt(sock)

**Returns**: `None`

Displays the default game prompt to the socket. Can be replaced by assigning a new function to `mudsys.show_prompt`.

**Parameters**:
- `sock` (PySocket): The socket to show the prompt to

### password_matches(acct, passwd)

**Returns**: `bool`

Returns True or False if the given password matches the account's password.

**Parameters**:
- `acct` (PyAccount): The account to check
- `passwd` (str): The password to verify

### set_password(acct, passwd)

**Returns**: `None`

Sets an account's password.

**Parameters**:
- `acct` (PyAccount): The account
- `passwd` (str): The new password

## Bitvector Operations

### create_bitvector()

**Returns**: `None`

Not yet implemented.

### create_bit(bitvector, bit)

**Returns**: `None`

Creates a new bit on the specified bitvector.

**Parameters**:
- `bitvector` (object): The bitvector object
- `bit` (str): The bit name

## See Also

- [auxiliary Module](auxiliary.md) - Auxiliary data management
- [event Module](event.md) - Event system
- [char Module](char.md) - Character manipulation
- [account Module](account.md) - Account management
- [Core Concepts: Python Integration](../../core-concepts/python-integration.md)