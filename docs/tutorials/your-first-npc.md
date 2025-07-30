---
layout: default
title: Your First NPC
parent: Start with the Basics
grand_parent: Tutorials
nav_order: 2
permalink: /tutorials/your-first-npc/
---

# Your First NPC

Learn to create non-player characters using character prototypes, from basic NPCs to interactive characters with behaviors.

## Overview

This tutorial teaches you how to create NPCs (Non-Player Characters) using NakedMud's prototype system. You'll build a simple shopkeeper NPC that can interact with players, demonstrate basic AI behaviors, and use auxiliary data to maintain state.

## Prerequisites

- Completed [Getting Started with Python Scripting](getting-started-scripting/)
- Understanding of [Character Prototypes](/core-concepts/prototypes/)
- Wizard-level access to your mud

## What You'll Learn

- How to create character prototypes
- Basic NPC behaviors and interactions
- Using triggers for NPC responses
- Managing NPC state with auxiliary data
- Best practices for NPC design

## Step 1: Understanding Character Prototypes

Character prototypes are templates that define NPC properties and behaviors. Let's examine the structure:

```
# Connect to your mud and examine existing prototypes
# Use: mlist [zone]
# This shows available mob prototypes in a zone
```

A character prototype defines:
- Basic stats (name, description, level)
- Appearance and equipment
- Behaviors and triggers
- Special properties

## Step 2: Creating Your First NPC Prototype

Let's create a simple merchant NPC using NakedMud's OLC (Online Creation) system. First, you'll need to understand the basic OLC commands:

### Essential OLC Commands for NPCs

- `medit <mob_key>` - Create or edit a mob (NPC) prototype
- `mlist [zone]` - List all mob prototypes in a zone
- `mview <mob_key>` - Show details for a mob prototype
- `load mobile <mob_key>` - Load an instance of a mob into the current room

### Creating the Merchant Prototype

```
# In-game commands (as a wizard/builder):
medit tutorial_merchant

# This opens the mob editor with a menu like:
# [tutorial_merchant]
# 1) Abstract: yes
# 2) Inherits from prototypes:
# 
# 3) Name
# 
# 4) Name for multiple occurrences:
# 
# 5) Keywords:
# 
# 6) Room description:
# 
# 7) Room description for multiple occurrences:
# 
# 8) Description:
# 
# T) Trigger menu
# R) Change race   [leave unchanged]
# G) Change Gender [leave unchanged]
# C) Extra code
```

Set these properties by selecting the menu options:

1. **Abstract**: Select 1 to toggle to `no` (so the NPC can be loaded)
3. **Name**: `a friendly merchant`
5. **Keywords**: `merchant trader shopkeeper friendly`
6. **Room description**: `A friendly merchant stands here, ready to trade with customers.`
8. **Description**: `He has a warm smile and keen eyes that suggest years of experience in commerce. His clothes are well-made but practical, and he carries himself with the confidence of someone who knows the value of things.`
**R) Change race**: Select R and enter `human`
**G) Change Gender**: Select G and enter `male`

### Understanding NPC Properties

- **Abstract**: Whether this is a template (yes) or can be loaded (no)
- **Inherits from prototypes**: Parent prototypes to inherit properties from
- **Name**: The name shown in room descriptions and targeting
- **Name for multiple occurrences**: Name when multiple copies exist
- **Keywords**: Words players can use to target this NPC (e.g., "look merchant")
- **Room description**: Brief description shown when NPC is in a room
- **Room description for multiple occurrences**: Description when multiple copies exist
- **Description**: Detailed description when looking at the NPC
- **Race**: Determines base stats and abilities
- **Gender**: Affects pronouns and some interactions

### Important OLC Tips

1. **Always save your work**: Use 'S' to save before exiting
2. **Test your NPCs**: Use `load mobile tutorial_merchant` to create an instance
3. **Check your work**: Use `mview tutorial_merchant` to review the prototype
4. **Zone organization**: Keep related NPCs in the same zone for easy management

## Step 3: Creating Triggers for NPC Behaviors

Now we'll create interactive behaviors for our NPC using NakedMud's trigger system. This involves two steps: creating the triggers and attaching them to the NPC.

### Step 3a: Create the Greeting Trigger

First, let's create a trigger for greeting players:

```
# Create the greeting trigger:
tedit merchant_greet

# This opens the trigger editor:
# [merchant_greet]
# 1) Name        : An Unfinished Trigger
# 2) Trigger type: <NONE>
# 3) Script Code
```

Set up the trigger:

1. **Name**: `Merchant greeting trigger`
2. **Trigger type**: `enter` (this makes it fire when someone enters the room)
3. **Script Code**: Select this to edit the Python code

In the Script Code editor, replace the default code with:

```python
# Merchant greeting trigger - fires when someone enters the room

import char
import random
import event

# Don't greet other NPCs
if char.charIsNPC(actor):
    return

# Get names for the interaction
merchant_name = char.charGetName(me)
player_name = char.charGetName(actor)

# Random greeting messages
greetings = [
    "Welcome to my shop, %s!" % player_name,
    "Greetings, traveler! Looking for anything special?",
    "Ah, a new customer! How can I help you today?",
    "Welcome, welcome! I have the finest goods in the land!"
]

greeting = random.choice(greetings)

# Send the greeting with a slight delay for realism
char.charSend(me, "You notice %s and prepare to greet them." % player_name)
char.charSendRoom(me, "%s looks up as %s enters." % (merchant_name, player_name))

# Use the event system for a delayed greeting
def delayed_greeting(npc, message):
    npc_name = char.charGetName(npc)
    char.charSendRoom(npc, "%s says, '%s'" % (npc_name, message))

event.start_event(me, 2, delayed_greeting, me, greeting)
```

### Step 3b: Create the Speech Response Trigger

Create another trigger for responding to speech:

```
# Create the speech trigger:
tedit merchant_talk

# Set up the trigger:
# 1) Name: Merchant speech responses
# 2) Trigger type: speech
# 3) Script Code:
```

In the Script Code editor:

```python
# Merchant speech response trigger - fires when someone speaks

import char
import random

# Don't respond to NPCs talking
if char.charIsNPC(actor):
    return

player_name = char.charGetName(actor)
merchant_name = char.charGetName(me)

# Simple keyword responses
message = arg.lower() if arg else ""

if "hello" in message or "hi" in message:
    response = "Hello there, %s! I'm always happy to see a friendly face." % player_name
elif "buy" in message or "sell" in message or "trade" in message:
    response = "I'd love to trade with you! Unfortunately, my inventory system isn't ready yet."
elif "help" in message:
    response = "I can tell you about my wares, or we can just chat. What interests you?"
elif "bye" in message or "farewell" in message:
    response = "Safe travels, %s! Come back anytime!" % player_name
else:
    responses = [
        "That's interesting, %s. Tell me more!" % player_name,
        "I see, I see. Anything else on your mind?",
        "Fascinating! I love meeting new people and hearing their stories.",
        "Indeed! Life is full of surprises, isn't it?"
    ]
    response = random.choice(responses)

# Send the response
char.charSendRoom(me, "%s says, '%s'" % (merchant_name, response))
```

### Step 3c: Create the Heartbeat Trigger

Create a trigger for ambient behaviors:

```
# Create the heartbeat trigger:
tedit merchant_heartbeat

# Set up the trigger:
# 1) Name: Merchant ambient behaviors
# 2) Trigger type: heartbeat
# 3) Script Code:
```

In the Script Code editor:

```python
# Merchant heartbeat trigger - fires regularly for ambient actions

import char
import room
import random

# Only do ambient actions occasionally
if random.randint(1, 10) > 2:
    return

merchant_name = char.charGetName(me)

# Random ambient actions
actions = [
    "%s adjusts some items on the counter." % merchant_name,
    "%s hums a cheerful tune while working." % merchant_name,
    "%s polishes a piece of merchandise." % merchant_name,
    "%s counts some coins quietly." % merchant_name,
    "%s looks around for potential customers." % merchant_name
]

# Only do ambient actions if there are players in the room
room_obj = char.charGetRoom(me)
if room_obj:
    chars_in_room = room.roomGetChars(room_obj)
    has_players = any(not char.charIsNPC(c) for c in chars_in_room if c != me)
    
    if has_players:
        action = random.choice(actions)
        char.charSendRoom(me, action)
```

### Understanding Trigger Variables

In trigger code, you have access to special variables:
- **me**: The NPC/room/object the trigger is attached to
- **actor**: The character who caused the trigger to fire
- **arg**: Additional information (like speech text for speech triggers)

## Step 4: Attaching Triggers to the NPC

Now we need to attach the triggers we created to our merchant NPC:

```
# Edit the merchant NPC:
medit tutorial_merchant

# The medit screen shows:
# [tutorial_merchant]
# 1) Abstract: no
# 2) Inherits from prototypes:
# 3) Name
# a friendly merchant
# 4) Name for multiple occurrences:
# 5) Keywords:
# merchant trader shopkeeper friendly
# 6) Room description:
# A friendly merchant stands here, ready to trade with customers.
# 7) Room description for multiple occurrences:
# 8) Description:
# T) Trigger menu
# R) Change race   [human]
# G) Change Gender [male]
# C) Extra code
```

### Attaching the Triggers

Select **T) Trigger menu** to open the trigger attachment interface:

```
# Trigger menu shows:
# Current triggers:
# (none yet)
#
# N) Add new trigger
# D) Delete trigger
```

Attach each trigger:

1. **Select N** (Add new trigger)
2. **Enter trigger key**: `merchant_greet`
3. **Select N** again
4. **Enter trigger key**: `merchant_talk`  
5. **Select N** again
6. **Enter trigger key**: `merchant_heartbeat`

After attaching all triggers, the menu will show:

```
# Current triggers:
#   merchant_greet
#   merchant_talk
#   merchant_heartbeat
#
# N) Add new trigger
# D) Delete trigger
```

### How Trigger Attachment Works

- **Reusable**: Triggers can be attached to multiple NPCs
- **Modular**: Each trigger handles one specific behavior
- **Maintainable**: Edit the trigger once, affects all NPCs using it
- **Organized**: Keeps trigger code separate from NPC definitions

### Using Extra Code (Advanced)

The **C) Extra code** option is for additional Python code that runs when the NPC loads, such as:
- Setting special properties
- Initializing auxiliary data
- Custom initialization logic

For beginners, using the trigger system (T menu) is the recommended approach.

### Understanding NPC Triggers

NakedMud NPCs support various trigger types:

- **enter_room** - Fires when someone enters the room with the NPC
- **leave_room** - Fires when someone leaves the room
- **speech** - Fires when someone speaks in the room
- **heartbeat** - Fires regularly (every few seconds)
- **death** - Fires when the NPC dies
- **combat** - Fires during combat situations
- **greet** - Fires when the NPC should greet someone
- **give** - Fires when someone gives the NPC an item

### Alternative: Using the Trigger Editor

You can also use the dedicated trigger editor:

```
# Alternative method using trigger editor:
mpedit tutorial_merchant

# This opens the mob program editor where you can:
# - Add trigger programs
# - Set trigger conditions
# - Write trigger responses
```

### Testing Your NPC

After saving the prototype:

```
# Load an instance to test:
load mobile tutorial_merchant

# Test the behaviors:
# - Enter and leave the room
# - Say "hello" to trigger speech responses
# - Wait to see heartbeat behaviors
```

## Step 5: Adding Personality with Auxiliary Data

Let's make the merchant remember interactions:

```python
# Add to tutorial_merchant.py

def merchant_remember_player(ch, actor):
    """Remember interactions with players."""
    
    if char.charIsNPC(actor):
        return
    
    player_name = char.charGetName(actor)
    
    # Get or create interaction count
    interaction_key = "interactions_%s" % player_name.lower()
    count = auxiliary.charGetAuxiliaryData(ch, interaction_key)
    
    if count is None:
        count = 0
    else:
        count = int(count)
    
    count += 1
    auxiliary.charSetAuxiliaryData(ch, interaction_key, str(count))
    
    return count

def enhanced_merchant_greet_trigger(ch, actor, arg):
    """Enhanced greeting that remembers players."""
    
    if char.charIsNPC(actor):
        return
    
    player_name = char.charGetName(actor)
    merchant_name = char.charGetName(ch)
    
    # Remember this interaction
    interaction_count = merchant_remember_player(ch, actor)
    
    # Customize greeting based on history
    if interaction_count == 1:
        greeting = "Welcome to my shop, %s! I don't think we've met before." % player_name
    elif interaction_count < 5:
        greeting = "Good to see you again, %s! This is your %s visit." % (player_name, get_ordinal(interaction_count))
    else:
        greeting = "Ah, my good friend %s! Always a pleasure to see a regular customer!" % player_name
    
    # Send greeting with delay
    import event
    event.start_event(ch, 2, merchant_say_greeting, greeting)

def get_ordinal(n):
    """Convert number to ordinal (1st, 2nd, 3rd, etc.)."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

# Update the registration
mudsys.add_char_method("merchant_greet", enhanced_merchant_greet_trigger)
```

## Step 6: Creating and Managing NPC Instances

Now create an actual instance of your NPC in the world:

### Loading NPCs

```
# Basic loading:
load mobile tutorial_merchant

# Loading to a specific room:
goto <room_vnum>  # Go to the target room first
load mobile tutorial_merchant

# Note: The load command always loads to your current room
```

### Managing NPCs in the World

```
# List all loaded instances of your NPC:
mfind tutorial_merchant

# Get detailed info about the NPC prototype:
mview tutorial_merchant

# Remove an NPC instance:
# Target the NPC and use:
purge merchant

# Or purge all instances of a prototype:
mpurge tutorial_merchant
```

### Zone Integration

For permanent NPCs, add them to zone reset files:

```
# Edit the zone file:
zedit <zone_number>

# Add a mob reset:
# M <mob_vnum> <max_in_world> <room_vnum>
# Example: M 1001 1 3001
# This loads mob 1001, max 1 in world, in room 3001
```

### NPC Persistence

- **Temporary**: NPCs loaded with `load mobile` disappear on reboot
- **Permanent**: NPCs added to zone resets respawn automatically
- **Unique**: Use max_in_world = 1 for unique NPCs
- **Multiple**: Higher numbers allow multiple instances

## Step 7: Testing Your NPC

Test the various behaviors:

1. **Enter the room** - The merchant should greet you
2. **Say "hello"** - The merchant should respond
3. **Try different keywords** - "buy", "help", "bye"
4. **Wait and watch** - Ambient behaviors should occur
5. **Leave and return** - The merchant should remember you

## Step 8: Advanced NPC Features

Let's add more sophisticated behaviors:

```python
# Add to tutorial_merchant.py

def merchant_mood_system(ch):
    """Simple mood system for the merchant."""
    
    # Get current mood
    mood = auxiliary.charGetAuxiliaryData(ch, "mood")
    if mood is None:
        mood = "neutral"
    
    # Factors that affect mood
    room = char.charGetRoom(ch)
    if room:
        import room as room_mod
        chars_in_room = room_mod.roomGetChars(room)
        player_count = sum(1 for c in chars_in_room if not char.charIsNPC(c))
        
        # More players = happier merchant
        if player_count > 2:
            mood = "happy"
        elif player_count == 0:
            mood = "lonely"
        else:
            mood = "neutral"
    
    # Store the mood
    auxiliary.charSetAuxiliaryData(ch, "mood", mood)
    return mood

def mood_based_response(ch, base_response):
    """Modify responses based on current mood."""
    
    mood = merchant_mood_system(ch)
    merchant_name = char.charGetName(ch)
    
    if mood == "happy":
        return base_response + " *%s seems particularly cheerful today*" % merchant_name
    elif mood == "lonely":
        return base_response + " *%s seems a bit lonely*" % merchant_name
    else:
        return base_response

# Update the talk trigger to use mood
def advanced_merchant_talk_trigger(ch, actor, arg):
    """Talk trigger with mood system."""
    
    if char.charIsNPC(actor):
        return
    
    player_name = char.charGetName(actor)
    merchant_name = char.charGetName(ch)
    message = arg.lower() if arg else ""
    
    # Base responses (same as before)
    if "hello" in message:
        base_response = "Hello there, %s!" % player_name
    elif "buy" in message:
        base_response = "I'd love to help you find something special!"
    else:
        base_response = "That's interesting, %s!" % player_name
    
    # Apply mood modification
    final_response = mood_based_response(ch, base_response)
    
    char.charSendRoom(ch, "%s says, '%s'" % (merchant_name, final_response))

# Register the advanced version
mudsys.add_char_method("merchant_talk", advanced_merchant_talk_trigger)
```

## Step 9: NPC Commands

You can also give NPCs special commands that only they can use:

```python
def cmd_merchant_restock(ch, cmd, arg):
    """Special command for merchant NPCs to restock."""
    
    # Only NPCs can use this command
    if not char.charIsNPC(ch):
        char.charSend(ch, "Only NPCs can use this command.")
        return
    
    merchant_name = char.charGetName(ch)
    
    # Simulate restocking
    char.charSendRoom(ch, "%s busily restocks the shop inventory." % merchant_name)
    
    # Reset any relevant auxiliary data
    auxiliary.charSetAuxiliaryData(ch, "last_restock", str(mudsys.current_time()))
    
    # Log the action
    mudsys.log_string("Merchant %s restocked inventory." % merchant_name)

# Register the command for NPCs only
mudsys.add_cmd("restock", None, cmd_merchant_restock, "npc", 1)
```

## Best Practices for NPC Creation

### 1. Keep Behaviors Realistic
- Don't make NPCs too chatty
- Add random delays to responses
- Include ambient behaviors sparingly

### 2. Use Auxiliary Data Wisely
- Store persistent information about player interactions
- Track NPC state and mood
- Remember important events

### 3. Handle Edge Cases
```python
# Always check if objects exist
if ch is None or actor is None:
    return

# Validate input
if not arg or len(arg.strip()) == 0:
    # Handle empty input
    pass
```

### 4. Performance Considerations
- Don't do expensive operations in heartbeat functions
- Use random chances to limit ambient actions
- Clean up old auxiliary data periodically

## Common Patterns

### NPC Response Template
```python
def npc_trigger(ch, actor, arg):
    """Template for NPC trigger functions."""
    
    # Validate inputs
    if ch is None or (actor and char.charIsNPC(actor)):
        return
    
    try:
        # Get necessary information
        npc_name = char.charGetName(ch)
        
        # Process the trigger
        # ... your logic here ...
        
        # Provide response
        char.charSendRoom(ch, "Response message")
        
    except Exception as e:
        mudsys.log_string("Error in NPC trigger: %s" % str(e))
```

### State Management
```python
def get_npc_state(ch, key, default=None):
    """Get NPC state from auxiliary data."""
    value = auxiliary.charGetAuxiliaryData(ch, key)
    return value if value is not None else default

def set_npc_state(ch, key, value):
    """Set NPC state in auxiliary data."""
    auxiliary.charSetAuxiliaryData(ch, key, str(value))
```

## Next Steps

Now that you can create basic NPCs:

1. **Try [Building Your First Room](building-your-first-room/)** to create environments for your NPCs
2. **Learn [Basic Triggers and Scripts](basic-triggers-scripts/)** for more advanced behaviors
3. **Explore [Advanced NPC Behaviors](../advanced-npc-behaviors/)** for complex AI systems

## Summary

You've learned to:
- Create character prototypes using OLC
- Write Python scripts for NPC behaviors
- Use triggers to make NPCs interactive
- Implement memory and mood systems
- Follow best practices for NPC design

## Troubleshooting

**NPC not responding to triggers?**
- Check that triggers are properly attached
- Verify the Python module is loaded
- Look for errors in the mud logs

**Triggers firing too often?**
- Add random chances to limit frequency
- Use auxiliary data to track timing
- Consider the performance impact

**NPC behaving strangely?**
- Test each trigger individually
- Add debug logging to your functions
- Check for null pointer issues

Ready to create interactive environments? Continue with [Building Your First Room](building-your-first-room/)!