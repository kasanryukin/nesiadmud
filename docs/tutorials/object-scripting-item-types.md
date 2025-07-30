---
layout: default
title: Object Scripting and Item Types
parent: Build Complexity
grand_parent: Tutorials
nav_order: 3
permalink: /tutorials/object-scripting-item-types/
---

# Object Scripting and Item Types

Learn to create sophisticated interactive objects with complex behaviors, custom item types, and advanced scripting systems.

## Overview

This tutorial teaches you how to create interactive objects that respond to player actions with complex behaviors. You'll learn to build custom item types, implement object state systems, and create objects that interact with each other and the environment.

## Prerequisites

- Completed [Basic Triggers and Scripts](basic-triggers-scripts/)
- Understanding of [Auxiliary Data](/core-concepts/auxiliary-data/)
- Familiarity with object prototypes
- Intermediate Python programming skills

## What You'll Learn

- Creating interactive object behaviors
- Building custom item types and categories
- Implementing object state management
- Creating objects that interact with each other
- Advanced object scripting patterns
- Performance optimization for object systems

## Step 1: Creating Your First Interactive Object

Let's start by creating a simple interactive magic stone that responds to player actions. We'll use the trigger system to make it interactive.

### Step 1a: Create the Get Trigger

First, create a trigger for when the stone is picked up:

```
# Create the get trigger:
tedit magic_stone_get

# Set up the trigger:
# 1) Name: Magic stone pickup effects
# 2) Trigger type: get
# 3) Script Code:
```

In the Script Code editor:

```python
# Magic stone get trigger - fires when picked up

import char
import auxiliary

if char.charIsNPC(actor):
    return

actor_name = char.charGetName(actor)

# Check if this is the first time picking it up
first_pickup = auxiliary.objGetAuxiliaryData(me, "first_pickup_%s" % actor_name.lower())

if first_pickup is None:
    # First time pickup
    auxiliary.objSetAuxiliaryData(me, "first_pickup_%s" % actor_name.lower(), "true")
    
    char.charSend(actor, "As you pick up the stone, it begins to glow with a soft blue light!")
    char.charSendRoom(actor, "%s picks up a stone that suddenly begins glowing!" % actor_name)
    
    # Give the player some information
    char.charSend(actor, "The stone feels warm in your hands and seems to pulse with magical energy.")
    
else:
    # Subsequent pickups
    char.charSend(actor, "The familiar warmth of the magic stone fills your hands.")
    char.charSendRoom(actor, "%s picks up the glowing stone." % actor_name)
```

### Step 1b: Create the Drop Trigger

```
# Create the drop trigger:
tedit magic_stone_drop

# Set up the trigger:
# 1) Name: Magic stone drop effects
# 2) Trigger type: drop
# 3) Script Code:
```

In the Script Code editor:

```python
# Magic stone drop trigger - fires when dropped

import char
import auxiliary

if char.charIsNPC(actor):
    return

actor_name = char.charGetName(actor)

char.charSend(actor, "The stone's glow fades as you set it down.")
char.charSendRoom(actor, "The stone %s drops loses its magical glow." % actor_name)

# Track how many times it's been dropped
drops = auxiliary.objGetAuxiliaryData(me, "drop_count")
if drops is None:
    drops = 0
else:
    drops = int(drops)

drops += 1
auxiliary.objSetAuxiliaryData(me, "drop_count", str(drops))

# Special message if dropped many times
if drops > 5:
    char.charSend(actor, "The stone seems to flicker with annoyance at being dropped so often.")
```

### Step 1c: Create the Look Trigger

```
# Create the look trigger:
tedit magic_stone_look

# Set up the trigger:
# 1) Name: Magic stone examination
# 2) Trigger type: look
# 3) Script Code:
```

In the Script Code editor:

```python
# Magic stone look trigger - provides detailed examination

import char
import auxiliary

actor_name = char.charGetName(actor)

# Get the stone's current state
drop_count = auxiliary.objGetAuxiliaryData(me, "drop_count")
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
if char.charHasObj(actor, me):
    desc += " It feels warm and alive in your hands."
else:
    desc += " It sits quietly, waiting to be picked up."

char.charSend(actor, desc)
```

### Step 1d: Create the Magic Stone Object

Now create the object and attach the triggers:

```
# Create the object prototype:
oedit tutorial_magic_stone

# The oedit screen shows:
# [tutorial_magic_stone]
# 1) Abstract: yes
# 2) Inherits from prototypes:
# 
# 3) Name:
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
# W) Weight         : 
# B) Edit bitvector : 
# T) Trigger menu
# X) Extra Descriptions menu
# C) Extra code

# Set these properties:
# 1) Abstract: Toggle to 'no'
# 3) Name: a glowing magic stone
# 5) Keywords: stone magic glowing mystical
# 6) Room description: A smooth, oval stone glows with mystical energy.
# 8) Description: This stone pulses with magical energy.
# W) Weight: 1
```

### Step 1e: Attach the Triggers

In the oedit screen, select **T) Trigger menu**:

1. **Select N** (Add new trigger)
2. **Enter trigger key**: `magic_stone_get`
3. **Select N** again
4. **Enter trigger key**: `magic_stone_drop`
5. **Select N** again
6. **Enter trigger key**: `magic_stone_look`

### Testing the Magic Stone

```
# Load the object:
load object tutorial_magic_stone

# Test the triggers:
get stone     # Should show pickup effects
look stone    # Should show detailed description
drop stone    # Should show drop effects
get stone     # Should show different message (not first time)
```

## Step 2: Advanced Interactive Object Systems

Now let's look at more sophisticated interactive object systems:

```python
# File: lib/pymodules/advanced_object_scripting.py

import mudsys
import char
import room
import obj
import auxiliary
import random
import event

class ObjectState:
    """Manage complex object state and behavior."""
    
    def __init__(self, object_ref):
        self.object = object_ref
        self.object_name = obj.objGetName(object_ref) if object_ref else "Unknown"
    
    def get_state(self, key, default=None):
        """Get object state from auxiliary data."""
        value = auxiliary.objGetAuxiliaryData(self.object, key)
        return value if value is not None else default
    
    def set_state(self, key, value):
        """Set object state in auxiliary data."""
        auxiliary.objSetAuxiliaryData(self.object, key, str(value))
    
    def get_numeric_state(self, key, default=0):
        """Get numeric object state."""
        value = self.get_state(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def modify_state(self, key, delta, min_val=None, max_val=None):
        """Modify numeric object state."""
        current = self.get_numeric_state(key, 0)
        new_value = current + delta
        
        if min_val is not None:
            new_value = max(new_value, min_val)
        if max_val is not None:
            new_value = min(new_value, max_val)
        
        self.set_state(key, new_value)
        return new_value

def magical_weapon_system(weapon, actor, action_type):
    """Advanced magical weapon with evolving properties."""
    
    if char.charIsNPC(actor):
        return
    
    state = ObjectState(weapon)
    actor_name = char.charGetName(actor)
    weapon_name = obj.objGetName(weapon)
    
    # Track weapon usage and experience
    if action_type == "wield":
        # Weapon is being wielded
        state.set_state("wielder", actor_name.lower())
        state.set_state("wield_time", mudsys.current_time())
        
        # Check weapon's bond with this wielder
        bond_key = f"bond_{actor_name.lower()}"
        bond_level = state.get_numeric_state(bond_key, 0)
        
        if bond_level == 0:
            char.charSend(actor, f"As you grasp {weapon_name}, it feels cold and unfamiliar.")
        elif bond_level < 25:
            char.charSend(actor, f"{weapon_name} warms slightly to your touch.")
        elif bond_level < 50:
            char.charSend(actor, f"{weapon_name} feels comfortable and familiar in your hands.")
        elif bond_level < 75:
            char.charSend(actor, f"{weapon_name} seems to resonate with your fighting spirit!")
        else:
            char.charSend(actor, f"{weapon_name} pulses with power, perfectly attuned to your will!")
            char.charSendRoom(actor, f"{weapon_name} glows briefly as {actor_name} wields it.")
    
    elif action_type == "unwield":
        # Weapon is being unwielded
        wielder = state.get_state("wielder")
        if wielder == actor_name.lower():
            wield_duration = mudsys.current_time() - state.get_numeric_state("wield_time", 0)
            
            # Increase bond based on wield time
            bond_key = f"bond_{actor_name.lower()}"
            bond_increase = min(5, wield_duration // 60)  # 1 point per minute, max 5
            new_bond = state.modify_state(bond_key, bond_increase, 0, 100)
            
            state.set_state("wielder", "")
            
            if bond_increase > 0:
                char.charSend(actor, f"You feel your connection to {weapon_name} has grown stronger.")
    
    elif action_type == "combat_use":
        # Weapon used in combat
        wielder = state.get_state("wielder")
        if wielder == actor_name.lower():
            # Increase combat experience
            combat_exp = state.modify_state("combat_experience", 1, 0, 1000)
            
            # Check for weapon evolution
            check_weapon_evolution(weapon, actor, combat_exp)

def check_weapon_evolution(weapon, actor, combat_exp):
    """Check if weapon should evolve based on experience."""
    
    state = ObjectState(weapon)
    actor_name = char.charGetName(actor)
    weapon_name = obj.objGetName(weapon)
    
    current_tier = state.get_numeric_state("evolution_tier", 1)
    
    # Evolution thresholds
    evolution_thresholds = {
        2: 100,   # Tier 2 at 100 combat uses
        3: 300,   # Tier 3 at 300 combat uses
        4: 600,   # Tier 4 at 600 combat uses
        5: 1000   # Tier 5 at 1000 combat uses
    }
    
    for tier, threshold in evolution_thresholds.items():
        if combat_exp >= threshold and current_tier < tier:
            # Weapon evolves!
            state.set_state("evolution_tier", tier)
            
            char.charSend(actor, f"{weapon_name} suddenly blazes with power!")
            char.charSendRoom(actor, f"{weapon_name} in {actor_name}'s hands erupts with magical energy!")
            
            # Apply evolution effects
            apply_weapon_evolution(weapon, actor, tier)
            break

def apply_weapon_evolution(weapon, actor, new_tier):
    """Apply evolution effects to a weapon."""
    
    state = ObjectState(weapon)
    actor_name = char.charGetName(actor)
    weapon_name = obj.objGetName(weapon)
    
    evolution_effects = {
        2: {
            "name_suffix": " of Sharpness",
            "description": "The blade gleams with supernatural sharpness.",
            "message": f"{weapon_name} has evolved! It now cuts through armor more easily."
        },
        3: {
            "name_suffix": " of Power",
            "description": "Runes of power glow along the weapon's surface.",
            "message": f"{weapon_name} pulses with enhanced power! Your strikes hit harder."
        },
        4: {
            "name_suffix": " of Mastery",
            "description": "The weapon seems to anticipate your every move.",
            "message": f"{weapon_name} has achieved mastery! It guides your attacks with precision."
        },
        5: {
            "name_suffix": " of Legend",
            "description": "This legendary weapon radiates an aura of incredible power.",
            "message": f"{weapon_name} has become legendary! Its power is beyond mortal comprehension."
        }
    }
    
    if new_tier in evolution_effects:
        effect = evolution_effects[new_tier]
        
        # Update weapon properties (in a real implementation)
        # obj.objSetName(weapon, weapon_name + effect["name_suffix"])
        # obj.objSetDescription(weapon, effect["description"])
        
        char.charSend(actor, effect["message"])
        
        # Log the evolution
        mudsys.log_string(f"Weapon {weapon_name} evolved to tier {new_tier} for player {actor_name}")

# Register magical weapon system
mudsys.add_obj_method("magical_weapon", magical_weapon_system)
```

## Step 2: Custom Item Types and Categories

Create specialized item types with unique behaviors:

```python
# Add to advanced_object_scripting.py

class ItemTypeManager:
    """Manage different item types and their behaviors."""
    
    @staticmethod
    def get_item_type(obj_ref):
        """Get the item type of an object."""
        state = ObjectState(obj_ref)
        return state.get_state("item_type", "generic")
    
    @staticmethod
    def set_item_type(obj_ref, item_type):
        """Set the item type of an object."""
        state = ObjectState(obj_ref)
        state.set_state("item_type", item_type)
    
    @staticmethod
    def initialize_item_type(obj_ref, item_type, properties=None):
        """Initialize an object with a specific item type."""
        state = ObjectState(obj_ref)
        state.set_state("item_type", item_type)
        
        if properties:
            for key, value in properties.items():
                state.set_state(key, value)

def alchemical_potion_system(potion, actor, action_type):
    """System for alchemical potions with complex effects."""
    
    if char.charIsNPC(actor):
        return
    
    state = ObjectState(potion)
    actor_name = char.charGetName(actor)
    potion_name = obj.objGetName(potion)
    
    # Get potion properties
    potion_type = state.get_state("potion_type", "healing")
    potency = state.get_numeric_state("potency", 50)
    purity = state.get_numeric_state("purity", 75)
    age = state.get_numeric_state("age_days", 0)
    
    if action_type == "drink":
        # Apply potion effects
        apply_potion_effects(potion, actor, potion_type, potency, purity, age)
        
        # Potion is consumed
        char.charSend(actor, f"You drink {potion_name}. The liquid has a {get_potion_taste(potion_type, purity)} taste.")
        char.charSendRoom(actor, f"{actor_name} drinks {potion_name}.")
        
        # Remove the potion (in a real implementation)
        # obj.objDestroy(potion)
        
    elif action_type == "examine":
        # Detailed examination
        description = get_potion_description(potion_type, potency, purity, age)
        char.charSend(actor, description)
        
    elif action_type == "smell":
        # Smell the potion
        smell_desc = get_potion_smell(potion_type, purity, age)
        char.charSend(actor, f"You smell {potion_name}. {smell_desc}")

def apply_potion_effects(potion, actor, potion_type, potency, purity, age):
    """Apply the effects of drinking a potion."""
    
    actor_name = char.charGetName(actor)
    
    # Age affects potency (potions get weaker over time)
    effective_potency = max(10, potency - (age // 7))  # Lose potency weekly
    
    # Purity affects side effects
    side_effect_chance = max(0, 100 - purity)
    
    if potion_type == "healing":
        # Healing potion effects
        healing_amount = effective_potency
        char.charSend(actor, f"You feel your wounds healing! (Healing: {healing_amount})")
        
        if random.randint(1, 100) <= side_effect_chance:
            char.charSend(actor, "The impure potion makes you feel slightly nauseous.")
    
    elif potion_type == "strength":
        # Strength enhancement potion
        duration = effective_potency // 5  # Duration in minutes
        char.charSend(actor, f"You feel incredibly strong! (Duration: {duration} minutes)")
        
        # Set temporary effect (in a real implementation, this would use the effect system)
        state = ObjectState(actor)  # This would be a character state system
        
        if random.randint(1, 100) <= side_effect_chance:
            char.charSend(actor, "Your muscles ache from the impure enhancement.")
    
    elif potion_type == "invisibility":
        # Invisibility potion
        duration = effective_potency // 3
        char.charSend(actor, f"You fade from view! (Duration: {duration} minutes)")
        char.charSendRoom(actor, f"{actor_name} fades from view!")
        
        if random.randint(1, 100) <= side_effect_chance:
            char.charSend(actor, "The impure potion makes you flicker in and out of visibility.")
    
    elif potion_type == "poison":
        # Poison (could be accidental or intentional)
        damage = effective_potency // 2
        char.charSend(actor, f"You feel poison coursing through your veins! (Damage: {damage})")
        
        # Purity actually makes poison worse
        if purity > 80:
            char.charSend(actor, "This is a particularly pure and deadly poison!")

def get_potion_description(potion_type, potency, purity, age):
    """Get detailed potion description."""
    
    # Base descriptions by type
    base_descriptions = {
        "healing": "This red liquid glows with restorative energy.",
        "strength": "This thick, golden potion seems to pulse with power.",
        "invisibility": "This clear, shimmering liquid seems to bend light around it.",
        "poison": "This dark, viscous liquid has an ominous appearance."
    }
    
    desc = base_descriptions.get(potion_type, "This mysterious potion defies easy description.")
    
    # Add potency indicators
    if potency > 80:
        desc += " It radiates incredible magical power."
    elif potency > 60:
        desc += " It glows with strong magical energy."
    elif potency > 40:
        desc += " It has a moderate magical aura."
    elif potency > 20:
        desc += " It has a weak magical presence."
    else:
        desc += " Its magical energy is barely detectable."
    
    # Add purity indicators
    if purity > 90:
        desc += " The liquid is crystal clear and pure."
    elif purity > 70:
        desc += " The liquid is mostly clear with slight cloudiness."
    elif purity > 50:
        desc += " The liquid is somewhat cloudy."
    elif purity > 30:
        desc += " The liquid is quite murky."
    else:
        desc += " The liquid is thick and contaminated."
    
    # Add age indicators
    if age > 30:
        desc += " The potion shows signs of age and deterioration."
    elif age > 14:
        desc += " The potion appears to be getting old."
    elif age > 7:
        desc += " The potion is past its prime."
    
    return desc

def get_potion_taste(potion_type, purity):
    """Get potion taste description."""
    
    base_tastes = {
        "healing": "sweet and warming",
        "strength": "bitter but energizing",
        "invisibility": "tasteless and ethereal",
        "poison": "acrid and burning"
    }
    
    base_taste = base_tastes.get(potion_type, "strange and indescribable")
    
    if purity < 50:
        return f"{base_taste}, with an unpleasant aftertaste"
    elif purity < 75:
        return f"{base_taste}, with a slight bitter note"
    else:
        return base_taste

def get_potion_smell(potion_type, purity, age):
    """Get potion smell description."""
    
    base_smells = {
        "healing": "herbs and honey",
        "strength": "iron and ozone",
        "invisibility": "nothing at all",
        "poison": "sulfur and decay"
    }
    
    smell = f"It smells of {base_smells.get(potion_type, 'unknown chemicals')}"
    
    if age > 14:
        smell += ", with notes of staleness"
    
    if purity < 60:
        smell += ", mixed with unpleasant impurities"
    
    return smell + "."

# Register potion system
mudsys.add_obj_method("alchemical_potion", alchemical_potion_system)
```

## Step 3: Interactive Object Networks

Create objects that interact with each other:

```python
# Add to advanced_object_scripting.py

class ObjectNetwork:
    """Manage networks of interacting objects."""
    
    def __init__(self, network_id):
        self.network_id = network_id
        self.objects = []
    
    def add_object(self, obj_ref):
        """Add an object to this network."""
        self.objects.append(obj_ref)
        
        # Mark object as part of this network
        state = ObjectState(obj_ref)
        state.set_state("network_id", self.network_id)
    
    def get_network_state(self, key, default=None):
        """Get network-wide state (stored in first object)."""
        if not self.objects:
            return default
        
        state = ObjectState(self.objects[0])
        return state.get_state(f"network_{self.network_id}_{key}", default)
    
    def set_network_state(self, key, value):
        """Set network-wide state."""
        if not self.objects:
            return
        
        state = ObjectState(self.objects[0])
        state.set_state(f"network_{self.network_id}_{key}", value)
    
    def broadcast_to_network(self, message, exclude_obj=None):
        """Send a message to all rooms containing network objects."""
        rooms_messaged = set()
        
        for obj_ref in self.objects:
            if obj_ref == exclude_obj:
                continue
            
            # Get the room this object is in
            obj_room = obj.objGetRoom(obj_ref)  # This would be the actual function
            if obj_room and obj_room not in rooms_messaged:
                room.roomSendMessage(obj_room, message)
                rooms_messaged.add(obj_room)

def crystal_resonance_network(crystal, actor, action_type):
    """Network of crystals that resonate with each other."""
    
    state = ObjectState(crystal)
    network_id = state.get_state("network_id")
    
    if not network_id or network_id != "crystal_resonance":
        return
    
    if char.charIsNPC(actor):
        return
    
    actor_name = char.charGetName(actor)
    crystal_name = obj.objGetName(crystal)
    
    if action_type == "touch":
        # Touching a crystal activates the network
        crystal_color = state.get_state("crystal_color", "clear")
        resonance_frequency = state.get_numeric_state("resonance_frequency", 440)
        
        char.charSend(actor, f"You touch {crystal_name}. It begins to glow with {crystal_color} light!")
        char.charSendRoom(actor, f"{actor_name} touches {crystal_name}, causing it to glow brightly.")
        
        # Activate the network
        network = ObjectNetwork("crystal_resonance")
        network.add_object(crystal)  # In reality, you'd load all network objects
        
        # Set the activation frequency
        network.set_network_state("active_frequency", resonance_frequency)
        network.set_network_state("activated_by", actor_name)
        
        # Trigger resonance in other crystals
        trigger_crystal_resonance(crystal, resonance_frequency)
        
    elif action_type == "attune":
        # Attuning changes the crystal's frequency
        new_frequency = random.randint(200, 800)
        state.set_state("resonance_frequency", new_frequency)
        
        char.charSend(actor, f"You attune {crystal_name} to a new frequency ({new_frequency} Hz).")
        char.charSendRoom(actor, f"{crystal_name} hums as {actor_name} attunes it to a new frequency.")

def trigger_crystal_resonance(source_crystal, frequency):
    """Trigger resonance effects in the crystal network."""
    
    # In a real implementation, this would find all crystals in the network
    # and trigger effects based on frequency matching
    
    source_state = ObjectState(source_crystal)
    network_id = source_state.get_state("network_id")
    
    if network_id == "crystal_resonance":
        # Create network and broadcast resonance
        network = ObjectNetwork("crystal_resonance")
        
        resonance_message = f"Crystals throughout the area begin to resonate at {frequency} Hz!"
        network.broadcast_to_network(resonance_message, source_crystal)
        
        # Log the resonance event
        mudsys.log_string(f"Crystal resonance triggered at frequency {frequency}")

def mechanical_clockwork_system(device, actor, action_type):
    """Complex mechanical device with interconnected parts."""
    
    state = ObjectState(device)
    device_name = obj.objGetName(device)
    
    if char.charIsNPC(actor):
        return
    
    actor_name = char.charGetName(actor)
    
    # Get device state
    power_level = state.get_numeric_state("power_level", 0)
    gear_alignment = state.get_state("gear_alignment", "neutral")
    spring_tension = state.get_numeric_state("spring_tension", 50)
    
    if action_type == "wind":
        # Wind the clockwork mechanism
        if power_level >= 100:
            char.charSend(actor, f"{device_name} is already fully wound.")
            return
        
        wind_amount = random.randint(15, 25)
        new_power = state.modify_state("power_level", wind_amount, 0, 100)
        new_tension = state.modify_state("spring_tension", wind_amount//2, 0, 100)
        
        char.charSend(actor, f"You wind {device_name}. The springs tighten and gears begin to turn.")
        char.charSendRoom(actor, f"{actor_name} winds {device_name}, causing it to tick and whir.")
        
        if new_power >= 100:
            char.charSend(actor, f"{device_name} is now fully powered!")
            # Trigger any powered effects
            activate_clockwork_device(device)
    
    elif action_type == "adjust":
        # Adjust gear alignment
        alignments = ["neutral", "forward", "reverse", "precision", "power"]
        current_index = alignments.index(gear_alignment) if gear_alignment in alignments else 0
        new_index = (current_index + 1) % len(alignments)
        new_alignment = alignments[new_index]
        
        state.set_state("gear_alignment", new_alignment)
        
        char.charSend(actor, f"You adjust {device_name}'s gears to {new_alignment} configuration.")
        char.charSendRoom(actor, f"{actor_name} adjusts the gears on {device_name}.")
        
        # Different alignments have different effects
        apply_gear_alignment_effects(device, new_alignment)
    
    elif action_type == "examine":
        # Detailed examination of the mechanism
        description = get_clockwork_description(device_name, power_level, gear_alignment, spring_tension)
        char.charSend(actor, description)

def activate_clockwork_device(device):
    """Activate a fully powered clockwork device."""
    
    state = ObjectState(device)
    device_name = obj.objGetName(device)
    device_type = state.get_state("device_type", "generic")
    
    if device_type == "music_box":
        # Play a musical sequence
        device_room = obj.objGetRoom(device)
        if device_room:
            room.roomSendMessage(device_room, f"{device_name} begins playing a beautiful, haunting melody.")
            
            # Schedule the melody to continue
            event.start_event(device, 5, continue_music_box_melody, 1)
    
    elif device_type == "automaton":
        # Animate a mechanical figure
        device_room = obj.objGetRoom(device)
        if device_room:
            room.roomSendMessage(device_room, f"A mechanical figure emerges from {device_name} and begins to dance!")
            
            # Schedule dance sequence
            event.start_event(device, 3, continue_automaton_dance, 1)
    
    elif device_type == "puzzle_box":
        # Open hidden compartments
        device_room = obj.objGetRoom(device)
        if device_room:
            room.roomSendMessage(device_room, f"{device_name} clicks and whirs, revealing hidden compartments!")
            
            # Create treasure or items in the compartments
            create_puzzle_box_contents(device)

def continue_music_box_melody(device, sequence_step):
    """Continue the music box melody sequence."""
    
    state = ObjectState(device)
    power_level = state.get_numeric_state("power_level", 0)
    
    if power_level <= 0:
        # Out of power
        device_room = obj.objGetRoom(device)
        if device_room:
            room.roomSendMessage(device_room, "The music box winds down and falls silent.")
        return
    
    # Consume power
    new_power = state.modify_state("power_level", -5, 0, 100)
    
    # Play next part of melody
    device_room = obj.objGetRoom(device)
    if device_room:
        melodies = [
            "The melody rises to a crescendo, filling the air with magic.",
            "Delicate notes dance through the air like silver bells.",
            "The music shifts to a minor key, becoming hauntingly beautiful.",
            "A complex harmony emerges, weaving multiple melodic lines together."
        ]
        
        if sequence_step <= len(melodies):
            room.roomSendMessage(device_room, melodies[sequence_step - 1])
        
        # Continue if there's power and more melody
        if new_power > 0 and sequence_step < 6:
            event.start_event(device, 4, continue_music_box_melody, sequence_step + 1)
        else:
            room.roomSendMessage(device_room, "The beautiful melody comes to an end.")

def apply_gear_alignment_effects(device, alignment):
    """Apply effects based on gear alignment."""
    
    state = ObjectState(device)
    device_room = obj.objGetRoom(device)
    
    if not device_room:
        return
    
    alignment_effects = {
        "neutral": "The gears settle into a balanced configuration.",
        "forward": "The gears align for maximum forward motion.",
        "reverse": "The gears reverse their rotation direction.",
        "precision": "The gears align for precise, delicate movements.",
        "power": "The gears align for maximum power output."
    }
    
    if alignment in alignment_effects:
        room.roomSendMessage(device_room, alignment_effects[alignment])

# Register object network systems
mudsys.add_obj_method("crystal_resonance", crystal_resonance_network)
mudsys.add_obj_method("clockwork_device", mechanical_clockwork_system)
```

## Step 4: Advanced Object Scripting Patterns

Create sophisticated object behavior patterns:

```python
# Add to advanced_object_scripting.py

class ObjectBehaviorTree:
    """Implement behavior trees for complex object AI."""
    
    def __init__(self, obj_ref):
        self.object = obj_ref
        self.state = ObjectState(obj_ref)
    
    def execute_behavior_tree(self, root_behavior):
        """Execute a behavior tree starting from the root."""
        return self.execute_behavior_node(root_behavior)
    
    def execute_behavior_node(self, behavior):
        """Execute a single behavior node."""
        behavior_type = behavior.get("type", "action")
        
        if behavior_type == "sequence":
            # Execute all children in sequence, stop on first failure
            for child in behavior.get("children", []):
                if not self.execute_behavior_node(child):
                    return False
            return True
        
        elif behavior_type == "selector":
            # Execute children until one succeeds
            for child in behavior.get("children", []):
                if self.execute_behavior_node(child):
                    return True
            return False
        
        elif behavior_type == "condition":
            # Check a condition
            return self.check_condition(behavior.get("condition"))
        
        elif behavior_type == "action":
            # Execute an action
            return self.execute_action(behavior.get("action"))
        
        return False
    
    def check_condition(self, condition):
        """Check a behavior condition."""
        if not condition:
            return False
        
        condition_type = condition.get("type")
        
        if condition_type == "state_equals":
            key = condition.get("key")
            value = condition.get("value")
            return self.state.get_state(key) == value
        
        elif condition_type == "state_greater":
            key = condition.get("key")
            value = condition.get("value", 0)
            return self.state.get_numeric_state(key, 0) > value
        
        elif condition_type == "random_chance":
            chance = condition.get("chance", 50)
            return random.randint(1, 100) <= chance
        
        return False
    
    def execute_action(self, action):
        """Execute a behavior action."""
        if not action:
            return False
        
        action_type = action.get("type")
        
        if action_type == "set_state":
            key = action.get("key")
            value = action.get("value")
            self.state.set_state(key, value)
            return True
        
        elif action_type == "modify_state":
            key = action.get("key")
            delta = action.get("delta", 0)
            self.state.modify_state(key, delta)
            return True
        
        elif action_type == "send_message":
            message = action.get("message", "")
            obj_room = obj.objGetRoom(self.object)
            if obj_room and message:
                room.roomSendMessage(obj_room, message)
            return True
        
        return False

def intelligent_artifact_system(artifact, actor, action_type):
    """Intelligent artifact with complex behavior patterns."""
    
    state = ObjectState(artifact)
    artifact_name = obj.objGetName(artifact)
    
    if char.charIsNPC(actor):
        return
    
    actor_name = char.charGetName(actor)
    
    # Initialize artifact intelligence if needed
    if state.get_state("intelligence_initialized") != "true":
        initialize_artifact_intelligence(artifact)
    
    # Create behavior tree
    behavior_tree = ObjectBehaviorTree(artifact)
    
    if action_type == "commune":
        # Communicate with the artifact's intelligence
        communion_behavior = {
            "type": "selector",
            "children": [
                {
                    "type": "sequence",
                    "children": [
                        {
                            "type": "condition",
                            "condition": {"type": "state_greater", "key": "trust_level", "value": 75}
                        },
                        {
                            "type": "action",
                            "action": {"type": "send_message", "message": f"{artifact_name} shares deep wisdom with {actor_name}."}
                        }
                    ]
                },
                {
                    "type": "sequence",
                    "children": [
                        {
                            "type": "condition",
                            "condition": {"type": "state_greater", "key": "trust_level", "value": 25}
                        },
                        {
                            "type": "action",
                            "action": {"type": "send_message", "message": f"{artifact_name} responds cautiously to {actor_name}."}
                        }
                    ]
                },
                {
                    "type": "action",
                    "action": {"type": "send_message", "message": f"{artifact_name} remains silent and unresponsive."}
                }
            ]
        }
        
        behavior_tree.execute_behavior_tree(communion_behavior)
        
        # Increase trust based on successful communion
        trust_increase = random.randint(1, 5)
        state.modify_state("trust_level", trust_increase, 0, 100)
    
    elif action_type == "attune":
        # Attune to the artifact
        attunement_level = state.get_numeric_state("attunement_level", 0)
        
        if attunement_level >= 100:
            char.charSend(actor, f"You are already fully attuned to {artifact_name}.")
            return
        
        # Attunement behavior tree
        attunement_behavior = {
            "type": "sequence",
            "children": [
                {
                    "type": "condition",
                    "condition": {"type": "random_chance", "chance": 70}
                },
                {
                    "type": "action",
                    "action": {"type": "modify_state", "key": "attunement_level", "delta": 10}
                },
                {
                    "type": "action",
                    "action": {"type": "send_message", "message": f"{actor_name} grows more attuned to {artifact_name}."}
                }
            ]
        }
        
        if behavior_tree.execute_behavior_tree(attunement_behavior):
            char.charSend(actor, f"You feel your connection to {artifact_name} strengthen.")
        else:
            char.charSend(actor, f"Your attunement attempt fails. {artifact_name} resists your efforts.")

def initialize_artifact_intelligence(artifact):
    """Initialize an artifact's intelligence system."""
    
    state = ObjectState(artifact)
    
    # Set initial intelligence parameters
    state.set_state("intelligence_initialized", "true")
    state.set_state("trust_level", random.randint(10, 30))
    state.set_state("attunement_level", 0)
    state.set_state("personality_type", random.choice(["wise", "cautious", "proud", "benevolent", "mysterious"]))
    state.set_state("knowledge_level", random.randint(50, 90))
    
    # Log initialization
    artifact_name = obj.objGetName(artifact)
    personality = state.get_state("personality_type")
    mudsys.log_string(f"Artifact {artifact_name} initialized with {personality} personality")

def adaptive_tool_system(tool, actor, action_type):
    """Tool that adapts to user's skill and usage patterns."""
    
    state = ObjectState(tool)
    tool_name = obj.objGetName(tool)
    
    if char.charIsNPC(actor):
        return
    
    actor_name = char.charGetName(actor)
    
    # Track user-specific adaptation
    user_key = f"user_{actor_name.lower()}"
    user_skill = state.get_numeric_state(f"{user_key}_skill", 0)
    user_familiarity = state.get_numeric_state(f"{user_key}_familiarity", 0)
    
    if action_type == "use":
        # Tool adapts based on usage
        skill_increase = random.randint(1, 3)
        familiarity_increase = 1
        
        new_skill = state.modify_state(f"{user_key}_skill", skill_increase, 0, 100)
        new_familiarity = state.modify_state(f"{user_key}_familiarity", familiarity_increase, 0, 200)
        
        # Tool provides feedback based on adaptation level
        if new_familiarity < 10:
            char.charSend(actor, f"{tool_name} feels awkward and unfamiliar in your hands.")
        elif new_familiarity < 30:
            char.charSend(actor, f"{tool_name} is starting to feel more comfortable to use.")
        elif new_familiarity < 60:
            char.charSend(actor, f"{tool_name} feels familiar and responsive to your touch.")
        elif new_familiarity < 100:
            char.charSend(actor, f"{tool_name} seems to anticipate your needs.")
        else:
            char.charSend(actor, f"{tool_name} feels like an extension of your own body.")
        
        # Skill-based success rates
        success_chance = min(95, 30 + new_skill)
        if random.randint(1, 100) <= success_chance:
            char.charSend(actor, f"You use {tool_name} with skill and precision.")
            char.charSendRoom(actor, f"{actor_name} uses {tool_name} expertly.")
        else:
            char.charSend(actor, f"Your use of {tool_name} is clumsy and ineffective.")
            char.charSendRoom(actor, f"{actor_name} struggles with {tool_name}.")

# Register advanced object systems
mudsys.add_obj_method("intelligent_artifact", intelligent_artifact_system)
mudsys.add_obj_method("adaptive_tool", adaptive_tool_system)
```

## Step 5: Performance Optimization

Optimize object systems for better performance:

```python
# Add to advanced_object_scripting.py

class ObjectPerformanceManager:
    """Manage performance for complex object systems."""
    
    @staticmethod
    def should_process_object(obj_ref, base_chance=15):
        """Determine if an object should process complex behaviors."""
        
        # Don't process if object isn't in a room with players
        obj_room = obj.objGetRoom(obj_ref)
        if not obj_room:
            return False
        
        chars_in_room = room.roomGetChars(obj_room)
        players_present = any(not char.charIsNPC(c) for c in chars_in_room)
        
        if not players_present:
            return False
        
        # Use random chance to distribute processing load
        return random.randint(1, 100) <= base_chance
    
    @staticmethod
    def cleanup_object_data(obj_ref, max_age_hours=72):
        """Clean up old object auxiliary data."""
        
        # This would implement cleanup of old interaction data
        current_time = mudsys.current_time()
        
        # In a real implementation, you'd clean up old user data,
        # interaction logs, temporary states, etc.
        pass
    
    @staticmethod
    def batch_process_objects(object_list, process_function):
        """Process multiple objects in batches."""
        
        batch_size = 4  # Process 4 objects per call
        
        for i in range(0, len(object_list), batch_size):
            batch = object_list[i:i + batch_size]
            for obj_ref in batch:
                try:
                    process_function(obj_ref)
                except Exception as e:
                    obj_name = obj.objGetName(obj_ref) if obj_ref else "Unknown"
                    mudsys.log_string(f"Error processing object {obj_name}: {e}")

def optimized_object_heartbeat(obj_ref):
    """Optimized heartbeat for complex objects."""
    
    # Only process complex behaviors occasionally
    if not ObjectPerformanceManager.should_process_object(obj_ref, 20):
        return
    
    try:
        state = ObjectState(obj_ref)
        object_type = state.get_state("item_type", "generic")
        
        # Process based on object type
        if object_type == "magical_weapon":
            # Weapon maintenance and evolution checks
            process_weapon_maintenance(obj_ref)
        
        elif object_type == "alchemical_potion":
            # Potion aging and degradation
            process_potion_aging(obj_ref)
        
        elif object_type == "clockwork_device":
            # Clockwork power consumption
            process_clockwork_power(obj_ref)
        
        # Occasionally clean up old data
        if random.randint(1, 500) == 1:
            ObjectPerformanceManager.cleanup_object_data(obj_ref)
    
    except Exception as e:
        obj_name = obj.objGetName(obj_ref) if obj_ref else "Unknown"
        mudsys.log_string(f"Error in object heartbeat for {obj_name}: {e}")

def process_weapon_maintenance(weapon):
    """Process weapon maintenance and degradation."""
    
    state = ObjectState(weapon)
    
    # Weapons degrade over time without maintenance
    last_maintenance = state.get_numeric_state("last_maintenance", mudsys.current_time())
    current_time = mudsys.current_time()
    
    if current_time - last_maintenance > 86400:  # 24 hours
        condition = state.get_numeric_state("condition", 100)
        if condition > 0:
            new_condition = state.modify_state("condition", -1, 0, 100)
            
            if new_condition <= 25:
                # Weapon is in poor condition
                weapon_room = obj.objGetRoom(weapon)
                if weapon_room and random.randint(1, 20) == 1:
                    weapon_name = obj.objGetName(weapon)
                    room.roomSendMessage(weapon_room, f"{weapon_name} shows signs of wear and neglect.")

def process_potion_aging(potion):
    """Process potion aging effects."""
    
    state = ObjectState(potion)
    
    # Potions age and lose potency over time
    creation_time = state.get_numeric_state("creation_time", mudsys.current_time())
    current_time = mudsys.current_time()
    
    age_days = (current_time - creation_time) // 86400
    state.set_state("age_days", age_days)
    
    # Potency decreases with age
    if age_days > 0 and random.randint(1, 10) == 1:
        potency = state.get_numeric_state("potency", 50)
        if potency > 10:
            state.modify_state("potency", -1, 10, 100)

def process_clockwork_power(device):
    """Process clockwork device power consumption."""
    
    state = ObjectState(device)
    power_level = state.get_numeric_state("power_level", 0)
    
    if power_level > 0:
        # Consume power over time
        power_consumption = 1
        new_power = state.modify_state("power_level", -power_consumption, 0, 100)
        
        if new_power == 0:
            # Device runs out of power
            device_room = obj.objGetRoom(device)
            if device_room:
                device_name = obj.objGetName(device)
                room.roomSendMessage(device_room, f"{device_name} winds down and stops working.")

# Register optimized systems
mudsys.add_obj_method("optimized_heartbeat", optimized_object_heartbeat)
```

## Best Practices for Object Scripting

### 1. Design for Modularity
Create reusable object behavior components:

```python
# Good: Modular design
def base_item_behavior(obj_ref, actor, action):
    # Common item behavior
    pass

def enhanced_item_behavior(obj_ref, actor, action):
    # Call base behavior first
    base_item_behavior(obj_ref, actor, action)
    # Add enhanced features
    pass
```

### 2. Use State Management Consistently
Always use auxiliary data for persistent object state:

```python
def get_object_property(obj_ref, key, default=None):
    state = ObjectState(obj_ref)
    return state.get_state(key, default)

def set_object_property(obj_ref, key, value):
    state = ObjectState(obj_ref)
    state.set_state(key, value)
```

### 3. Handle Edge Cases
Always validate object states and inputs:

```python
def safe_object_interaction(obj_ref, actor, action):
    # Validate inputs
    if not obj_ref or not actor:
        return
    
    # Check object state
    if not obj.objExists(obj_ref):  # Hypothetical function
        return
    
    # Your interaction logic here
```

### 4. Optimize for Performance
Use random chances and batching for expensive operations:

```python
# Only process complex behaviors occasionally
if random.randint(1, 20) == 1:
    # Complex behavior
    pass
```

## Next Steps

Now that you understand advanced object scripting:

1. **Try [Using the Event System](using-event-system/)** for timed object behaviors
2. **Explore integration with room and character systems**
3. **Create complete interactive game mechanics**

## Summary

You've learned to:
- Create sophisticated interactive object behaviors
- Build custom item types with unique properties
- Implement object state management systems
- Create networks of interacting objects
- Use advanced scripting patterns like behavior trees
- Optimize performance for complex object systems

## Troubleshooting

**Objects not responding to interactions?**
- Check that object methods are properly registered
- Verify auxiliary data is being stored correctly
- Look for errors in mud logs

**Performance issues with many objects?**
- Reduce heartbeat frequency for complex operations
- Use random chances to limit processing
- Clean up old auxiliary data regularly

**Object networks not working?**
- Verify all objects are properly configured as part of the network
- Check that network state is being stored consistently
- Test individual object behaviors before connecting them

Ready for the final intermediate tutorial? Continue with [Using the Event System](using-event-system/)!