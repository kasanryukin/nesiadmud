---
layout: default
title: Modules
parent: API Reference
nav_order: 1
has_children: true
permalink: /reference/modules/
---

# Python Modules

NakedMud provides 13 core Python modules that expose C functionality to Python scripts. Each module contains both EFuns (External Functions) and EObjs (External Objects) related to its domain.

## Core System Modules

### [mudsys](mudsys.md)
Core MUD system utilities, logging, configuration, and fundamental operations.

### [auxiliary](auxiliary.md) 
Auxiliary data management system for extending objects with custom data.

### [event](event.md)
Event handling, scheduling, and timed action management.

### [storage](storage.md)
Data persistence, serialization, and storage management.

## Character and Account Modules

### [account](account.md)
Player account management, authentication, and account-level data.

### [char](char.md)
Character manipulation, stats, properties, and character-specific operations.

### [mudsock](mudsock.md)
Socket and connection handling for player communication.

## World and Environment Modules

### [room](room.md)
Room and world management, area creation, and environmental systems.

### [exit](exit.md)
Exit and movement system, connections between rooms.

### [obj](obj.md)
Game object management, item creation, and object interactions.

## Development and Building Modules

### [mud](mud.md)
General MUD utilities and helper functions.

### [hooks](hooks.md)
Hook and trigger system for event-driven programming.

### [olc](olc.md)
Online creation tools for building and editing game content.

## Module Organization

Each module contains:
- **EFuns**: C functions exposed to Python
- **EObjs**: C objects wrapped as Python classes
- **Constants**: Module-specific constants and enumerations
- **Examples**: Working code examples for common tasks

## Usage Patterns

### Importing Modules
```python
import mudsys
import char
import room
```

### Common Function Patterns
- **Get/Set Functions**: `charGetName()`, `charSetName()`
- **Creation Functions**: `newChar()`, `newRoom()`
- **Query Functions**: `charIsNPC()`, `roomHasExit()`
- **Action Functions**: `charSend()`, `roomSendMessage()`

### Error Handling
Most functions return `None` or `False` on error. Always check return values:

```python
character = char.charGetByName("player")
if character:
    char.charSend(character, "Hello!")
else:
    mudsys.log_string("Character not found")
```

## See Also

- [EFuns Reference](../efuns.md) - All external functions by category
- [EObjs Reference](../eobjs.md) - All external objects and their methods
- [Core Concepts](/core-concepts/) - Understanding NakedMud's architecture