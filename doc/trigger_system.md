# NakedMud Trigger System

## Overview

The trigger system in NakedMud provides a powerful way to attach Python scripts to game objects (rooms, mobiles, objects) that execute automatically when specific events occur. Triggers are the bridge between the C game engine and Python scripting, allowing builders to create dynamic, interactive content without modifying the core codebase.

## What Are Triggers?

Triggers are Python scripts that:
- Attach to game entities (rooms, mobiles, objects)
- Execute automatically when specific events occur
- Have access to contextual variables (characters, objects, commands, etc.)
- Can modify game state, send messages, create objects, etc.

## Trigger System Architecture

```
Game Event Occurs
        |
        v
┌─────────────────┐
│   Hook System   │ ← hookRun("event_name", info)
│   (hooks.c)     │
└─────────┬───────┘
          |
          v
┌─────────────────┐
│  Trigger Hook   │ ← do_<event>_trighooks(info)
│  Handler        │
│ (trighooks.c)   │
└─────────┬───────┘
          |
          v
┌─────────────────┐
│ Find Entities   │ ← Iterate through relevant lists
│ with Triggers   │   (mobile_list, object_list, etc.)
└─────────┬───────┘
          |
          v
┌─────────────────┐
│ Filter by Type  │ ← Check if entity has triggers of
│ and Existence   │   the specific type
└─────────┬───────┘
          |
          v
┌─────────────────┐
│  gen_do_trigs   │ ← Prepare Python environment
│                 │   and context variables
└─────────┬───────┘
          |
          v
┌─────────────────┐
│ Execute Python  │ ← Run individual trigger scripts
│ Trigger Scripts │   with restricted environment
└─────────────────┘
```

## Available Trigger Types

| Trigger Type | Usable By | Description | Context Variables |
|--------------|-----------|-------------|-------------------|
| `speech` | mob, room | When someone speaks | `ch`, `cmd`, `arg` |
| `greet` | mob | When someone enters the room | `ch` |
| `enter` | mob, room | When someone enters | `ch` |
| `exit` | mob, room | When someone leaves | `ch` |
| `self enter` | mob | When the mob enters a room | - |
| `self exit` | mob | When the mob leaves a room | - |
| `drop` | obj, room | When object is dropped | `ch`, `obj` |
| `get` | obj, room | When object is picked up | `ch`, `obj` |
| `give` | obj, mob | When object is given | `ch`, `obj` |
| `receive` | mob | When mob receives an object | `ch`, `obj` |
| `wear` | obj, mob | When object is worn | `ch`, `obj` |
| `remove` | obj, mob | When object is removed | `ch`, `obj` |
| `reset` | room | When room resets | - |
| `look` | obj, mob, room | When something is examined | `ch` |
| `open` | obj, room | When something is opened | `ch` |
| `close` | obj, room | When something is closed | `ch` |
| `to_game` | obj, mob, room | When entity enters the game | - |
| `heartbeat` | obj, mob | Every 2 seconds (pulse) | - |
| `pre_command` | obj, mob, room | Before any command execution | `ch`, `cmd`, `arg` |

## Pre-Command Trigger

The `pre_command` trigger is a special trigger that fires before any command is executed, allowing you to intercept, modify, or block commands. This is useful for creating custom commands, handling typos, or adding special behaviors to NPCs and objects.

### Context Variables
- `ch` - The character executing the command
- `cmd` - The command name (string)
- `arg` - The command arguments (string)

### Blocking Commands
To prevent the normal command from executing, set the `pc_block_command` dynamic variable on the character:

```python
# Block the command
ch.setvar("pc_block_command", 1)
```

**Important:** The system automatically resets this flag to 0 after checking it, so you don't need to manually clear it.

### Usage Examples

```python
# NPC responding to commands directed at them
if cmd == "greet" and ch.name == "player":
    me.send("The shopkeeper nods politely.")
    ch.setvar("pc_block_command", 1)

# Object with custom commands  
if cmd == "push" and "button" in arg:
    ch.send("You push the mysterious button.")
    # trigger some effect
    ch.setvar("pc_block_command", 1)

# Room handling specific commands
if cmd == "xyzzy":
    ch.send("A hollow voice says 'Fool.'")
    ch.setvar("pc_block_command", 1)
```

#### Command Logging
```python
# Log all commands for debugging
import mudsys
if valid:
    mudsys.log_string(f"VALID: {ch.name} used '{cmd} {arg}'")
else:
    mudsys.log_string(f"INVALID: {ch.name} tried '{cmd} {arg}'")
# Don't block - let command proceed normally
```

### Trigger Priority
Pre-command triggers are checked in this order:
1. **Self** (triggers on the character executing the command)
2. **Inventory** (triggers on carried items)
3. **Room inventory** (triggers on NPCs and objects in the room)
4. **Room** (triggers on the room itself)

The first trigger that sets `pc_block_command` will prevent further triggers and the original command from executing.

## Using Triggers in OLC

### Creating Triggers

1. **Edit the entity** (room, mobile, or object):
   ```
   redit <vnum>    # For rooms
   medit <vnum>    # For mobiles  
   oedit <vnum>    # For objects
   ```

2. **Access trigger menu**:
   ```
   T               # Select trigger menu
   ```

3. **Add a new trigger**:
   ```
   N               # Add new trigger
   <trigger_key>   # Enter unique key for the trigger
   ```

4. **Edit the trigger**:
   ```
   tedit <trigger_key>
   ```

5. **Set trigger properties**:
   ```
   1               # Set trigger name
   2               # Set trigger type (choose from available types)
   3               # Edit Python script
   ```

### Example Trigger Script

```python
# A simple greeting trigger for a mob
import mudsys

# This trigger runs when someone enters the room
if ch.name != me.name:  # Don't greet yourself
    me.send("say Welcome to my shop, %s!" % ch.name)
    
    # Check if it's a specific player
    if ch.name.lower() == "admin":
        me.send("bow " + ch.name)
        me.send("say It's an honor to meet you, my lord!")
```

## Implementing a New Trigger Type

### Step 1: Add the Hook Handler Function

Add a new handler function in `src/scripts/trighooks.c`:

```c
void do_my_event_trighooks(const char *info) {
  // Parse the hook info to extract relevant data
  CHAR_DATA *ch = NULL;
  OBJ_DATA *obj = NULL;
  // ... parse other variables as needed
  hookParseInfo(info, &ch, &obj);
  
  // Determine which entities should have triggers run
  // Example: Run on all objects in the character's inventory
  if (ch && charGetInventory(ch)) {
    LIST_ITERATOR *obj_i = newListIterator(charGetInventory(ch));
    OBJ_DATA *inv_obj = NULL;
    ITERATE_LIST(inv_obj, obj_i) {
      if (listSize(objGetTriggers(inv_obj)) > 0) {
        gen_do_trigs(inv_obj, TRIGVAR_OBJ, "my_event", 
                     ch, obj, charGetRoom(ch), NULL, 
                     NULL, NULL, NULL);
      }
    } deleteListIterator(obj_i);
  }
}
```

### Step 2: Register the Hook and Trigger Type

In the `init_trighooks()` function in `src/scripts/trighooks.c`:

```c
void init_trighooks(void) {
  // ... existing hook registrations ...
  
  // Add your new hook
  hookAdd("my_event", do_my_event_trighooks);
  
  // ... existing trigger type registrations ...
  
  // Add your new trigger type to OLC
  register_tedit_opt("my_event", "obj, mob, room");
}
```

### Step 3: Call the Hook from Game Code

In the appropriate place in the game code where your event occurs:

```c
// Example: In a command function
COMMAND(cmd_my_command) {
  // ... command logic ...
  
  // Trigger the event
  hookRun("my_event", hookBuildInfo("ch obj", ch, obj));
}
```

### Step 4: Build and Test

```bash
cd src
scons -c && scons
```

## Context Variables in Triggers

Triggers have access to several predefined variables:

- `me` - The entity that owns the trigger (room, mob, or object)
- `ch` - The character involved in the event (if applicable)
- `obj` - The object involved in the event (if applicable)
- `room` - The room where the event occurred (if applicable)
- `cmd` - The command that triggered the event (if applicable)
- `arg` - Arguments to the command (if applicable)

## Best Practices

### Performance
- Only attach triggers to entities that need them
- Keep trigger scripts efficient - they run frequently
- Use heartbeat triggers sparingly (they run every 2 seconds)

### Security
- Triggers run in a restricted Python environment
- They cannot import arbitrary modules
- File system access is limited

### Debugging
- Use `mudsys.log()` to debug trigger execution
- Test triggers thoroughly before deploying
- Use descriptive trigger names and keys

### Organization
- Use consistent naming conventions for trigger keys
- Group related triggers logically
- Document complex trigger interactions

## Advanced Usage

### Trigger Communication
Triggers can communicate through:
- Global variables (use sparingly)
- Object/room/character properties
- The event system

### Conditional Execution
```python
# Only run during certain times
import time
current_hour = time.time() // 3600 % 24
if 6 <= current_hour <= 18:  # Daytime only
    # ... trigger logic ...
```

### State Management
```python
# Use auxiliary data for persistent state
if not hasattr(me, 'visit_count'):
    me.visit_count = 0
me.visit_count += 1

if me.visit_count == 1:
    me.send("say First time here? Welcome!")
else:
    me.send("say Welcome back! Visit #%d" % me.visit_count)
```

## Troubleshooting

### Common Issues
1. **Trigger not firing**: Check trigger type matches the event
2. **Python errors**: Check syntax and available variables
3. **Performance issues**: Review trigger frequency and complexity
4. **Context variables missing**: Verify the trigger type provides needed variables

### Debugging Tips
1. Add logging statements to track execution
2. Test with simple triggers first
3. Check the mud logs for Python errors
4. Verify trigger is attached to the correct entity type

## Related Files

- `src/scripts/trighooks.c` - Trigger hook handlers
- `src/scripts/trighooks.h` - Trigger system headers
- `src/scripts/trigedit.c` - Trigger OLC editor
- `src/scripts/triggers.c` - Core trigger data structures
- `src/scripts/scripts.c` - Python script integration
- `src/hooks.c` - Hook system implementation
