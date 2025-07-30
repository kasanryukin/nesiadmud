---
layout: default
title: Basic Triggers and Scripts
parent: Start with the Basics
grand_parent: Tutorials
nav_order: 4
permalink: /tutorials/basic-triggers-scripts/
---

# Basic Triggers and Scripts

Learn to create event-driven behaviors using NakedMud's trigger system, from simple responses to complex interactive scenarios.

## Overview

This tutorial teaches you how to use NakedMud's trigger system to create event-driven behaviors. You'll learn about different trigger types, how to create responsive scripts, and how to build complex interactions that react to player actions and game events.

## Prerequisites

- Completed [Getting Started with Python Scripting](getting-started-scripting/)
- Completed [Your First NPC](your-first-npc/) and [Building Your First Room](building-your-first-room/)
- Understanding of [Core Concepts](/core-concepts/)
- Wizard-level access to your mud

## What You'll Learn

- Understanding trigger types and when they fire
- Creating responsive trigger scripts
- Managing trigger state and data
- Building complex trigger interactions
- Best practices for trigger design
- Debugging trigger systems

## Step 1: Understanding Trigger Types

NakedMud supports various trigger types that fire on different events:

### Character Triggers
- `enter_room` - When a character enters a room
- `leave_room` - When a character leaves a room
- `speech` - When someone speaks in the room
- `heartbeat` - Regular periodic trigger
- `death` - When the character dies
- `combat` - During combat situations

### Room Triggers
- `enter_room` - When someone enters the room
- `leave_room` - When someone leaves the room
- `look` - When someone looks at the room or objects
- `heartbeat` - Regular periodic trigger
- `speech` - When someone speaks in the room

### Object Triggers
- `get` - When the object is picked up
- `drop` - When the object is dropped
- `wear` - When the object is worn
- `remove` - When the object is removed
- `use` - When the object is used

Let's explore these with practical examples.

## Step 2: Creating Your First Trigger Script

Let's create a simple greeting system that responds to speech. This involves creating a trigger and then attaching it to an NPC.

### Step 2a: Create the Greeting Trigger

First, create the trigger itself:

```
# Create the greeting trigger:
tedit greeting_speech

# This opens the trigger editor:
# [greeting_speech]
# 1) Name        : An Unfinished Trigger
# 2) Trigger type: <NONE>
# 3) Script Code
```

Set up the trigger:

1. **Name**: `Simple greeting response`
2. **Trigger type**: `speech` (this makes it fire when someone speaks)
3. **Script Code**: Select this to edit the Python code

In the Script Code editor, replace the default code with:

```python
# Simple greeting trigger - responds to greetings in speech

import char
import random
import event

# Don't respond to NPCs talking
if char.charIsNPC(actor):
    return

# Don't respond to yourself
if me == actor:
    return

speech_lower = arg.lower() if arg else ""
char_name = char.charGetName(me)
actor_name = char.charGetName(actor)

# Check for greeting words
greetings = ["hello", "hi", "greetings", "good morning", "good day", "hey"]

if any(greeting in speech_lower for greeting in greetings):
    # Respond with a greeting
    responses = [
        "Hello there, %s!" % actor_name,
        "Greetings, %s! How are you today?" % actor_name,
        "Well hello! Nice to see you, %s." % actor_name,
        "Hi %s! What brings you here?" % actor_name
    ]
    
    response = random.choice(responses)
    
    # Use a slight delay for more natural conversation
    def delayed_response(npc, message):
        npc_name = char.charGetName(npc)
        char.charSendRoom(npc, "%s says, '%s'" % (npc_name, message))
    
    event.start_event(me, 1, delayed_response, me, response)
```

### Step 2b: Create a Greeting NPC

Now create an NPC to attach the trigger to:

```
# Create a new NPC:
medit tutorial_greeter

# Set basic properties in the medit screen:
# 3) Name: a friendly greeter
# 5) Keywords: greeter friendly person
# 6) Room description: A friendly person stands here, ready to greet visitors.
# 8) Description: This person has a warm smile and seems eager to talk.
```

### Step 2c: Attach the Trigger

In the medit screen, select **T) Trigger menu**:

```
# Current triggers:
# (none yet)
#
# N) Add new trigger
# D) Delete trigger
```

1. **Select N** (Add new trigger)
2. **Enter trigger key**: `greeting_speech`

### Testing Your Trigger

After saving both the trigger and NPC:

```
# Load the NPC:
load mobile tutorial_greeter

# Test the trigger:
say hello
# The NPC should respond with a greeting after a short delay!

# Try other greetings:
say hi there
say good morning
```

## Step 3: Understanding the Trigger System

Now that you've created your first trigger, let's understand how the system works:

### The Two-Part System

NakedMud's trigger system has two parts:

1. **Trigger Creation** (`tedit`): Write the Python code that defines what happens
2. **Trigger Attachment** (OLC menus): Connect triggers to NPCs, rooms, or objects

### Why This Separation?

- **Reusability**: One trigger can be used by multiple NPCs/rooms/objects
- **Maintainability**: Edit the trigger once, affects all users of it
- **Organization**: Keeps code separate from content definitions
- **Modularity**: Mix and match different triggers as needed

### Trigger Variables

In trigger code, you have access to special variables:

- **me**: The NPC/room/object the trigger is attached to
- **actor**: The character who caused the trigger to fire  
- **arg**: Additional information (like speech text for speech triggers)

### Common Trigger Types

**Character Triggers:**
- `enter` - When someone enters the room with the NPC
- `speech` - When someone speaks in the room
- `heartbeat` - Regular periodic trigger
- `death` - When the NPC dies
- `greet` - When the NPC should greet someone

**Room Triggers:**
- `enter` - When someone enters the room
- `leave` - When someone leaves the room
- `look` - When someone looks at the room
- `heartbeat` - Regular atmospheric effects
- `speech` - When someone speaks in the room

**Object Triggers:**
- `get` - When the object is picked up
- `drop` - When the object is dropped
- `look` - When someone looks at the object
- `wear` - When the object is worn
- `use` - When the object is used

## Step 4: Room Entry and Exit Triggers

Let's create a room that tracks who enters and leaves:

```python
# Add to tutorial_triggers.py

def room_entry_tracker(rm, actor):
    """Track who enters the room."""
    
    # Don't track NPCs
    if char.charIsNPC(actor):
        return
    
    actor_name = char.charGetName(actor)
    room_name = room.roomGetName(rm)
    
    # Get entry count for this player
    entry_key = "entries_%s" % actor_name.lower()
    entries = auxiliary.roomGetAuxiliaryData(rm, entry_key)
    
    if entries is None:
        entries = 0
    else:
        entries = int(entries)
    
    entries += 1
    auxiliary.roomSetAuxiliaryData(rm, entry_key, str(entries))
    
    # Customize message based on visit count
    if entries == 1:
        message = "Welcome to %s, %s! This is your first visit here." % (room_name, actor_name)
    elif entries < 5:
        message = "Welcome back to %s, %s! This is visit number %d." % (room_name, actor_name, entries)
    else:
        message = "Ah, %s returns to %s once again! You're becoming a regular here." % (actor_name, room_name)
    
    char.charSend(actor, message)
    
    # Log the entry
    mudsys.log_string("Player %s entered %s (visit #%d)" % (actor_name, room_name, entries))

def room_exit_tracker(rm, actor):
    """Track who leaves the room."""
    
    if char.charIsNPC(actor):
        return
    
    actor_name = char.charGetName(actor)
    room_name = room.roomGetName(rm)
    
    # Get total time spent (simplified - just count exits)
    exit_key = "exits_%s" % actor_name.lower()
    exits = auxiliary.roomGetAuxiliaryData(rm, exit_key)
    
    if exits is None:
        exits = 0
    else:
        exits = int(exits)
    
    exits += 1
    auxiliary.roomSetAuxiliaryData(rm, exit_key, str(exits))
    
    # Farewell messages
    farewells = [
        "Safe travels, %s!" % actor_name,
        "Come back soon, %s!" % actor_name,
        "Until next time, %s!" % actor_name
    ]
    
    farewell = random.choice(farewells)
    char.charSend(actor, farewell)

# Register room triggers
mudsys.add_room_method("entry_tracker", room_entry_tracker)
mudsys.add_room_method("exit_tracker", room_exit_tracker)
```

Attach these to a room:
```
tedit room tutorial_tracked_room
attach entry_tracker enter_room
attach exit_tracker leave_room
```

## Step 5: Object Interaction Triggers

Create an interactive object with multiple trigger types:

```python
# Add to tutorial_triggers.py

def magic_stone_get_trigger(obj, actor):
    """Trigger when the magic stone is picked up."""
    
    if char.charIsNPC(actor):
        return
    
    actor_name = char.charGetName(actor)
    
    # Check if this is the first time picking it up
    first_pickup = auxiliary.objGetAuxiliaryData(obj, "first_pickup_%s" % actor_name.lower())
    
    if first_pickup is None:
        # First time pickup
        auxiliary.objSetAuxiliaryData(obj, "first_pickup_%s" % actor_name.lower(), "true")
        
        char.charSend(actor, "As you pick up the stone, it begins to glow with a soft blue light!")
        char.charSendRoom(actor, "%s picks up a stone that suddenly begins glowing!" % actor_name)
        
        # Give the player some information
        char.charSend(actor, "The stone feels warm in your hands and seems to pulse with magical energy.")
        
    else:
        # Subsequent pickups
        char.charSend(actor, "The familiar warmth of the magic stone fills your hands.")
        char.charSendRoom(actor, "%s picks up the glowing stone." % actor_name)

def magic_stone_drop_trigger(obj, actor):
    """Trigger when the magic stone is dropped."""
    
    if char.charIsNPC(actor):
        return
    
    actor_name = char.charGetName(actor)
    
    char.charSend(actor, "The stone's glow fades as you set it down.")
    char.charSendRoom(actor, "The stone %s drops loses its magical glow." % actor_name)
    
    # Track how many times it's been dropped
    drops = auxiliary.objGetAuxiliaryData(obj, "drop_count")
    if drops is None:
        drops = 0
    else:
        drops = int(drops)
    
    drops += 1
    auxiliary.objSetAuxiliaryData(obj, "drop_count", str(drops))
    
    # Special message if dropped many times
    if drops > 5:
        char.charSend(actor, "The stone seems to flicker with annoyance at being dropped so often.")

def magic_stone_look_trigger(obj, actor):
    """Trigger when someone looks at the magic stone."""
    
    actor_name = char.charGetName(actor)
    
    # Get the stone's current state
    drop_count = auxiliary.objGetAuxiliaryData(obj, "drop_count")
    drops = int(drop_count) if drop_count else 0
    
    # Base description
    desc = "This smooth, oval stone has an otherworldly quality to it."
    
    # Add state-based descriptions
    if drops == 0:
        desc += " It seems pristine and untouched, radiating potential energy."
    elif drops < 3:
        desc += " It shows slight signs of handling but still pulses with power."
    elif drops < 6:
        desc += " The stone looks well-used and its glow seems slightly dimmer."
    else:
        desc += " The poor stone looks quite battered and its magical aura is weak."
    
    # Check if the player is holding it
    if char.charHasObj(actor, obj):
        desc += " It feels warm and alive in your hands."
    else:
        desc += " It sits quietly, waiting to be picked up."
    
    char.charSend(actor, desc)

# Register object triggers
mudsys.add_obj_method("magic_stone_get", magic_stone_get_trigger)
mudsys.add_obj_method("magic_stone_drop", magic_stone_drop_trigger)
mudsys.add_obj_method("magic_stone_look", magic_stone_look_trigger)
```

Create the object and attach triggers:
```
tedit obj tutorial_magic_stone
# Set up basic object properties, then:
attach magic_stone_get get
attach magic_stone_drop drop
attach magic_stone_look look
```

## Step 6: Complex Trigger Interactions

Let's create a puzzle system using multiple triggers:

```python
# Add to tutorial_triggers.py

def puzzle_room_enter(rm, actor):
    """Initialize puzzle state when someone enters."""
    
    if char.charIsNPC(actor):
        return
    
    actor_name = char.charGetName(actor)
    
    # Check if puzzle is already solved
    solved = auxiliary.roomGetAuxiliaryData(rm, "puzzle_solved")
    if solved == "true":
        char.charSend(actor, "This room's puzzle has already been solved. The magical barrier is down.")
        return
    
    # Initialize puzzle state for this player
    player_state = auxiliary.charGetAuxiliaryData(actor, "puzzle_state")
    if player_state is None:
        auxiliary.charSetAuxiliaryData(actor, "puzzle_state", "started")
        
        char.charSend(actor, "You enter a mysterious chamber. Ancient runes glow on the walls.")
        char.charSend(actor, "A magical barrier blocks the exit to the north. Perhaps the runes hold a clue?")
        char.charSend(actor, "Try 'look runes' to examine them more closely.")

def puzzle_room_look(rm, actor, target):
    """Handle looking at puzzle elements."""
    
    if not target:
        return  # Normal room look
    
    target_lower = target.lower()
    actor_name = char.charGetName(actor)
    
    if target_lower in ["runes", "rune", "wall", "walls"]:
        char.charSend(actor, "The ancient runes glow with mystical energy. You can make out four symbols:")
        char.charSend(actor, "A sun symbol (☀), a moon symbol (☽), a star symbol (★), and a tree symbol (🌳)")
        char.charSend(actor, "Below them is an inscription: 'Speak the cycle of day and night, growth and guidance.'")
        char.charSend(actor, "Perhaps you need to say something related to these symbols?")
        
        # Update player's puzzle state
        auxiliary.charSetAuxiliaryData(actor, "puzzle_state", "examined_runes")
        
    elif target_lower in ["barrier", "exit", "north"]:
        solved = auxiliary.roomGetAuxiliaryData(rm, "puzzle_solved")
        if solved == "true":
            char.charSend(actor, "The magical barrier has been dispelled. The way north is clear.")
        else:
            char.charSend(actor, "A shimmering magical barrier blocks your path. It pulses with the same energy as the runes.")

def puzzle_room_speech(rm, actor, speech):
    """Handle speech-based puzzle solving."""
    
    if char.charIsNPC(actor):
        return
    
    # Check if puzzle is already solved
    solved = auxiliary.roomGetAuxiliaryData(rm, "puzzle_solved")
    if solved == "true":
        return
    
    actor_name = char.charGetName(actor)
    speech_lower = speech.lower() if speech else ""
    
    # Check if player has examined the runes
    player_state = auxiliary.charGetAuxiliaryData(actor, "puzzle_state")
    if player_state != "examined_runes":
        char.charSend(actor, "The runes don't react to your words. Perhaps you should examine them first?")
        return
    
    # The correct sequence: sun, moon, star, tree (day, night, guidance, growth)
    correct_words = ["sun", "moon", "star", "tree"]
    
    # Check if the speech contains the correct sequence
    words_found = []
    for word in correct_words:
        if word in speech_lower:
            words_found.append(word)
    
    # Store progress
    progress_key = "puzzle_progress_%s" % actor_name.lower()
    
    if len(words_found) == 4 and all(word in speech_lower for word in correct_words):
        # Puzzle solved!
        auxiliary.roomSetAuxiliaryData(rm, "puzzle_solved", "true")
        auxiliary.charSetAuxiliaryData(actor, "puzzle_state", "solved")
        
        char.charSend(actor, "As you speak the words, the runes blaze with brilliant light!")
        char.charSendRoom(actor, "%s speaks ancient words, causing the runes to flare with power!" % actor_name)
        
        # Delayed effect
        import event
        event.start_event(rm, 2, puzzle_completion_effect, actor)
        
    elif len(words_found) > 0:
        # Partial progress
        auxiliary.roomSetAuxiliaryData(rm, progress_key, str(len(words_found)))
        
        char.charSend(actor, "Some of the runes flicker in response to your words. You're on the right track!")
        char.charSend(actor, "You've activated %d of 4 runes. Keep trying!" % len(words_found))
        
    else:
        char.charSend(actor, "The runes remain dim. Your words don't seem to be the right ones.")

def puzzle_completion_effect(rm, solver):
    """Complete the puzzle with dramatic effect."""
    
    solver_name = char.charGetName(solver)
    
    room.roomSendMessage(rm, "The magical barrier dissolves in a shower of sparkling light!")
    room.roomSendMessage(rm, "The way north is now clear!")
    
    char.charSend(solver, "Congratulations! You have solved the ancient puzzle!")
    
    # Give the solver some recognition
    auxiliary.charSetAuxiliaryData(solver, "puzzles_solved", "1")
    
    mudsys.log_string("Player %s solved the rune puzzle!" % solver_name)

# Register puzzle triggers
mudsys.add_room_method("puzzle_enter", puzzle_room_enter)
mudsys.add_room_method("puzzle_look", puzzle_room_look)
mudsys.add_room_method("puzzle_speech", puzzle_room_speech)
```

Attach the puzzle triggers to a room:
```
tedit room tutorial_puzzle_room
attach puzzle_enter enter_room
attach puzzle_look look
attach puzzle_speech speech
```

## Step 7: Heartbeat Triggers for Ongoing Effects

Create a system that uses heartbeat triggers for continuous effects:

```python
# Add to tutorial_triggers.py

def healing_fountain_heartbeat(obj):
    """Healing fountain that helps nearby players."""
    
    # Get the room the fountain is in
    rm = obj.getRoom()  # This would be the actual method to get object's room
    if not rm:
        return
    
    # Get all characters in the room
    chars_in_room = room.roomGetChars(rm)
    players_in_room = [c for c in chars_in_room if not char.charIsNPC(c)]
    
    if not players_in_room:
        return  # No players to heal
    
    # Only heal occasionally
    if random.randint(1, 10) > 2:
        return
    
    # Heal each player a small amount
    for player in players_in_room:
        player_name = char.charGetName(player)
        
        # Check if player needs healing (this would use actual HP functions)
        # For now, just simulate
        char.charSend(player, "The magical fountain's mist refreshes you slightly.")
        
        # Track fountain usage
        usage_key = "fountain_healing_%s" % player_name.lower()
        usage = auxiliary.objGetAuxiliaryData(obj, usage_key)
        if usage is None:
            usage = 0
        else:
            usage = int(usage)
        
        usage += 1
        auxiliary.objSetAuxiliaryData(obj, usage_key, str(usage))
        
        # Special message for frequent users
        if usage % 10 == 0:
            char.charSend(player, "The fountain seems to recognize you as a frequent visitor.")

def weather_sensitive_npc_heartbeat(ch):
    """NPC that reacts to weather conditions."""
    
    # This would integrate with your mud's weather system
    # For demonstration, we'll simulate weather
    
    weather_conditions = ["sunny", "rainy", "cloudy", "stormy", "snowy"]
    current_weather = random.choice(weather_conditions)
    
    char_name = char.charGetName(ch)
    
    # Only react to weather occasionally
    if random.randint(1, 20) > 1:
        return
    
    # Weather-based behaviors
    if current_weather == "rainy":
        actions = [
            "%s pulls their cloak tighter against the rain." % char_name,
            "%s looks up at the cloudy sky with concern." % char_name,
            "%s mutters about the wet weather." % char_name
        ]
    elif current_weather == "sunny":
        actions = [
            "%s smiles and enjoys the warm sunshine." % char_name,
            "%s stretches contentedly in the sunlight." % char_name,
            "%s comments on what a beautiful day it is." % char_name
        ]
    elif current_weather == "stormy":
        actions = [
            "%s looks nervously at the stormy sky." % char_name,
            "%s seeks shelter from the fierce wind." % char_name,
            "%s jumps slightly at a loud thunderclap." % char_name
        ]
    else:
        return  # No special behavior for other weather
    
    action = random.choice(actions)
    char.charSendRoom(ch, action)

# Register heartbeat triggers
mudsys.add_obj_method("healing_fountain_heartbeat", healing_fountain_heartbeat)
mudsys.add_char_method("weather_npc_heartbeat", weather_sensitive_npc_heartbeat)
```

## Step 8: Trigger Debugging and Testing

Add debugging capabilities to your triggers:

```python
# Add to tutorial_triggers.py

def debug_trigger_info(trigger_name, obj_type, obj, actor=None, extra_info=""):
    """Log detailed trigger information for debugging."""
    
    if not mudsys.get_config("debug_triggers"):  # Only if debugging is enabled
        return
    
    debug_msg = "TRIGGER DEBUG: %s on %s" % (trigger_name, obj_type)
    
    if obj_type == "char" and obj:
        debug_msg += " (%s)" % char.charGetName(obj)
    elif obj_type == "room" and obj:
        debug_msg += " (%s)" % room.roomGetName(obj)
    elif obj_type == "obj" and obj:
        debug_msg += " (object)"  # Would use actual object name function
    
    if actor:
        debug_msg += " triggered by %s" % char.charGetName(actor)
    
    if extra_info:
        debug_msg += " - %s" % extra_info
    
    mudsys.log_string(debug_msg)

# Example of using debug info in triggers
def debug_speech_trigger(ch, actor, speech):
    """Example trigger with debugging."""
    
    debug_trigger_info("speech", "char", ch, actor, "speech: '%s'" % speech)
    
    # Your actual trigger logic here
    char_name = char.charGetName(ch)
    actor_name = char.charGetName(actor)
    
    char.charSend(actor, "%s heard you say: %s" % (char_name, speech))

# Test command to enable/disable trigger debugging
def cmd_debug_triggers(ch, cmd, arg):
    """Command to toggle trigger debugging."""
    
    if not char.charIsWizard(ch):  # Only wizards can use this
        char.charSend(ch, "You don't have permission to use this command.")
        return
    
    if not arg:
        current = mudsys.get_config("debug_triggers")
        char.charSend(ch, "Trigger debugging is currently: %s" % ("ON" if current else "OFF"))
        char.charSend(ch, "Use 'debug_triggers on' or 'debug_triggers off' to change.")
        return
    
    if arg.lower() == "on":
        mudsys.set_config("debug_triggers", True)
        char.charSend(ch, "Trigger debugging enabled.")
    elif arg.lower() == "off":
        mudsys.set_config("debug_triggers", False)
        char.charSend(ch, "Trigger debugging disabled.")
    else:
        char.charSend(ch, "Use 'on' or 'off'.")

mudsys.add_cmd("debug_triggers", None, cmd_debug_triggers, "wizard", 1)
```

## Best Practices for Trigger Design

### 1. Keep Triggers Focused
Each trigger should have a single, clear purpose:

```python
# Good - focused trigger
def door_open_trigger(obj, actor):
    """Handle opening a door."""
    # Just handle door opening logic

# Bad - trigger doing too much
def door_everything_trigger(obj, actor):
    """Handle all door interactions."""
    # Trying to handle open, close, lock, unlock, etc.
```

### 2. Validate Inputs
Always check that your inputs are valid:

```python
def safe_trigger(obj, actor):
    """Example of safe trigger design."""
    
    # Check for null objects
    if obj is None or actor is None:
        return
    
    # Check for NPC actors if needed
    if char.charIsNPC(actor):
        return
    
    # Your trigger logic here
```

### 3. Use Auxiliary Data for State
Store trigger state in auxiliary data:

```python
def stateful_trigger(obj, actor):
    """Trigger that remembers state."""
    
    # Get current state
    state = auxiliary.objGetAuxiliaryData(obj, "trigger_state")
    if state is None:
        state = "initial"
    
    # Process based on state
    if state == "initial":
        # First time logic
        auxiliary.objSetAuxiliaryData(obj, "trigger_state", "activated")
    elif state == "activated":
        # Subsequent logic
        pass
```

### 4. Handle Errors Gracefully
Wrap trigger logic in try-catch blocks:

```python
def robust_trigger(obj, actor):
    """Example of error-resistant trigger."""
    
    try:
        # Your trigger logic here
        pass
    except Exception as e:
        mudsys.log_string("Error in trigger: %s" % str(e))
        # Provide user feedback if appropriate
        if actor and not char.charIsNPC(actor):
            char.charSend(actor, "Something went wrong. Please try again.")
```

## Common Trigger Patterns

### Delayed Response Pattern
```python
def trigger_with_delay(obj, actor):
    """Trigger that responds after a delay."""
    
    import event
    event.start_event(obj, 3, delayed_response, actor)

def delayed_response(obj, actor):
    """The delayed response function."""
    # Response logic here
    pass
```

### State Machine Pattern
```python
def state_machine_trigger(obj, actor):
    """Trigger implementing a state machine."""
    
    current_state = auxiliary.objGetAuxiliaryData(obj, "state")
    
    if current_state == "state1":
        # Handle state1 logic
        auxiliary.objSetAuxiliaryData(obj, "state", "state2")
    elif current_state == "state2":
        # Handle state2 logic
        auxiliary.objSetAuxiliaryData(obj, "state", "state1")
```

## Next Steps

Now that you understand basic triggers:

1. **Try [Advanced NPC Behaviors](../advanced-npc-behaviors/)** for complex character AI
2. **Learn [Complex Room Interactions](../complex-room-interactions/)** for sophisticated environmental systems
3. **Explore [Using the Event System](../using-event-system/)** for timed and scheduled actions

## Summary

You've learned to:
- Understand different trigger types and their uses
- Create responsive trigger scripts
- Build complex interactive systems
- Use auxiliary data for trigger state management
- Debug and test trigger systems
- Follow best practices for trigger design

## Troubleshooting

**Triggers not firing?**
- Check trigger attachment with `tstat`
- Verify the trigger function is registered
- Look for errors in mud logs

**Triggers firing too often?**
- Add random chances to limit frequency
- Use auxiliary data to track timing
- Consider performance impact

**Complex interactions not working?**
- Break down into smaller, testable triggers
- Add debug logging to trace execution
- Test each trigger type individually

Ready for more advanced scripting? Continue with the intermediate tutorials!