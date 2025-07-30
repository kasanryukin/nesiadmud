---
layout: default
title: event Module
parent: Modules
grand_parent: API Reference
nav_order: 3
---

# event Module

The `event` module handles delayed function calls and timed events in the MUD. It provides a robust system for scheduling actions to occur after a specified delay, making it essential for implementing time-based game mechanics.

**Module Type**: Core EFuns (External Functions)  
**Import**: `import event`

## Overview

The event system is used for:
- Delayed actions (e.g., spell effects, healing over time)
- Timed sequences (e.g., combat rounds, respawn timers)
- Scheduled maintenance tasks
- Animation and atmospheric effects
- Cooldown timers

Events are automatically cancelled when their owner is extracted from the game, preventing memory leaks and orphaned events.

## Core Functions

### start_event(owner, delay, event_func, data=None, arg='')

**Returns**: `None`

Queues a new delayed event to execute after the specified delay.

**Parameters**:
- `owner` (PyChar, PyObj, PyRoom, or None): The event owner - events are cancelled when owner is extracted
- `delay` (float): Delay in seconds before the event fires
- `event_func` (function): Function to call when event fires
- `data` (any, optional): Optional data of any type to pass to the event function
- `arg` (str, optional): Optional string argument to pass to the event function

**Event Function Signature**:
The event function must accept three parameters:
```python
def event_function(owner, data, arg):
    # owner: The event owner (or None)
    # data: The data parameter passed to start_event
    # arg: The string argument passed to start_event
    pass
```

**Example**:
```python
import event

def heal_character(owner, data, arg):
    if owner and not owner.is_dead():
        heal_amount = data
        owner.hit_points += heal_amount
        owner.send(f"You feel better! (+{heal_amount} HP)")

# Heal the character for 50 HP after 10 seconds
event.start_event(character, 10.0, heal_character, 50, "healing spell")
```

### interrupt_events_involving(thing)

**Returns**: `None`

Interrupts and cancels all events involving the specified object, room, or character.

**Parameters**:
- `thing` (PyChar, PyObj, or PyRoom): The object whose events should be cancelled

**Example**:
```python
import event

# Cancel all events involving a character (e.g., when they die)
event.interrupt_events_involving(character)

# Cancel all events involving a room (e.g., when it's being reset)
event.interrupt_events_involving(room)
```

### start_update(...)

**Returns**: `None`

**Deprecated**: This function is deprecated. For repeating events, use events that manually re-queue themselves.

## Usage Patterns

### Simple Delayed Action

```python
import event

def delayed_message(owner, data, arg):
    if owner:
        owner.send(data)

# Send a message after 5 seconds
event.start_event(character, 5.0, delayed_message, "Time's up!", "")
```

### Repeating Events

Since `start_update` is deprecated, create repeating events by having the event function re-queue itself:

```python
import event

def repeating_heal(owner, data, arg):
    if owner and not owner.is_dead():
        heal_amount = data
        owner.hit_points += heal_amount
        owner.send(f"Regeneration heals you for {heal_amount} HP.")
        
        # Re-queue the event for another 30 seconds
        event.start_event(owner, 30.0, repeating_heal, heal_amount, arg)
    else:
        # Stop the repeating event if owner is dead or gone
        if owner:
            owner.send("Your regeneration effect ends.")

# Start a repeating heal every 30 seconds
event.start_event(character, 30.0, repeating_heal, 10, "regen")
```

### Complex Event Data

Events can pass complex data structures:

```python
import event

def spell_effect_end(owner, data, arg):
    if owner:
        spell_name = data['name']
        stat_bonus = data['bonus']
        stat_type = data['stat']
        
        # Remove the spell effect
        owner.send(f"The {spell_name} spell wears off.")
        # Restore original stats (implementation depends on your stat system)

# Start a temporary stat boost
spell_data = {
    'name': 'Strength of the Bear',
    'bonus': 5,
    'stat': 'strength'
}

event.start_event(character, 300.0, spell_effect_end, spell_data, "buff")
```

### Event Chains

Create sequences of events:

```python
import event

def event_chain_step1(owner, data, arg):
    if owner:
        owner.send("The ritual begins...")
        event.start_event(owner, 3.0, event_chain_step2, data, arg)

def event_chain_step2(owner, data, arg):
    if owner:
        owner.send("Mystical energies swirl around you...")
        event.start_event(owner, 3.0, event_chain_step3, data, arg)

def event_chain_step3(owner, data, arg):
    if owner:
        owner.send("The ritual is complete! You feel empowered.")
        # Apply final effect here

# Start the chain
event.start_event(character, 1.0, event_chain_step1, None, "ritual")
```

### Room-Based Events

Events can be owned by rooms for environmental effects:

```python
import event

def room_atmosphere(owner, data, arg):
    if owner:  # owner is the room
        message = data
        # Send message to all characters in the room
        for ch in owner.chars:
            ch.send(message)
        
        # Schedule next atmospheric message
        import random
        next_delay = random.randint(60, 180)  # 1-3 minutes
        event.start_event(owner, next_delay, room_atmosphere, message, arg)

# Start atmospheric messages in a room
messages = [
    "A gentle breeze rustles through the trees.",
    "You hear the distant call of a bird.",
    "Sunlight filters through the canopy above."
]

import random
event.start_event(room, 60.0, room_atmosphere, random.choice(messages), "atmosphere")
```

### Combat Events

Events are commonly used in combat systems:

```python
import event

def combat_round(owner, data, arg):
    if owner and owner.fighting:
        target = owner.fighting
        
        # Perform attack
        damage = calculate_damage(owner, target)
        target.hit_points -= damage
        
        owner.send(f"You hit {target.name} for {damage} damage!")
        target.send(f"{owner.name} hits you for {damage} damage!")
        
        # Check if combat continues
        if target.hit_points > 0 and owner.hit_points > 0:
            # Schedule next combat round
            event.start_event(owner, 3.0, combat_round, data, arg)
        else:
            # Combat ends
            end_combat(owner, target)

def start_combat(attacker, defender):
    attacker.fighting = defender
    defender.fighting = attacker
    
    # Start combat rounds for both participants
    event.start_event(attacker, 1.0, combat_round, None, "combat")
    event.start_event(defender, 2.0, combat_round, None, "combat")
```

### Cooldown System

Implement ability cooldowns:

```python
import event

def remove_cooldown(owner, data, arg):
    if owner:
        ability_name = data
        # Remove from cooldown list (implementation depends on your system)
        owner.send(f"{ability_name} is ready to use again.")

def use_ability(character, ability_name, cooldown_seconds):
    # Check if ability is on cooldown
    if is_on_cooldown(character, ability_name):
        character.send(f"{ability_name} is still on cooldown.")
        return False
    
    # Use the ability
    perform_ability(character, ability_name)
    
    # Start cooldown
    add_to_cooldown(character, ability_name)
    event.start_event(character, cooldown_seconds, remove_cooldown, ability_name, "cooldown")
    
    return True
```

## Event Ownership and Cleanup

### Automatic Cleanup

Events are automatically cancelled when their owner is extracted:

```python
import event

# This event will be automatically cancelled if the character quits or dies
event.start_event(character, 60.0, some_function, data, "")

# This event will be cancelled if the room is destroyed
event.start_event(room, 30.0, room_function, data, "")

# This event will be cancelled if the object is destroyed
event.start_event(obj, 45.0, obj_function, data, "")
```

### Ownerless Events

Events can have no owner (owner=None) for global effects:

```python
import event

def global_announcement(owner, data, arg):
    # owner will be None
    message = data
    # Send to all players online
    for player in get_all_players():
        player.send(message)

# Global event with no owner - will not be automatically cancelled
event.start_event(None, 3600.0, global_announcement, "Server maintenance in 1 hour.", "")
```

### Manual Event Interruption

Use `interrupt_events_involving` to manually cancel events:

```python
import event

# Cancel all events for a character when they enter a safe zone
def enter_safe_zone(character, room):
    event.interrupt_events_involving(character)
    character.send("All ongoing effects are cancelled in this safe zone.")

# Cancel room events when resetting an area
def reset_area(room_list):
    for room in room_list:
        event.interrupt_events_involving(room)
```

## Best Practices

### Error Handling

Always check if the owner still exists and is valid:

```python
def safe_event_function(owner, data, arg):
    # Check if owner still exists and is valid
    if not owner:
        return
    
    # Check specific conditions
    if hasattr(owner, 'is_dead') and owner.is_dead():
        return
    
    # Proceed with event logic
    owner.send("Event executed successfully!")
```

### Event Data Management

Keep event data simple and avoid circular references:

```python
# Good: Simple data
event.start_event(character, 10.0, heal_function, 50, "heal")

# Good: Dictionary with simple values
event_data = {'amount': 50, 'type': 'heal', 'source': 'potion'}
event.start_event(character, 10.0, complex_heal, event_data, "")

# Avoid: Complex objects that might create circular references
# event.start_event(character, 10.0, bad_function, character, "")  # Don't do this
```

### Timing Considerations

- Use appropriate delays for game balance
- Consider server performance with many simultaneous events
- Use random delays to prevent synchronized events

```python
import random

# Add randomness to prevent all events firing simultaneously
base_delay = 60.0
random_delay = base_delay + random.uniform(-10.0, 10.0)
event.start_event(owner, random_delay, function, data, arg)
```

## Common Patterns

### Delayed Command Execution

```python
def delayed_command(owner, data, arg):
    if owner:
        command = data
        owner.act(command)

# Execute a command after a delay
event.start_event(character, 5.0, delayed_command, "say The spell is complete!", "")
```

### Temporary Effects

```python
def remove_temporary_effect(owner, data, arg):
    if owner:
        effect_name = data
        owner.remove_effect(effect_name)
        owner.send(f"The {effect_name} effect wears off.")

def apply_temporary_effect(character, effect_name, duration):
    character.add_effect(effect_name)
    character.send(f"You are affected by {effect_name}.")
    event.start_event(character, duration, remove_temporary_effect, effect_name, "")
```

### Respawn Timers

```python
def respawn_mob(owner, data, arg):
    # owner is None for respawn events
    room_key = data['room']
    mob_key = data['mob']
    
    room = get_room(room_key)
    if room:
        mob = create_mob(mob_key)
        mob.to_room(room)

def schedule_respawn(room, mob_prototype, delay):
    respawn_data = {'room': room.key, 'mob': mob_prototype}
    event.start_event(None, delay, respawn_mob, respawn_data, "respawn")
```

## See Also

- [mudsys Module](mudsys.md) - Core system functions
- [auxiliary Module](auxiliary.md) - Auxiliary data system
- [char Module](char.md) - Character functions
- [Core Concepts: Event System](../../core-concepts/event-system.md)
- [Tutorials: Using Events](../../tutorials/event-tutorial.md)