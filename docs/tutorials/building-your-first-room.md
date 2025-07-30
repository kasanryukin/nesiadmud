---
layout: default
title: Building Your First Room
parent: Start with the Basics
grand_parent: Tutorials
nav_order: 3
permalink: /tutorials/building-your-first-room/
---

# Building Your First Room

Learn to create interactive room environments using room prototypes, from basic rooms to complex areas with dynamic behaviors.

## Overview

This tutorial teaches you how to create rooms using NakedMud's prototype system. You'll build an interactive tavern room with environmental effects, special features, and scripted behaviors that respond to player actions.

## Prerequisites

- Completed [Getting Started with Python Scripting](getting-started-scripting/)
- Completed [Your First NPC](your-first-npc/)
- Understanding of [Room Prototypes](/core-concepts/prototypes/)
- Wizard-level access to your mud

## What You'll Learn

- How to create room prototypes
- Adding environmental effects and atmosphere
- Creating interactive room features
- Using room triggers for dynamic behavior
- Managing room state with auxiliary data
- Best practices for world building

## Step 1: Understanding Room Prototypes

Room prototypes define the template for creating room instances. Let's examine the structure:

```
# Connect to your mud and examine existing rooms
# Use: rlist [zone]
# This shows available room prototypes in a zone
```

A room prototype defines:
- Basic properties (name, description, terrain type)
- Exits and connections
- Environmental features
- Interactive behaviors and triggers
- Special properties and flags

## Step 2: Creating Your First Room Prototype

Let's create an interactive tavern room using NakedMud's OLC system. First, understand the basic room OLC commands:

### Essential OLC Commands for Rooms

- `redit <room_key>` - Create or edit a room prototype
- `rlist [zone]` - List all room prototypes in a zone
- `rview <room_key>` - Show details for a room prototype
- `goto <room_key>` - Go to a room (loads it if needed)
- `zlist` - List all zones

### Creating the Tavern Prototype

```
# In-game commands (as a wizard/builder):
redit tutorial_tavern

# This opens the room editor with a menu like:
# [tutorial_tavern]
# 1) Abstract: yes
# 2) Inherits from prototypes:
# 
# 3) Name
# 
# 4) Description
# 
# L) Land type [inside]
# B) Set Bits: 
# Z) Room can be reset: no
# R) Room reset menu
# X) Extra descriptions menu
# T) Trigger menu
# E) Edit exit
# F) Fill exit
# C) Extra code
```

Set these properties by selecting the menu options:

1. **Abstract**: Select 1 to toggle to `no` (so the room can be loaded)
3. **Name**: `The Cozy Tavern`
4. **Description**: 
```
This warm and inviting tavern bustles with activity. Wooden tables and chairs are scattered throughout the room, while a large stone fireplace crackles merrily in one corner. The bar stretches along the north wall, lined with bottles of various spirits. Soft candlelight flickers from wall sconces, creating dancing shadows on the rough-hewn walls.
```
**L) Land type**: Select L to change terrain if needed (default `inside` is good)
**B) Set Bits**: Select B to add flags like `no_attack` and `peaceful` if desired

### Understanding Room Properties

- **Abstract**: Whether this is a template (yes) or can be loaded (no)
- **Inherits from prototypes**: Parent prototypes to inherit properties from
- **Name**: The room title shown to players
- **Description**: The main room description players see
- **Land type**: Terrain type affecting movement, weather effects, and skills
- **Set Bits**: Special room flags (no_attack, dark, peaceful, etc.)
- **Room can be reset**: Whether the room participates in zone resets
- **Extra descriptions**: Additional details for specific keywords
- **Exits**: Connections to other rooms (managed through E and F options)
- **Extra Code**: Python code that runs when the room loads

### Common Room Terrain Types

- `inside` - Indoor rooms (no weather effects)
- `city` - Urban areas
- `field` - Open grassland
- `forest` - Wooded areas
- `hills` - Hilly terrain
- `mountain` - Mountainous regions
- `water` - Bodies of water
- `underwater` - Submerged areas
- `air` - Flying/floating areas

### Common Room Flags

- `dark` - Room is always dark
- `no_attack` - Combat is disabled
- `peaceful` - No aggressive actions allowed
- `silent` - Sound doesn't carry
- `no_magic` - Magic is disabled
- `indoors` - Weather doesn't affect room

## Step 3: Creating Triggers for Room Behaviors

Now we'll create interactive behaviors for our tavern using NakedMud's trigger system. We'll create several triggers and then attach them to the room.

### Step 3a: Create the Entry Trigger

First, let's create a trigger for when players enter the tavern:

```
# Create the entry trigger:
tedit tavern_enter

# Set up the trigger:
# 1) Name: Tavern entry atmosphere
# 2) Trigger type: enter
# 3) Script Code:
```

In the Script Code editor:

```python
# Tavern entry trigger - creates atmosphere when players enter

import char
import room
import auxiliary
import random

# Don't trigger for NPCs
if char.charIsNPC(actor):
    return

player_name = char.charGetName(actor)

# Welcome messages based on atmosphere
welcomes = [
    "The warm atmosphere of the tavern envelops you as you enter.",
    "Conversations quiet momentarily as you step inside, then resume.",
    "The scent of roasted meat and ale fills your nostrils.",
    "A few patrons glance up from their drinks to nod at you."
]

welcome = random.choice(welcomes)
char.charSend(actor, welcome)

# Announce to others in the room
char.charSendRoom(actor, "%s enters the tavern, looking around curiously." % player_name)

# Track visitor count
visitors = auxiliary.roomGetAuxiliaryData(me, "visitor_count")
if visitors is None:
    visitors = 0
else:
    visitors = int(visitors)

visitors += 1
auxiliary.roomSetAuxiliaryData(me, "visitor_count", str(visitors))
```

### Step 3b: Create the Look Trigger

Create a trigger for special look commands:

```
# Create the look trigger:
tedit tavern_look

# Set up the trigger:
# 1) Name: Tavern special look descriptions
# 2) Trigger type: look
# 3) Script Code:
```

In the Script Code editor:

```python
# Tavern look trigger - handles special look targets

import char

# Only handle specific look targets, let normal room look work normally
if not arg:
    return

target = arg.lower().strip()
player_name = char.charGetName(actor)

# Special look targets
if target in ["fireplace", "fire"]:
    char.charSend(actor, "The stone fireplace crackles warmly, casting dancing shadows on the walls. Logs burn brightly, filling the room with comfortable heat.")
    char.charSendRoom(actor, "%s examines the fireplace closely." % player_name)
    
elif target in ["bar", "bottles"]:
    char.charSend(actor, "The bar is well-stocked with bottles of various shapes and sizes. You can see ales, wines, and stronger spirits arranged neatly on wooden shelves.")
    char.charSendRoom(actor, "%s looks over the selection at the bar." % player_name)
    
elif target in ["tables", "chairs", "furniture"]:
    char.charSend(actor, "The wooden tables and chairs show signs of heavy use but are well-maintained. Each table has candles providing intimate lighting for conversations.")
    char.charSendRoom(actor, "%s examines the tavern furniture." % player_name)
    
elif target in ["candles", "light", "lighting"]:
    char.charSend(actor, "Candles flicker from wall sconces and table tops, creating a warm, inviting atmosphere. The light dances and wavers, making the room feel alive.")
    char.charSendRoom(actor, "%s studies the candlelit atmosphere." % player_name)
```

### Step 3c: Create the Heartbeat Trigger

Create a trigger for atmospheric effects:

```
# Create the heartbeat trigger:
tedit tavern_heartbeat

# Set up the trigger:
# 1) Name: Tavern atmospheric effects
# 2) Trigger type: heartbeat
# 3) Script Code:
```

In the Script Code editor:

```python
# Tavern heartbeat trigger - provides atmospheric effects

import char
import room
import random

# Only do atmospheric effects occasionally
if random.randint(1, 15) > 1:
    return

# Get characters in the room
chars_in_room = room.roomGetChars(me)
players_present = [c for c in chars_in_room if not char.charIsNPC(c)]

# Only do atmospheric effects if players are present
if not players_present:
    return

# Random atmospheric messages
atmospherics = [
    "The fire in the fireplace crackles and pops, sending sparks up the chimney.",
    "A gentle breeze stirs the candle flames, making shadows dance on the walls.",
    "The sound of quiet conversation and clinking glasses fills the air.",
    "Someone laughs heartily at a nearby table.",
    "The bartender polishes a glass with practiced efficiency.",
    "A log shifts in the fireplace, sending up a shower of sparks.",
    "The warm scent of bread and stew wafts from the kitchen.",
    "A patron raises his mug in a silent toast to no one in particular."
]

atmospheric = random.choice(atmospherics)
room.roomSendMessage(me, atmospheric)
```

### Understanding Room Trigger Types

Common room trigger types include:
- **enter**: Fires when someone enters the room
- **leave**: Fires when someone leaves the room  
- **look**: Fires when someone uses the look command
- **heartbeat**: Fires regularly for atmospheric effects
- **speech**: Fires when someone speaks in the room
- **command**: Fires on specific commands

## Step 4: Attaching Triggers to the Room

Now we need to attach the triggers we created to our tavern room:

```
# Edit the tavern room:
redit tutorial_tavern

# The redit screen shows:
# [tutorial_tavern]
# 1) Abstract: no
# 2) Inherits from prototypes:
# 3) Name
# The Cozy Tavern
# 4) Description
# This warm and inviting tavern bustles with activity...
# L) Land type [inside]
# B) Set Bits: 
# Z) Room can be reset: no
# R) Room reset menu
# X) Extra descriptions menu
# T) Trigger menu
# E) Edit exit
# F) Fill exit
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
2. **Enter trigger key**: `tavern_enter`
3. **Select N** again  
4. **Enter trigger key**: `tavern_look`
5. **Select N** again
6. **Enter trigger key**: `tavern_heartbeat`

After attaching all triggers, the menu will show:

```
# Current triggers:
#   tavern_enter
#   tavern_look
#   tavern_heartbeat
#
# N) Add new trigger
# D) Delete trigger
```

### Room Trigger Best Practices

1. **Performance**: Use random chances in heartbeat triggers to avoid spam
2. **Context**: Check if players are present before showing atmospheric effects
3. **Immersion**: Make triggers enhance the environment without being intrusive
4. **Reusability**: Create triggers that can be used in multiple similar rooms

### Using Extra Code for Rooms (Advanced)

The **C) Extra code** option is for additional Python code that runs when the room loads, such as:
- Setting special room properties
- Initializing room-specific data
- Custom room initialization logic

For beginners, using the trigger system (T menu) is the recommended approach.

### Understanding Room Triggers

NakedMud rooms support various trigger types:

- **enter_room** - Fires when someone enters the room
- **leave_room** - Fires when someone leaves the room
- **look** - Fires when someone uses the look command
- **heartbeat** - Fires regularly (every few seconds)
- **speech** - Fires when someone speaks in the room
- **command** - Fires on specific commands
- **sit/stand/sleep** - Fires on position changes
- **get/drop** - Fires when items are manipulated

### Room Trigger Best Practices

1. **Performance**: Use random chances in heartbeat triggers to avoid spam
2. **Context**: Check if players are present before showing atmospheric effects
3. **Immersion**: Make triggers enhance the environment without being intrusive
4. **Testing**: Always test triggers with multiple players present

### Alternative: Using Room Programs

You can also create room programs similar to mob programs:

```
# Room program editor (if available):
rpedit tutorial_tavern

# Add programs for specific triggers and conditions
```

## Step 5: Adding Interactive Features

Let's add more interactive elements to make the room come alive:

```python
# Add to tutorial_tavern.py

def tavern_order_command(ch, cmd, arg):
    """Special command to order drinks in the tavern."""
    
    # Check if player is in a tavern room
    rm = char.charGetRoom(ch)
    if not rm:
        return
    
    # Check if this room has tavern functionality
    room_keywords = room.roomGetKeywords(rm)
    if "tavern" not in room_keywords.lower():
        char.charSend(ch, "You can't order anything here.")
        return
    
    player_name = char.charGetName(ch)
    
    if not arg:
        char.charSend(ch, "What would you like to order? Try 'order ale', 'order wine', or 'order food'.")
        return
    
    item = arg.lower().strip()
    
    # Available items and their descriptions
    menu = {
        "ale": {
            "name": "a frothy mug of ale",
            "desc": "A large wooden mug filled with golden ale, topped with a thick foam head.",
            "action": "%s orders a mug of ale from the bar." % player_name,
            "cost": 5
        },
        "beer": {
            "name": "a cold beer",
            "desc": "A chilled bottle of dark beer with condensation beading on the glass.",
            "action": "%s orders a cold beer." % player_name,
            "cost": 4
        },
        "wine": {
            "name": "a glass of red wine",
            "desc": "A crystal glass filled with deep red wine that catches the candlelight.",
            "action": "%s orders a glass of wine." % player_name,
            "cost": 8
        },
        "food": {
            "name": "a hearty meal",
            "desc": "A wooden plate loaded with roasted meat, vegetables, and fresh bread.",
            "action": "%s orders a meal from the kitchen." % player_name,
            "cost": 12
        },
        "stew": {
            "name": "a bowl of hot stew",
            "desc": "A steaming bowl of thick stew with chunks of meat and vegetables.",
            "action": "%s orders a bowl of stew." % player_name,
            "cost": 10
        }
    }
    
    if item not in menu:
        char.charSend(ch, "Sorry, we don't have that. Try: %s" % ", ".join(menu.keys()))
        return
    
    # For now, just simulate the ordering (no actual economy system)
    order = menu[item]
    
    char.charSend(ch, "You order %s. The server nods and heads to fulfill your request." % order["name"])
    char.charSendRoom(ch, order["action"])
    
    # Simulate delivery with a delay
    event.start_event(ch, random.randint(5, 10), deliver_order, order)

def deliver_order(ch, order):
    """Deliver the ordered item to the player."""
    
    # Make sure player is still in a tavern
    rm = char.charGetRoom(ch)
    if not rm:
        return
    
    room_keywords = room.roomGetKeywords(rm)
    if "tavern" not in room_keywords.lower():
        return
    
    player_name = char.charGetName(ch)
    
    char.charSend(ch, "A server arrives with %s and places it before you." % order["name"])
    char.charSendRoom(ch, "A server delivers %s to %s." % (order["name"], player_name))
    
    # Could create an actual object here, but for now just simulate
    char.charSend(ch, "You now have %s. %s" % (order["name"], order["desc"]))

# Register the order command
mudsys.add_cmd("order", None, tavern_order_command, "player", 1)
```

## Step 6: Environmental State Management

Add a system to track the tavern's state throughout the day:

```python
# Add to tutorial_tavern.py

def get_tavern_atmosphere(rm):
    """Determine the current atmosphere based on various factors."""
    
    # Get current game time (you'll need to implement this based on your mud's time system)
    # For now, we'll use a simple random system
    
    # Count players in the room
    chars_in_room = room.roomGetChars(rm)
    player_count = sum(1 for c in chars_in_room if not char.charIsNPC(c))
    
    # Get visitor count
    visitors = auxiliary.roomGetAuxiliaryData(rm, "visitor_count")
    total_visitors = int(visitors) if visitors else 0
    
    # Determine atmosphere
    if player_count == 0:
        atmosphere = "empty"
    elif player_count == 1:
        atmosphere = "quiet"
    elif player_count < 4:
        atmosphere = "cozy"
    else:
        atmosphere = "bustling"
    
    # Store current atmosphere
    auxiliary.roomSetAuxiliaryData(rm, "current_atmosphere", atmosphere)
    
    return atmosphere

def atmospheric_room_description(rm, actor):
    """Provide atmosphere-based room descriptions."""
    
    atmosphere = get_tavern_atmosphere(rm)
    base_desc = room.roomGetDescription(rm)
    
    # Add atmospheric details
    if atmosphere == "empty":
        addition = " The tavern is quiet and peaceful, with only the crackling fire for company."
    elif atmosphere == "quiet":
        addition = " The tavern has a intimate, quiet atmosphere perfect for contemplation."
    elif atmosphere == "cozy":
        addition = " The tavern has a warm, cozy feeling with the perfect amount of activity."
    elif atmosphere == "bustling":
        addition = " The tavern is alive with activity, filled with laughter and conversation."
    else:
        addition = ""
    
    return base_desc + addition

def enhanced_tavern_look_trigger(rm, actor, arg):
    """Enhanced look trigger that includes atmospheric descriptions."""
    
    if not arg:  # Looking at the room itself
        # Get the atmospheric description
        desc = atmospheric_room_description(rm, actor)
        char.charSend(actor, desc)
        
        # Add current occupancy info
        chars_in_room = room.roomGetChars(rm)
        player_count = sum(1 for c in chars_in_room if not char.charIsNPC(c))
        
        if player_count > 1:
            char.charSend(actor, "There are %d other people here enjoying the tavern's hospitality." % (player_count - 1))
        
        return True  # Indicate we handled the look
    
    # Handle specific look targets (from previous function)
    return tavern_look_trigger(rm, actor, arg)

# Update the registration
mudsys.add_room_method("tavern_look", enhanced_tavern_look_trigger)
```

## Step 7: Creating Exits and Connections

Connect your tavern to the world by adding exits:

```
# In the room editor:
redit tutorial_tavern

# Select: 4. Exit
# This shows current exits and allows you to add new ones

# To add an exit:
# - Choose a direction (north, south, east, west, up, down, etc.)
# - Set the destination room
# - Configure exit properties (door, key, etc.)
```

### Exit Configuration Options

When adding an exit, you can set:

- **Direction**: north, south, east, west, northeast, northwest, southeast, southwest, up, down
- **Destination**: The room key or vnum to connect to
- **Door**: Whether there's a door (none, door, secret door)
- **Key**: Item needed to unlock the door
- **Keywords**: Words to reference the exit/door
- **Description**: What players see when looking at the exit

### Creating Bidirectional Exits

```
# From the tavern, add exit south to main street:
redit tutorial_tavern
# 4. Exit -> south -> main_street_room

# From main street, add exit north to tavern:
redit main_street_room  
# 4. Exit -> north -> tutorial_tavern
```

## Step 8: Room Instance Management

### Loading and Testing Rooms

```
# Go to the room to test (this loads it automatically):
goto tutorial_tavern

# Or if you know the vnum:
goto <room_vnum>
```

### Zone Integration

For permanent rooms, integrate them into zone files:

```
# Edit the zone:
zedit <zone_number>

# Rooms are typically created automatically when:
# - NPCs are loaded into them
# - Objects are loaded into them
# - Players enter them via exits

# But you can force room creation:
# R <room_vnum> - Reset room to default state
```

### Room Management Commands

```
# List rooms in current zone:
rlist

# Find rooms by keyword:
rfind tavern

# Get detailed room information:
rview tutorial_tavern

# Purge room contents:
rpurge tutorial_tavern
```

## Step 9: Testing Your Room

Test the various features:

1. **Enter the room** - Should get atmospheric welcome
2. **Look around** - Try "look fireplace", "look bar", etc.
3. **Sit at table** - Should trigger service interactions
4. **Order something** - Test the ordering system
5. **Wait and observe** - Atmospheric effects should occur
6. **Bring friends** - Test how atmosphere changes with more people

## Step 10: Advanced Room Features

Add more sophisticated room behaviors:

```python
# Add to tutorial_tavern.py

def tavern_weather_effects(rm):
    """Add weather-based atmospheric changes."""
    
    # This would integrate with your mud's weather system
    # For now, we'll simulate different weather effects
    
    weather_effects = {
        "rain": "The sound of rain pattering against the windows adds to the cozy atmosphere.",
        "storm": "Thunder rumbles outside, making the tavern feel like a safe haven.",
        "snow": "Snow falls gently past the frosted windows, making the fire seem even warmer.",
        "clear": "Sunlight streams through the windows, illuminating dancing dust motes."
    }
    
    # Randomly pick weather (in a real implementation, this would come from the weather system)
    current_weather = random.choice(list(weather_effects.keys()))
    effect = weather_effects[current_weather]
    
    # Only show weather effects occasionally
    if random.randint(1, 20) == 1:
        room.roomSendMessage(rm, effect)

def tavern_special_events(rm):
    """Trigger special events in the tavern."""
    
    # Get current atmosphere
    atmosphere = auxiliary.roomGetAuxiliaryData(rm, "current_atmosphere")
    
    # Special events based on atmosphere
    if atmosphere == "bustling" and random.randint(1, 30) == 1:
        events = [
            "A traveling minstrel begins playing a lively tune in the corner.",
            "Someone starts telling an animated story to a gathered crowd.",
            "A friendly drinking contest breaks out at one of the tables.",
            "The tavern keeper announces that the next round is on the house!"
        ]
        event = random.choice(events)
        room.roomSendMessage(rm, event)
    
    elif atmosphere == "quiet" and random.randint(1, 25) == 1:
        events = [
            "An old patron shares a quiet tale of adventure from years past.",
            "The fire crackles extra loudly in the peaceful atmosphere.",
            "A cat wanders in and curls up by the fireplace.",
            "The bartender hums a gentle melody while cleaning glasses."
        ]
        event = random.choice(events)
        room.roomSendMessage(rm, event)

def enhanced_tavern_heartbeat(rm):
    """Enhanced heartbeat with weather and special events."""
    
    # Regular atmospheric effects
    tavern_heartbeat(rm)
    
    # Weather effects
    tavern_weather_effects(rm)
    
    # Special events
    tavern_special_events(rm)

# Update the registration
mudsys.add_room_method("tavern_heartbeat", enhanced_tavern_heartbeat)
```

## Best Practices for Room Creation

### 1. Create Immersive Descriptions
- Use all five senses in descriptions
- Include dynamic elements that change
- Make the environment feel alive

### 2. Balance Interactivity
- Don't overwhelm players with too many special features
- Make interactions feel natural and optional
- Provide clear feedback for player actions

### 3. Use Auxiliary Data Effectively
```python
# Track room state
def set_room_state(rm, key, value):
    auxiliary.roomSetAuxiliaryData(rm, key, str(value))

def get_room_state(rm, key, default=None):
    value = auxiliary.roomGetAuxiliaryData(rm, key)
    return value if value is not None else default
```

### 4. Performance Considerations
- Limit heartbeat frequency for atmospheric effects
- Use random chances to prevent spam
- Clean up old auxiliary data periodically

## Common Patterns

### Room Trigger Template
```python
def room_trigger(rm, actor, arg):
    """Template for room trigger functions."""
    
    # Validate inputs
    if rm is None:
        return
    
    try:
        # Get room information
        room_name = room.roomGetName(rm)
        
        # Process the trigger
        # ... your logic here ...
        
        # Provide feedback
        room.roomSendMessage(rm, "Something happens in the room")
        
    except Exception as e:
        mudsys.log_string("Error in room trigger: %s" % str(e))
```

### Atmospheric Effect System
```python
def add_atmospheric_effect(rm, message, chance=10):
    """Add an atmospheric effect with specified chance."""
    if random.randint(1, chance) == 1:
        room.roomSendMessage(rm, message)
```

## Next Steps

Now that you can create interactive rooms:

1. **Try [Basic Triggers and Scripts](basic-triggers-scripts/)** for more advanced room behaviors
2. **Learn [Advanced Room Interactions](../complex-room-interactions/)** for sophisticated environmental systems
3. **Explore [Object Scripting](../object-scripting-item-types/)** to add interactive items to your rooms

## Summary

You've learned to:
- Create room prototypes using OLC
- Write Python scripts for room behaviors
- Use triggers to make rooms interactive
- Implement atmospheric and environmental effects
- Manage room state with auxiliary data
- Follow best practices for world building

## Troubleshooting

**Room triggers not firing?**
- Check that triggers are properly attached
- Verify the Python module is loaded
- Look for errors in the mud logs

**Too many atmospheric messages?**
- Reduce the frequency of heartbeat effects
- Use higher random number ranges
- Consider player count before showing effects

**Room descriptions not updating?**
- Make sure you're overriding the look trigger properly
- Check that auxiliary data is being stored correctly
- Verify the atmospheric calculation logic

Ready to add more complex behaviors? Continue with [Basic Triggers and Scripts](basic-triggers-scripts/)!