# NakedMud: A Guide for Programmers

## Introduction

This manual provides a basic introduction to the concepts in NakedMud's code. It explains important aspects of NakedMud in plain English and includes code examples to demonstrate how to use its features. While this guide covers the fundamentals, more advanced usage and examples can be found in the source code, particularly in the header files.

## Table of Contents

1. [Modules](#modules)
2. [Commands](#commands)
3. [Hooks](#hooks)
4. [Events](#events)
5. [Actions](#actions)
6. [Storage Sets](#storage-sets)
7. [Auxiliary Data](#auxiliary-data)
8. [Exposing Data to Python](#exposing-data-to-python)

## Modules

Almost all new extensions to NakedMud are added through modules. A module is a directory containing source files that are conceptually related. For example, you might have a module for combat mechanics, magic systems, or commands that give your MUD a specific look and feel.

### Benefits of Modular Design

- **Organization**: Code is grouped by concept, making it easier to locate and maintain.
- **Maintainability**: Changes are isolated to specific modules, reducing side effects.
- **Portability**: Modules can be easily shared or distributed.
- **Upgradability**: Core updates are simpler when most custom code is in modules.

### Creating a Module

There are six steps to create a module:

1. Create a directory for your module
2. Create a `module.mk` file
3. Add an entry to the main Makefile
4. Define your module in `mud.h`
5. Initialize your module in `gameloop.c`
6. Write your module's code

### 1. Create a Directory

Create a new folder in NakedMud's `src` directory. Name it to reflect your module's purpose (e.g., "combat", "magic").

### 2. Create a module.mk File

In your module's directory, create a `module.mk` file. This file tells the build system which files to compile and any required compiler flags or libraries.

Example `module.mk` for a module named "foo":

```makefile
# include our source code
SRC += foo/bar.c

# include our required libraries
LIBS += -labc

# and our compiler flags
C_FLAGS += -xyz
```

### 3. Add to Main Makefile

Edit the main `Makefile` in the `src` directory and add your module's directory to the `MODULES` variable.

### 4. Define Module in mud.h

Add a definition for your module in `mud.h` to allow other modules to check for its presence. This is done using preprocessor directives:

```c
#define MODULE_FOO
```

### 5. Initialize Your Module

Create an initialization function for your module and call it from `main()` in `gameloop.c`:

```c
void init_your_module(void) {
    // Initialization code here
}
```

### 6. Write Your Module Code

Now you can write your module's functionality. A simple example module might look like this:

```c
// hello.h
#ifndef HELLO_H
#define HELLO_H

// Initialize the hello module
void init_hello(void);

// Get the name of the last person to use the hello command
const char *last_hello_user(void);

#endif // HELLO_H

// hello.c
#include "../mud.h"
#include "../character.h"
#include "hello.h"

// Store the name of the last user
static char *last_hello_user_name = NULL;

// The hello command implementation
COMMAND(cmd_hello) {
    send_to_char(ch, "Hello, world!\r\n");
    free(last_hello_user_name);
    last_hello_user_name = strdup(charGetName(ch));
}

// Initialize the hello module
void init_hello(void) {
    last_hello_user_name = strdup("");
    add_cmd("hello", NULL, cmd_hello, 0, POS_SITTING, POS_FLYING,
           "player", FALSE, FALSE);
}

// Get the last user of the hello command
const char *last_hello_user(void) {
    return last_hello_user_name;
}
```

## Commands

Commands are functions that players can execute in the game (e.g., `look`, `north`, `inventory`).

### Defining a New Command

Commands are defined using the `COMMAND` macro, which expands to a function with the following signature:

```c
void cmd_name(CHAR_DATA *ch, const char *cmd, char *arg)
```

Where:
- `ch`: The character executing the command
- `cmd`: The command string that was typed
- `arg`: The arguments provided with the command

Example:

```c
COMMAND(cmd_mycommand) {
    send_to_char(ch, "You used my command with argument: %s\r\n", arg);
}
```

### Parsing Command Arguments

For commands that need to parse complex arguments, use the `parse_args` function:

```c
bool parse_args(CHAR_DATA *ch, bool show_errors, const char *cmd, char *args,
                const char *syntax, ...)
```

Example:

```c
COMMAND(cmd_give) {
    CHAR_DATA *receiver = NULL;
    void *to_give = NULL;
    bool multiple = FALSE;
    
    if (!parse_args(ch, TRUE, cmd, arg, "obj.inv.multiple [to] ch.room.noself",
                    &to_give, &multiple, &receiver))
        return;
        
    // Handle single item
    if (!multiple) {
        do_give(ch, receiver, to_give);
    }
    // Handle multiple items
    else {
        LIST_ITERATOR *obj_i = newListIterator(to_give);
        OBJ_DATA *obj = NULL;
        ITERATE_LIST(obj, obj_i) {
            do_give(ch, receiver, obj);
        } 
        deleteListIterator(obj_i);
        deleteList(to_give);
    }
}
```

### Argument Types and Suffixes

| Type    | Description                          |
|---------|--------------------------------------|
| ch      | Character reference                  |
| obj     | Object reference                     |
| room    | Room reference                       |
| exit    | Exit reference                       |
| word    | Single word                          |
| int     | Integer value                        |
| double  | Floating-point value                 |
| bool    | Boolean value                        |
| string  | Full remaining argument as string    |

Suffixes can be added to refine searches:

| Suffix     | Applies To   | Description                                  |
|------------|--------------|----------------------------------------------|
| .world     | ch, obj      | Search the entire game world                 |
| .room      | ch, obj      | Search the current room                      |
| .inv       | obj          | Search the character's inventory             |
| .eq        | obj          | Search the character's equipment             |
| .multiple  | ch, obj, exit| Return multiple matches if they exist        |
| .noself    | ch           | Exclude the command issuer from results      |
| .invis_ok  | ch, obj, exit| Override visibility checks                   |

### Adding Commands to the MUD

Use the `add_cmd` function to register a command:

```c
void add_cmd(const char *name, const char *abbrev, COMMAND(func),
             int min_pos, int max_pos, const char *user_group, bool mob_ok,
             bool interrupts)
```

Example:

```c
add_cmd("hello", NULL, cmd_hello, 0, POS_STANDING, "player", FALSE, FALSE);
```

## Hooks

Hooks allow you to attach functions to specific game events, enabling you to extend functionality without modifying core code.

### Adding a Hook

Use `hookAdd` to attach a function to an event:

```c
void hookAdd(const char *hook_type, HOOK_FUNC *hook_func);
```

Example:

```c
void my_hook(CHAR_DATA *giver, CHAR_DATA *receiver, OBJ_DATA *obj) {
    // Handle the give event
}

void init_my_module(void) {
    hookAdd("give", my_hook);
}
```

### Available Hook Types

| Signal   | Arguments               | Description                          |
|----------|-------------------------|--------------------------------------|
| give     | giver, receiver, object | When an item is given                |
| get      | taker, object           | When an item is picked up            |
| drop     | dropper, object         | When an item is dropped              |
| enter    | mover, new_room         | When a character enters a room       |
| exit     | mover, old_room, exit   | When a character leaves a room       |
| ask      | speaker, listener, text | When a character asks a question     |
| say      | speaker, text           | When a character speaks              |
| greet    | greeter, greeted        | When characters greet each other     |
| wear     | wearer, object          | When an item is worn                 |
| remove   | remover, object         | When an item is removed              |
| reset    | zone                    | When a zone resets                   |
| shutdown | -                       | When the MUD shuts down              |

### Creating New Hook Types

To create a new hook type, call `hookRun` when the event occurs:

```c
void hookRun(const char *hook_type, void *arg1, void *arg2, void *arg3);
```

Example:

```c
// When a character dies
void handle_death(CHAR_DATA *killer, CHAR_DATA *victim) {
    // Game logic...
    
    // Run death hooks
    hookRun("death", killer, victim, NULL);
}
```

### Removing Hooks

Use `hookRemove` to detach a hook:

```c
void hookRemove(const char *hook_type, HOOK_FUNC *hook_func);
```

## Events and Actions

NakedMud provides two related systems for handling delayed or interruptible actions: Events and Actions.

### Events

Events are simple delayed function calls that execute after a specified time period.

#### Creating an Event

Use `start_event` to schedule an event:

```c
void start_event(void *owner, int delay, void *on_complete,
                 void *check_involvement, void *data, const char *arg);
```

Example:

```c
void delayed_message(CHAR_DATA *ch, void *data, char *arg) {
    send_to_char(ch, "Your delayed message: %s\r\n", arg);
}

COMMAND(cmd_delay) {
    if (!*arg) {
        send_to_char(ch, "What do you want to say after a delay?\r\n");
        return;
    }
    
    start_event(ch, 5 * PULSE_PER_SEC, delayed_message, NULL, NULL, arg);
    send_to_char(ch, "Your message will be displayed in 5 seconds.\r\n");
}
```

### Actions

Actions are similar to events but are tied to a character and can be interrupted by movement, combat, or other actions.

#### Creating an Action

Use `start_action` to create an action:

```c
void start_action(CHAR_DATA *actor, int delay, bitvector_t where, 
                 void *on_complete, void *on_interrupt, void *data,
                 const char *arg);
```

Example:

```c
void cast_spell(CHAR_DATA *ch, void *data, char *arg) {
    send_to_char(ch, "You finish casting your spell!\r\n");
    // Spell effect here
}

void interrupt_spell(CHAR_DATA *ch, void *data, char *arg) {
    send_to_char(ch, "Your spell was interrupted!\r\n");
}

COMMAND(cmd_cast) {
    if (!*arg) {
        send_to_char(ch, "Cast what spell?\r\n");
        return;
    }
    
    start_action(ch, 3 * PULSE_PER_SEC, 1, cast_spell, interrupt_spell, NULL, arg);
    send_to_char(ch, "You begin casting %s...\r\n", arg);
}
```

### Action Flags

The `where` parameter in `start_action` determines what can interrupt the action. It's a bitvector where you can combine these flags:

| Flag        | Description                                      |
|-------------|--------------------------------------------------|
| POS_DEAD    | Action continues even if character dies          |
| POS_MORTAL  | Action continues if mortally wounded             |
| POS_INCAP   | Action continues if incapacitated                |
| POS_STUNNED | Action continues if stunned                      |
| POS_SLEEPING| Action continues if sleeping                     |
| POS_RESTING | Action continues if resting                      |
| POS_SITTING | Action continues if sitting                      |
| POS_FIGHTING| Action continues if in combat                   |
| POS_STANDING| Action continues if standing                     |

## Storage Sets

Storage sets are NakedMud's primary method for saving and loading game data. They provide a way to serialize complex data structures to disk and restore them later.

### Basic Usage

A storage set is a key-value store where keys are strings and values can be:
- Strings
- Integers
- Long integers
- Doubles
- Booleans
- Nested storage sets
- Lists of storage sets

### Creating and Using Storage Sets

```c
// Create a new storage set
STORAGE_SET *set = new_storage_set();

// Store values
store_string(set, "name", "Player Name");
store_int(set, "level", 50);
store_bool(set, "is_admin", TRUE);

// Save to file
storage_write(set, "player.dat");

// Later, load it back
STORAGE_SET *loaded = storage_read("player.dat");
if (loaded) {
    const char *name = read_string(loaded, "name");
    int level = read_int(loaded, "level");
    bool is_admin = read_bool(loaded, "is_admin");
    
    // Clean up when done
    storage_close(loaded);
}

// Always free the original set
storage_close(set);
```

### Working with Nested Data

```c
// Create a nested structure
STORAGE_SET *player = new_storage_set();
STORAGE_SET *inventory = new_storage_set();
STORAGE_SET *equipment = new_storage_set();

// Store nested data
store_set(player, "inventory", inventory);
store_set(player, "equipment", equipment);

// Store list of items
STORAGE_SET_LIST *items = new_storage_list();
STORAGE_SET *item1 = new_storage_set();
STORAGE_SET *item2 = new_storage_set();

store_string(item1, "name", "Sword");
store_int(item1, "damage", 10);
store_string(item2, "name", "Shield");
store_int(item2, "defense", 5);

storage_list_put(items, item1);
storage_list_put(items, item2);
store_list(player, "items", items);

// Save and clean up
storage_write(player, "player_data.dat");
storage_close(player);
```

## Auxiliary Data

Auxiliary data allows you to extend NakedMud's core data types (characters, objects, rooms) with custom data without modifying the core code.

### Creating Auxiliary Data

To create auxiliary data, you need to define several functions:

```c
typedef struct {
    int num_saves;
    int num_loads;
} SAVE_DATA;

// Create new save data
SAVE_DATA *new_save_data(void) {
    SAVE_DATA *data = calloc(1, sizeof(SAVE_DATA));
    data->num_saves = 0;
    data->num_loads = 0;
    return data;
}

// Delete save data
void delete_save_data(SAVE_DATA *data) {
    free(data);
}

// Copy save data
SAVE_DATA *save_data_copy(SAVE_DATA *src) {
    SAVE_DATA *dest = new_save_data();
    dest->num_saves = src->num_saves;
    dest->num_loads = src->num_loads;
    return dest;
}

// Save to storage set
STORAGE_SET *save_data_store(SAVE_DATA *data) {
    STORAGE_SET *set = new_storage_set();
    store_int(set, "saves", data->num_saves + 1);
    store_int(set, "loads", data->num_loads);
    return set;
}

// Load from storage set
SAVE_DATA *save_data_read(STORAGE_SET *set) {
    SAVE_DATA *data = new_save_data();
    data->num_saves = read_int(set, "saves");
    data->num_loads = read_int(set, "loads") + 1;
    return data;
}

// Copy data to another instance
void save_data_copy_to(SAVE_DATA *from, SAVE_DATA *to) {
    to->num_saves = from->num_saves;
    to->num_loads = from->num_loads;
}
```

### Registering Auxiliary Data

Register your auxiliary data during module initialization:

```c
void init_my_module(void) {
    // Create auxiliary function structure
    AUXILIARY_FUNCS *funcs = new_auxiliary_funcs(
        AUXILIARY_TYPE_CHAR,  // Type of data this is for
        (void *(*)(void))new_save_data,
        (void (*)(void *))delete_save_data,
        (void (*)(void *, void *))save_data_copy_to,
        (void *(*)(void *))save_data_copy,
        (STORAGE_SET *(*)(void *))save_data_store,
        (void *(*)(STORAGE_SET *))save_data_read
    );
    
    // Register with the auxiliary system
    auxiliaries_install("save_data", funcs);
}
```

### Using Auxiliary Data

Access your auxiliary data from anywhere in the code:

```c
// Get auxiliary data (creates it if it doesn't exist)
SAVE_DATA *data = charGetAuxiliaryData(ch, "save_data");

// Update the data
data->num_saves++;

// Save the character (this will automatically call save_data_store)
charSave(ch);
```

### Best Practices

1. **Memory Management**: Always provide proper cleanup functions to prevent memory leaks.
2. **Type Safety**: Use proper type casting when working with auxiliary data.
3. **Error Handling**: Check for NULL returns when retrieving auxiliary data.
4. **Namespace**: Use unique names for your auxiliary data to avoid conflicts with other modules.
5. **Performance**: Be mindful of the size of data you're storing in auxiliary data structures.

## Exposing Data to Python

NakedMud allows you to expose C functions and data structures to Python, enabling powerful scripting capabilities. This section covers how to make your C code accessible from Python scripts.

### Basic Python Integration

To expose a C function to Python, you need to:

1. Create a Python method definition
2. Register the method with the appropriate Python type
3. Handle Python objects and reference counting properly

### Example: Adding a Method to Character Class

Here's how to add a simple method to the Character class that can be called from Python:

```c
#include <Python.h>

// The C implementation of our Python method
static PyObject *char_say_hello(PyObject *self, PyObject *args) {
    CHAR_DATA *ch;
    
    // Parse the arguments (self is the Character object)
    if (!PyArg_ParseTuple(args, ""))
        return NULL;
        
    // Get the CHAR_DATA pointer from the Python object
    ch = PyChar_AsChar(self);
    if (!ch) {
        PyErr_SetString(PyExc_RuntimeError, "Invalid character object");
        return NULL;
    }
    
    // Call the MUD's say function
    do_say(ch, "Hello from Python!");
    
    // Return None
    Py_INCREF(Py_None);
    return Py_None;
}

// Method definition
static PyMethodDef CharMethods[] = {
    {"say_hello", char_say_hello, METH_VARARGS, "Make the character say hello"},
    {NULL, NULL, 0, NULL}  // Sentinel
};

// Initialize the Python module
void init_python_char(void) {
    // Get the PyChar type
    PyTypeObject *char_type = PyChar_Type();
    
    // Add our methods to the type
    PyType_Ready(char_type);
    PyDict_Merge(char_type->tp_dict, CharMethods, 1);
}
```

### Type Conversion

When working with Python, you'll often need to convert between Python objects and C types. Here are some common conversions:

| C Type | Python Type | Conversion Function |
|--------|-------------|----------------------|
| `int`  | `int`       | `PyLong_AsLong()`    |
| `char*`| `str`       | `PyUnicode_AsUTF8()` |
| `bool` | `bool`      | `PyObject_IsTrue()`  |
| `list` | `list`      | `PyList_*` functions |
| `dict` | `dict`      | `PyDict_*` functions |

### Error Handling

Proper error handling is crucial when exposing C functions to Python:

```c
// Example with error handling
static PyObject *get_character_level(PyObject *self, PyObject *args) {
    CHAR_DATA *ch;
    
    if (!PyArg_ParseTuple(args, ""))
        return NULL;
        
    ch = PyChar_AsChar(self);
    if (!ch) {
        PyErr_SetString(PyExc_RuntimeError, "Invalid character object");
        return NULL;
    }
    
    if (!CHAR_IS_PC(ch)) {
        PyErr_SetString(PyExc_TypeError, "Character is not a player");
        return NULL;
    }
    
    return PyLong_FromLong(charGetLevel(ch));
}
```

### Security Considerations

When exposing C functions to Python, keep these security considerations in mind:

1. **Input Validation**: Always validate input from Python before using it in C code.
2. **Memory Management**: Be careful with memory allocation and deallocation.
3. **Reference Counting**: Properly manage Python reference counts to prevent memory leaks.
4. **Sandboxing**: Consider using Python's restricted execution modes if allowing untrusted scripts.

### Example: Python Script

Here's how the Python code might look to use the exposed methods:

```python
def on_enter_room(char, room):
    # Call our custom method
    char.say_hello()
    
    # Get the character's level
    level = char.get_level()
    
    # Do something based on level
    if level > 50:
        char.send("You're very experienced!\n")
```

### Best Practices

1. **Keep It Simple**: Expose only what's necessary to Python.
2. **Documentation**: Document your Python API thoroughly.
3. **Error Messages**: Provide clear error messages for Python developers.
4. **Thread Safety**: Be aware of threading issues when Python and C interact.
5. **Testing**: Thoroughly test all exposed functions with various inputs.

For more advanced Python integration, refer to the Python/C API documentation and study the existing Python integration in NakedMud's source code.
