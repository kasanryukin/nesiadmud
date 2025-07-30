---
layout: default
title: API Reference
nav_order: 4
has_children: true
permalink: /reference/
---

# API Reference

Complete reference documentation for all NakedMud Python functionality. This section provides detailed information about every function, class, and module available to Python scripts.

## Organization

### [Modules](modules/)
Documentation for all 13 core Python modules that provide the main functionality:

| Module | Purpose |
|--------|---------|
| **[mudsys](modules/mudsys.md)** | Core MUD system utilities |
| **[auxiliary](modules/auxiliary.md)** | Auxiliary data management |
| **[event](modules/event.md)** | Event handling and scheduling |
| **[storage](modules/storage.md)** | Data persistence and storage |
| **[account](modules/account.md)** | Player account management |
| **[char](modules/char.md)** | Character manipulation |
| **[room](modules/room.md)** | Room and world management |
| **[exit](modules/exit.md)** | Exit and movement system |
| **[obj](modules/obj.md)** | Game object management |
| **[mudsock](modules/mudsock.md)** | Socket and connection handling |
| **[mud](modules/mud.md)** | General MUD utilities |
| **[hooks](modules/hooks.md)** | Hook and trigger system |
| **[olc](modules/olc.md)** | Online creation tools |

### Function Categories

#### [EFuns (External Functions)](efuns.md)
C-derived Python functionality exposed through the modules:
- Character manipulation functions
- Room and world management
- Object handling and creation
- Event system functions
- Storage and persistence
- And much more...

#### [EObjs (External Objects)](eobjs.md)
C-defined classes wrapped as Python objects:
- **PyChar** - Character objects and methods
- **PyRoom** - Room objects and properties
- **PyObj** - Game object instances
- **PySocket** - Player connection objects
- **PyAccount** - Player account management
- **PyExit** - Room exit objects

#### [SEFuns (System External Functions)](sefuns.md)
Global library functions exposed by Python:
- Utility functions available system-wide
- Registration and callback systems
- Extension mechanisms for adding functionality

#### [SEFuns Framework](sefuns-framework.md)
Documentation for the SEFuns framework system:
- How to create and register SEFuns
- Framework architecture and patterns
- Advanced SEFuns development

## Using This Reference

### Function Documentation Format
Each function is documented with:
- **Signature**: Complete function signature with parameters
- **Module**: Which module provides the function
- **Type**: Whether it's an efun, eobj method, or sefun
- **Description**: What the function does
- **Parameters**: Detailed parameter descriptions
- **Returns**: Return value information
- **Examples**: Working code examples
- **See Also**: Related functions and concepts

### Quick Lookup
Use the search functionality to quickly find specific functions or concepts. You can search by:
- Function name
- Module name
- Parameter types
- Keywords and concepts

### Cross-References
Throughout the reference, you'll find links to:
- Related functions
- Core concept explanations
- Tutorial examples
- Best practice guides

## Getting Started with the Reference

If you're new to the API reference:

1. **Browse by Module**: Start with the [Modules](modules/) section to understand what each module provides
2. **Explore by Type**: Check out [EFuns](efuns/), [EObjs](eobs/), and [SEFuns](sefuns/) to understand the different function categories
3. **Use Search**: When you know what you're looking for, use the search feature
4. **Follow Examples**: Each function includes working examples you can adapt

## Common Patterns

Many functions follow common patterns:
- **Object Creation**: Functions that create new game objects
- **Data Access**: Functions that get/set object properties
- **Event Handling**: Functions that work with the event system
- **Validation**: Functions that check object states or permissions

Understanding these patterns will help you navigate the API more effectively.