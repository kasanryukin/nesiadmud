---
title: Python Integration Overview
layout: default
nav_order: 3
parent: Core Concepts
description: "Understanding how C and Python components interact in NakedMud"
---

# Python Integration Overview

NakedMud features deep integration between its C core and Python scripting environment. This architecture allows for powerful, flexible scripting while maintaining security and performance. Understanding this integration is crucial for effective mud development.

## Overview

The Python integration in NakedMud provides:

- **Seamless C-Python Interface** - C objects are wrapped as Python objects
- **Bidirectional Communication** - C can call Python, Python can call C
- **Module-Based Architecture** - 13 core Python modules expose C functionality
- **Dynamic Content Generation** - Prototypes, triggers, and dynamic descriptions
- **Safe Execution Environment** - Security controls protect the system

## Why Python Integration?

NakedMud's hybrid C/Python architecture combines the best of both worlds:

### C Core Benefits
- **Performance**: Critical game loops run at native C speed
- **Memory Efficiency**: Optimal memory usage for large-scale operations
- **System Access**: Direct access to operating system resources
- **Stability**: Mature, well-tested core systems

### Python Scripting Benefits
- **Rapid Development**: Quick iteration on game logic and content
- **Expressiveness**: Rich language features for complex behaviors
- **Accessibility**: Easier for builders and content creators to learn
- **Flexibility**: Dynamic modification without recompilation

### Integration Advantages
- **Hot Reloading**: Modify scripts without restarting the MUD
- **Gradual Migration**: Move functionality between C and Python as needed
- **Specialization**: Use each language for what it does best
- **Community**: Leverage Python's extensive ecosystem

## The Integration Philosophy

NakedMud's integration follows several key principles:

### 1. Transparent Object Wrapping
C objects appear as natural Python objects:

```python
# C character appears as Python object
ch = load_mob("guard@castle")
ch.name = "Sir Galahad"        # Modifies C structure
ch.send("Hello, world!")       # Calls C function
print(ch.level)                # Reads C data
```

### 2. Bidirectional Communication
Both C and Python can initiate calls:

```python
# Python calls C
ch.send("Message")             # Python → C function

# C calls Python (via triggers, prototypes, etc.)
# When player enters room → Python trigger executes
```

### 3. Shared Data Model
Objects maintain consistency across language boundaries:

```python
# Modifications in Python are immediately visible in C
ch.hp = 50                     # Python sets value
# C code immediately sees hp = 50
```

### 4. Controlled Access
Python has access to appropriate functionality without compromising security:

```python
# Allowed: Game-related operations
ch.send("Hello")
obj = load_obj("sword@weapons")

# Blocked: System-level operations
# open("/etc/passwd")          # Security violation
# import os                    # Restricted import
```

## Architecture Components

### Core Integration Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    Python Scripts                          │
│  (Prototypes, Triggers, Commands, Dynamic Content)         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Python Modules (13 core)                   │
│  mudsys, char, room, obj, event, storage, auxiliary, etc.  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 C-Python Wrapper Layer                     │
│        (PyChar, PyRoom, PyObj, PySocket, etc.)             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    C Core Engine                           │
│     (Game Logic, Data Structures, Network, Storage)        │
└─────────────────────────────────────────────────────────────┘
```

### Python Module Structure

NakedMud exposes 13 core Python modules that provide access to C functionality:

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| `mudsys` | System-level functions | - |
| `char` | Character manipulation | PyChar |
| `room` | Room/world management | PyRoom |
| `obj` | Object handling | PyObj |
| `account` | Player accounts | PyAccount |
| `mudsock` | Socket/connection | PySocket |
| `exit` | Room exits | PyExit |
| `event` | Event system | - |
| `storage` | Data persistence | StorageSet |
| `auxiliary` | Auxiliary data | - |
| `hooks` | Hook system | - |
| `mud` | General utilities | - |
| `olc` | Online creation | - |

## See Also

- [Security Model](security-model.md) - Detailed security and restricted execution information
- [Scripting Best Practices](scripting-best-practices.md) - Guidelines for effective script development

## C-Python Object Wrapping

NakedMud creates seamless integration by wrapping C data structures as Python objects:

### Wrapper Architecture

```c
// Each C structure gets a Python wrapper
typedef struct {
    PyObject_HEAD           // Standard Python object header
    CHAR_DATA *char_data;   // Pointer to C structure
    int is_borrowed;        // Memory management flag
} PyChar;
```

### Method Binding

C functions become Python methods through method tables:

```c
static PyMethodDef PyChar_methods[] = {
    {"send", PyChar_send, METH_VARARGS, "Send message to character"},
    {"act", PyChar_act, METH_VARARGS, "Perform an action"},
    {"getAuxiliary", PyChar_getAuxiliary, METH_VARARGS, "Get auxiliary data"},
    {NULL, NULL, 0, NULL}  // Sentinel
};
```

### Transparent Access

From Python's perspective, C objects appear completely natural:

```python
# These operations work seamlessly across the C/Python boundary
ch.name = "Sir Galahad"        # Sets C structure field
ch.send("Hello!")              # Calls C function
level = ch.level               # Reads C data
aux = ch.getAuxiliary("data")  # Accesses auxiliary system
```

## Script Execution Contexts

Different types of scripts run in different contexts with appropriate variables and permissions:

### Prototype Scripts
```python
# Context: Creating new game objects
me    # The object being created (PyChar, PyRoom, or PyObj)
# Full access to object modification
```

### Trigger Scripts
```python
# Context: Responding to game events
me    # The object the trigger is attached to
ch    # The character who triggered the event
arg   # Arguments passed to the trigger
# Limited to event-appropriate actions
```

### Dynamic Descriptions
```python
# Context: Generating dynamic content
me    # The object being described
ch    # The character viewing the object
# Read-only access for content generation
```

## Integration Patterns

### Event-Driven Architecture

The integration follows an event-driven model where C code triggers Python execution:

1. **Game Event Occurs** (player enters room, combat starts, etc.)
2. **C Code Identifies Triggers** (checks for attached Python scripts)
3. **Python Environment Created** (restricted dictionary with context)
4. **Script Executes** (with appropriate permissions and variables)
5. **Results Applied** (changes reflected in C structures)
6. **Cleanup** (Python environment destroyed)

### Data Synchronization

Changes made in Python are immediately reflected in C structures:

```python
# Python modification
ch.hp = 50

# C code immediately sees the change
if(ch->hp < ch->max_hp) {
    // This condition reflects the Python change
}
```

### Memory Management

The integration uses Python's reference counting combined with careful C memory management:

- **Borrowed References**: Temporary access without ownership
- **Owned References**: Full ownership requiring cleanup
- **Automatic Cleanup**: Wrappers are cleaned up when C objects are destroyed

## See Also

- [Auxiliary Data System](auxiliary-data.md) - For extending objects with custom data
- [Prototype System](prototypes.md) - For template-based content creation
- [Security Guide](../tutorials/security-best-practices.md) - Detailed security practices
- [Scripting Reference](../reference/scripting-api.md) - Complete API documentation