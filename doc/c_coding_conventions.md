# NakedMud C Coding Conventions
**Maintainer**: LimpingNinja (Kevin Morgan)

## Introduction

This document outlines the coding conventions used in NakedMud 4.1. While some of these conventions might seem unconventional, they serve specific purposes in maintaining code clarity and modularity. The original function naming system was designed by Geoff Hollis to enforce proper encapsulation and reduce bugs by encouraging the reuse of tested functions.

## Function Naming Conventions

### The Two-Case System

NakedMud uses a dual naming convention to distinguish between different types of functions:

1. **CamelCase**: For functions that directly interact with data structures (getters, setters, and basic operations)
2. **snake_case**: For functions that perform actual functionality (business logic, complex operations)

### CamelCase Functions (Data Structure Interface)

These functions follow the pattern: `[datatype][routine][target]`

**Examples:**
- `roomGetName()` - Get the name of a room
- `charSetSocket()` - Set the socket for a character
- `listPut()` - Put an item in a list
- `hashGet()` - Get a value from a hashtable
- `exitSetClosed()` - Set an exit as closed

**Special Cases for Creation/Deletion:**
- `new[Datatype]()` - Create new instances (e.g., `newList()`, `newChar()`)
- `delete[Datatype]()` - Delete instances (e.g., `deleteList()`, `deleteChar()`)

### snake_case Functions (Business Logic)

These functions perform actual game functionality and complex operations:

**Examples:**
- `send_to_char()` - Send a message to a character
- `close_socket()` - Close a socket connection
- `game_loop()` - Main game loop
- `extract_mobile()` - Remove a character from the game
- `init_scripts()` - Initialize the scripting system
- `save_account()` - Save account data

## Data Structure Conventions

### Typedef Naming

All major data structures use `ALL_CAPS` with `_DATA` suffix:

```c
typedef struct socket_data    SOCKET_DATA;
typedef struct char_data      CHAR_DATA;
typedef struct room_data      ROOM_DATA;
typedef struct object_data    OBJ_DATA;
```

### Structure Member Access

- Use getter/setter functions instead of direct member access
- This enforces encapsulation and prevents bugs
- Example: Use `charGetName(ch)` instead of `ch->name`

## Macro and Constant Conventions

### Macro Naming

- Use `ALL_CAPS` with underscores for constants and macros
- Prefix with relevant module/system name when appropriate

**Examples:**
```c
#define MAX_BUFFER           4096
#define DFLT_START_ROOM     "tavern_entrance@examples"
#define POS_STANDING         3
#define BODYPOS_HEAD         1
```

### Iteration Macros

Special macros for clean iteration over data structures:

```c
#define ITERATE_LIST(var, it)     // Iterate over lists
#define ITERATE_HASH(key, val, it) // Iterate over hashtables
#define ITERATE_SET(elem, it)     // Iterate over sets
```

## Memory Management

### Consistent Patterns

- Always pair `new*()` with `delete*()`
- Use `strdupsafe()` for string duplication (handles NULL gracefully)
- Free resources in reverse order of allocation

**Example:**
```c
LIST *list = newList();
listPut(list, data);
// ... use list ...
deleteList(list);
```

### String Handling

- Use `strdupsafe()` instead of `strdup()` for NULL safety
- Always check for NULL before freeing strings
- Use buffers for dynamic string building

## Error Handling and Logging

### Logging Functions

- `log_string()` - General logging
- `bug()` - Bug reporting with file output
- Use descriptive error messages

### Return Value Conventions

- Return `NULL` for failed object creation/retrieval
- Return `TRUE`/`FALSE` for boolean operations
- Return `-1` for failed integer operations

## Module Organization

### Header Guards

Use double underscore prefix for header guards:

```c
#ifndef __MODULE_H
#define __MODULE_H
// ... content ...
#endif
```

### Module Initialization

- Each module has an `init_*()` function
- Modules register their functionality during initialization
- Use consistent naming: `init_scripts()`, `init_time()`, etc.

## Python Integration Conventions

### Python Module Functions

Python interface functions use descriptive names:

```c
PyMODINIT_FUNC PyInit_PyChar(void)
PyObject *PyChar_send(PyObject *self, PyObject *args)
```

### Python-C Bridge

- Use `Py*_As*()` functions to convert Python objects to C
- Always check for NULL returns from conversion functions
- Use `Py_BuildValue()` for return values

## Code Style Guidelines

### Indentation and Spacing

- Use 2-space indentation (consistent with existing code)
- Place opening braces on same line for functions
- Use spaces around operators

### Comments

- Use `//` for single-line comments
- Use `/* */` for multi-line comments
- Document complex algorithms and business logic
- Include author attribution for major changes

### Variable Naming

- Use descriptive names: `char_list` instead of `cl`
- Use `_i` suffix for iterators: `char_i`, `obj_i`
- Prefix global variables appropriately

## Best Practices

### Encapsulation

- Always use getter/setter functions for data access
- Keep structure definitions in source files, not headers
- Expose minimal interface in header files

### Function Design

- Keep functions focused on single responsibilities
- Use consistent parameter ordering (subject first, then modifiers)
- Validate input parameters

### Error Prevention

- Check for NULL pointers before dereferencing
- Use bounds checking for arrays and lists
- Initialize variables before use

## Example Code Structure

```c
// Good example following conventions
CHAR_DATA *ch = charLoad("player1");
if (ch != NULL) {
    const char *name = charGetName(ch);
    send_to_char(ch, "Welcome back, %s!", name);
    charSetRoom(ch, roomLoad("start_room"));
}

// Python integration example
PyObject *PyChar_getName(PyChar *self, PyObject *args) {
    CHAR_DATA *ch = PyChar_AsChar((PyObject *)self);
    if (ch == NULL) {
        PyErr_Format(PyExc_Exception, "Invalid character");
        return NULL;
    }
    return Py_BuildValue("s", charGetName(ch));
}
```

## Migration Notes

When working with existing code:

1. **Don't change existing naming** - maintain consistency with the codebase
2. **Follow established patterns** - look at similar functions for guidance
3. **Use existing data structures** - don't reinvent the wheel
4. **Test thoroughly** - the dual naming system helps catch interface violations

## Conclusion

While these conventions may seem unusual, they serve important purposes:

- **Modularity**: Clear separation between data access and business logic
- **Encapsulation**: Forced use of proper interfaces reduces bugs
- **Consistency**: Predictable naming makes code easier to navigate
- **Maintainability**: Clear patterns make the codebase easier to extend

Remember: the goal is not to have the "prettiest" code, but to have maintainable, bug-free code that multiple developers can work with effectively. These conventions have served NakedMud well through multiple versions and continue to provide value in the current codebase.

*Happy coding!*  

