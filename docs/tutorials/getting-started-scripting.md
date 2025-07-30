---
layout: default
title: Getting Started with Python Scripting
parent: Start with the Basics
grand_parent: Tutorials
nav_order: 1
permalink: /tutorials/getting-started-scripting/
---

# Getting Started with Python Scripting

Learn the fundamentals of Python scripting in NakedMud, from basic concepts to your first working script.

## Overview

This tutorial introduces you to Python scripting in NakedMud. You'll learn how to write, test, and debug Python scripts that interact with the mud's core systems. By the end, you'll have created your first functional script and understand the basic patterns used throughout NakedMud development.

## Prerequisites

- Basic Python programming knowledge
- Access to a NakedMud installation with wizard privileges
- Familiarity with mud terminology (rooms, characters, objects)

## What You'll Learn

- How Python integrates with NakedMud's C core
- Basic script structure and organization
- Using the core Python modules
- Testing and debugging techniques
- Best practices for mud scripting

## Step 1: Understanding the Environment

NakedMud runs Python scripts in a restricted environment for security. Let's explore what's available:

```python
# Connect to your mud and use the Python command to test
# Type: python
# Then enter this code:

import mudsys
print("Available modules:", dir())
print("MudSys functions:", [f for f in dir(mudsys) if not f.startswith('_')])
```

This shows you the available modules and functions. The core modules you'll use most often are:
- `mudsys` - Core mud system functions
- `char` - Character manipulation
- `room` - Room and world functions
- `obj` - Object handling

## Step 2: Your First Script

Let's create a simple script that responds to a command. Create a new file in your mud's Python modules directory:

```python
# File: lib/pymodules/tutorial_basics.py

import mudsys
import char

def cmd_hello(ch, cmd, arg):
    """A simple hello command that demonstrates basic scripting."""
    
    # Get the character's name
    char_name = char.charGetName(ch)
    
    # Send a message to the character
    char.charSend(ch, "Hello, %s! Welcome to Python scripting." % char_name)
    
    # Send a message to others in the room
    char.charSendRoom(ch, "%s waves hello to everyone." % char_name)
    
    # Log the command usage
    mudsys.log_string("Player %s used the hello command." % char_name)

# Register the command with the mud
mudsys.add_cmd("hello", None, cmd_hello, "player", 1)
```

## Step 3: Testing Your Script

1. Save the file in `lib/pymodules/tutorial_basics.py`
2. Restart your mud or use the `pyload` command if available
3. Test the command by typing `hello` in-game

You should see:
```
Hello, YourName! Welcome to Python scripting.
```

And others in the room should see:
```
YourName waves hello to everyone.
```

## Step 4: Understanding the Code

Let's break down what happened:

### Function Parameters
```python
def cmd_hello(ch, cmd, arg):
```
- `ch` - The character object executing the command
- `cmd` - The command string that was typed
- `arg` - Any arguments passed with the command

### Character Functions
```python
char_name = char.charGetName(ch)
char.charSend(ch, "message")
char.charSendRoom(ch, "message")
```
These functions get character information and send messages.

### Command Registration
```python
mudsys.add_cmd("hello", None, cmd_hello, "player", 1)
```
- `"hello"` - The command name
- `None` - No abbreviation restrictions
- `cmd_hello` - The function to call
- `"player"` - Minimum user level required
- `1` - Minimum position (standing, sitting, etc.)

## Step 5: Adding Arguments

Let's enhance the command to accept arguments:

```python
def cmd_hello(ch, cmd, arg):
    """Enhanced hello command with argument support."""
    
    char_name = char.charGetName(ch)
    
    if not arg:
        # No argument provided
        char.charSend(ch, "Hello, %s! You can also try 'hello <name>'." % char_name)
        char.charSendRoom(ch, "%s waves hello to everyone." % char_name)
    else:
        # Argument provided - greet specific person
        target_name = arg.strip()
        char.charSend(ch, "You say hello to %s!" % target_name)
        char.charSendRoom(ch, "%s says hello to %s." % (char_name, target_name))
    
    mudsys.log_string("Player %s used hello command with arg: '%s'" % (char_name, arg))
```

## Step 6: Error Handling

Good scripts handle errors gracefully:

```python
def cmd_hello(ch, cmd, arg):
    """Hello command with proper error handling."""
    
    try:
        char_name = char.charGetName(ch)
        
        if not arg:
            char.charSend(ch, "Hello, %s!" % char_name)
            char.charSendRoom(ch, "%s waves hello." % char_name)
        else:
            target_name = arg.strip()
            if len(target_name) > 20:  # Reasonable name length limit
                char.charSend(ch, "That name is too long!")
                return
                
            char.charSend(ch, "You say hello to %s!" % target_name)
            char.charSendRoom(ch, "%s says hello to %s." % (char_name, target_name))
            
    except Exception as e:
        # Log errors for debugging
        mudsys.log_string("Error in hello command: %s" % str(e))
        char.charSend(ch, "Something went wrong with the hello command.")
```

## Step 7: Using Auxiliary Data

Let's add a feature that remembers how many times someone has used the command:

```python
import auxiliary

def cmd_hello(ch, cmd, arg):
    """Hello command that tracks usage with auxiliary data."""
    
    try:
        char_name = char.charGetName(ch)
        
        # Get current usage count from auxiliary data
        usage_count = auxiliary.charGetAuxiliaryData(ch, "hello_count")
        if usage_count is None:
            usage_count = 0
        else:
            usage_count = int(usage_count)
        
        # Increment and store the count
        usage_count += 1
        auxiliary.charSetAuxiliaryData(ch, "hello_count", str(usage_count))
        
        # Customize message based on usage
        if usage_count == 1:
            message = "Hello, %s! This is your first time using this command." % char_name
        elif usage_count < 5:
            message = "Hello again, %s! You've used this command %d times." % (char_name, usage_count)
        else:
            message = "Hello, %s! You're quite friendly - %d hellos so far!" % (char_name, usage_count)
        
        char.charSend(ch, message)
        char.charSendRoom(ch, "%s waves hello enthusiastically." % char_name)
        
    except Exception as e:
        mudsys.log_string("Error in hello command: %s" % str(e))
        char.charSend(ch, "Something went wrong with the hello command.")
```

## Step 8: Debugging Tips

When your scripts don't work as expected:

### 1. Check the Logs
```python
mudsys.log_string("Debug: Variable value is %s" % some_variable)
```

### 2. Use Try-Catch Blocks
```python
try:
    # Your code here
    pass
except Exception as e:
    mudsys.log_string("Error: %s" % str(e))
    # Handle the error gracefully
```

### 3. Test Incrementally
Start with simple functionality and add complexity gradually.

### 4. Verify Module Loading
```python
# In-game, use the python command:
import sys
print("tutorial_basics" in sys.modules)
```

## Common Patterns

### Command Structure
```python
def cmd_name(ch, cmd, arg):
    """Command description."""
    try:
        # Validate input
        if not some_condition:
            char.charSend(ch, "Error message")
            return
        
        # Do the work
        result = do_something()
        
        # Provide feedback
        char.charSend(ch, "Success message")
        
    except Exception as e:
        mudsys.log_string("Error in cmd_name: %s" % str(e))
        char.charSend(ch, "Something went wrong.")

# Register the command
mudsys.add_cmd("name", None, cmd_name, "player", 1)
```

### Working with Objects
```python
# Always check if objects exist
if ch is None:
    return
    
# Get object properties safely
name = char.charGetName(ch) if ch else "Unknown"
```

## Next Steps

Now that you understand the basics:

1. **Try the [Your First NPC](your-first-npc/) tutorial** to learn about character prototypes
2. **Explore [Building Your First Room](building-your-first-room/)** for world creation
3. **Read about [Basic Triggers and Scripts](basic-triggers-scripts/)** for event-driven programming

## Summary

You've learned:
- How to create and register commands
- Basic character interaction functions
- Error handling best practices
- Using auxiliary data for persistence
- Debugging techniques

## Troubleshooting

**Command not working?**
- Check that the file is in the correct directory
- Verify the mud has been restarted or the module reloaded
- Look for error messages in the mud logs

**Getting permission errors?**
- Ensure you have wizard privileges
- Check the command registration parameters

**Python errors?**
- Review the syntax carefully
- Check for proper indentation
- Verify all imports are correct

Ready to build more complex functionality? Continue with the [Your First NPC](your-first-npc/) tutorial!