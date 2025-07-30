---
layout: default
title: Complex Prototype Inheritance
parent: Create Systems
grand_parent: Tutorials
nav_order: 2
permalink: /tutorials/complex-prototype-inheritance/
---

# Complex Prototype Inheritance

*This tutorial is currently being developed and will be available soon.*

## Coming Soon

This tutorial will teach you to create sophisticated prototype hierarchies using NakedMud's inheritance system, including:

- Multi-level inheritance patterns
- Abstract prototype design
- Mixin and composition patterns
- Dynamic prototype modification

## Prerequisites

- Completed [Start with the Basics](../start-with-basics/) tutorials
- Understanding of [Prototypes](/core-concepts/prototypes/) concepts
- Experience with OLC (Online Creation) system
- Familiarity with [Auxiliary Data](/core-concepts/auxiliary-data/)

## What You'll Learn

- Creating abstract parent prototypes
- Building inheritance hierarchies for weapons, NPCs, and rooms
- Using auxiliary data to extend inherited behavior
- Best practices for maintainable prototype design

*Check back soon for the complete tutorial, or see the [Examples section](/examples/inheritance/) for working code examples.*

## What You'll Learn

- How prototype inheritance works in NakedMud
- Creating abstract parent prototypes
- Building inheritance hierarchies for weapons, NPCs, and rooms
- Using auxiliary data to extend inherited behavior
- Best practices for maintainable prototype design

## Understanding Prototype Inheritance

In NakedMud, prototypes can inherit from one or more parent prototypes. When you create an instance, it gets all properties from its parents, with child properties overriding parent properties.

### How Inheritance Works

```
# Prototype hierarchy example:
base_weapon (abstract)
├── melee_weapon (abstract)
│   ├── sword
│   ├── axe
│   └── mace
└── ranged_weapon (abstract)
    ├── bow
    ├── crossbow
    └── throwing_knife
```

When you load a `sword`, it inherits from both `melee_weapon` and `base_weapon`, getting all their properties while adding its own specific features.

## Step 1: Creating Abstract Base Prototypes

Abstract prototypes serve as templates that define common properties but are never loaded directly. Let's create a weapon hierarchy.

### Creating the Base Weapon Prototype

```
# Create the abstract base weapon:
oedit base_weapon

# In the object editor:
# 1) Abstract: yes (toggle to yes)
# 2) Inherits from prototypes: (leave empty - this is the root)
# 3) Name: a weapon
# 4) Keywords: weapon
# 5) Short description: a weapon
# 6) Long description: This is a basic weapon template.
# 7) Room description: A weapon lies here.
# 8) Item type: weapon
# 9) Weight: 1
# 10) Value: 10
```

### Adding Base Weapon Properties

In the **C) Extra code** section, add initialization code:

```python
# Base weapon initialization
import auxiliary

# Set up basic weapon data
weapon_data = {
    "weapon_type": "generic",
    "damage_dice": "1d4",
    "damage_bonus": 0,
    "accuracy_bonus": 0,
    "durability": 100,
    "max_durability": 100,
    "special_properties": []
}

auxiliary.objSetAuxiliaryData(me, "weapon_stats", str(weapon_data))
```

### Understanding Abstract Prototypes

- **Abstract: yes** - Cannot be loaded directly
- **Serves as template** - Provides common properties to children
- **Defines structure** - Establishes what all weapons should have
- **Reduces duplication** - Common code written once

## Step 2: Creating Specialized Parent Prototypes

Now create more specific weapon categories that inherit from the base.

### Creating Melee Weapon Template

```
# Create melee weapon template:
oedit melee_weapon

# Set properties:
# 1) Abstract: yes
# 2) Inherits from prototypes: base_weapon
# 3) Name: a melee weapon
# 4) Keywords: weapon melee
# 5) Short description: a melee weapon
# 6) Long description: This weapon is designed for close combat.
# 8) Item type: weapon (inherited from base_weapon)
# 9) Weight: 3 (overrides base_weapon)
```

### Adding Melee-Specific Code

In **C) Extra code**:

```python
# Melee weapon specialization
import auxiliary

# Get base weapon data (inherited from parent)
weapon_data_str = auxiliary.objGetAuxiliaryData(me, "weapon_stats")

if weapon_data_str:
    # Parse the inherited data
    import ast
    weapon_data = ast.literal_eval(weapon_data_str)
    
    # Modify for melee weapons
    weapon_data["weapon_type"] = "melee"
    weapon_data["damage_dice"] = "1d6"
    weapon_data["range"] = "touch"
    weapon_data["special_properties"].append("melee_combat")
    
    # Save the modified data
    auxiliary.objSetAuxiliaryData(me, "weapon_stats", str(weapon_data))
```

### Creating Ranged Weapon Template

```
# Create ranged weapon template:
oedit ranged_weapon

# Set properties:
# 1) Abstract: yes
# 2) Inherits from prototypes: base_weapon
# 3) Name: a ranged weapon
# 4) Keywords: weapon ranged
# 5) Short description: a ranged weapon
# 6) Long description: This weapon can strike from a distance.
# 9) Weight: 2 (lighter than melee weapons)
```

In **C) Extra code**:

```python
# Ranged weapon specialization
import auxiliary

weapon_data_str = auxiliary.objGetAuxiliaryData(me, "weapon_stats")

if weapon_data_str:
    import ast
    weapon_data = ast.literal_eval(weapon_data_str)
    
    # Modify for ranged weapons
    weapon_data["weapon_type"] = "ranged"
    weapon_data["damage_dice"] = "1d4"
    weapon_data["range"] = "far"
    weapon_data["ammunition_type"] = "none"
    weapon_data["special_properties"].append("ranged_combat")
    
    auxiliary.objSetAuxiliaryData(me, "weapon_stats", str(weapon_data))
```

## Step 3: Creating Concrete Weapon Prototypes

Now create actual weapons that players can use.

### Creating a Sword

```
# Create a specific sword:
oedit iron_sword

# Set properties:
# 1) Abstract: no (can be loaded)
# 2) Inherits from prototypes: melee_weapon
# 3) Name: an iron sword
# 4) Keywords: sword iron weapon
# 5) Short description: an iron sword
# 6) Long description: This well-crafted iron sword has a sharp blade and sturdy grip.
# 7) Room description: An iron sword lies here, gleaming in the light.
# 9) Weight: 4
# 10) Value: 50
```

In **C) Extra code**:

```python
# Iron sword specialization
import auxiliary

weapon_data_str = auxiliary.objGetAuxiliaryData(me, "weapon_stats")

if weapon_data_str:
    import ast
    weapon_data = ast.literal_eval(weapon_data_str)
    
    # Customize for iron sword
    weapon_data["damage_dice"] = "1d8"
    weapon_data["damage_bonus"] = 1
    weapon_data["accuracy_bonus"] = 1
    weapon_data["material"] = "iron"
    weapon_data["special_properties"].append("slashing")
    
    auxiliary.objSetAuxiliaryData(me, "weapon_stats", str(weapon_data))
```

### Creating a Bow

```
# Create a hunting bow:
oedit hunting_bow

# Set properties:
# 1) Abstract: no
# 2) Inherits from prototypes: ranged_weapon
# 3) Name: a hunting bow
# 4) Keywords: bow hunting weapon
# 5) Short description: a hunting bow
# 6) Long description: This sturdy wooden bow is perfect for hunting game.
# 9) Weight: 2
# 10) Value: 30
```

In **C) Extra code**:

```python
# Hunting bow specialization
import auxiliary

weapon_data_str = auxiliary.objGetAuxiliaryData(me, "weapon_stats")

if weapon_data_str:
    import ast
    weapon_data = ast.literal_eval(weapon_data_str)
    
    # Customize for hunting bow
    weapon_data["damage_dice"] = "1d6"
    weapon_data["range"] = "long"
    weapon_data["ammunition_type"] = "arrow"
    weapon_data["special_properties"].extend(["piercing", "two_handed"])
    
    auxiliary.objSetAuxiliaryData(me, "weapon_stats", str(weapon_data))
```

## Step 4: Adding Magical Weapon Variants

Create magical versions using multiple inheritance.

### Creating Magical Weapon Template

```
# Create magical weapon template:
oedit magical_weapon

# Set properties:
# 1) Abstract: yes
# 2) Inherits from prototypes: (leave empty - this is a mixin)
# 3) Name: a magical weapon
# 4) Keywords: weapon magical magic
# 5) Short description: a magical weapon
# 6) Long description: This weapon radiates magical energy.
```

In **C) Extra code**:

```python
# Magical weapon mixin
import auxiliary

# Add magical properties
magical_data = {
    "is_magical": True,
    "magic_bonus": 1,
    "magical_properties": [],
    "charges": 0,
    "max_charges": 0
}

auxiliary.objSetAuxiliaryData(me, "magical_stats", str(magical_data))

# Enhance existing weapon stats if they exist
weapon_data_str = auxiliary.objGetAuxiliaryData(me, "weapon_stats")
if weapon_data_str:
    import ast
    weapon_data = ast.literal_eval(weapon_data_str)
    
    # Add magical enhancement
    weapon_data["damage_bonus"] += 1
    weapon_data["accuracy_bonus"] += 1
    weapon_data["special_properties"].append("magical")
    
    auxiliary.objSetAuxiliaryData(me, "weapon_stats", str(weapon_data))
```

### Creating a Flaming Sword

```
# Create flaming sword using multiple inheritance:
oedit flaming_sword

# Set properties:
# 1) Abstract: no
# 2) Inherits from prototypes: melee_weapon, magical_weapon
# 3) Name: a flaming sword
# 4) Keywords: sword flaming fire magical weapon
# 5) Short description: a flaming sword
# 6) Long description: This magical sword burns with eternal flames that never consume the blade.
# 10) Value: 200
```

In **C) Extra code**:

```python
# Flaming sword customization
import auxiliary

# Customize magical properties
magical_data_str = auxiliary.objGetAuxiliaryData(me, "magical_stats")
if magical_data_str:
    import ast
    magical_data = ast.literal_eval(magical_data_str)
    
    magical_data["magical_properties"].append("flaming")
    magical_data["magic_bonus"] = 2
    
    auxiliary.objSetAuxiliaryData(me, "magical_stats", str(magical_data))

# Enhance weapon stats
weapon_data_str = auxiliary.objGetAuxiliaryData(me, "weapon_stats")
if weapon_data_str:
    import ast
    weapon_data = ast.literal_eval(weapon_data_str)
    
    weapon_data["damage_dice"] = "1d8+1d4"  # Extra fire damage
    weapon_data["damage_bonus"] = 2
    weapon_data["special_properties"].extend(["fire_damage", "light_source"])
    
    auxiliary.objSetAuxiliaryData(me, "weapon_stats", str(weapon_data))
```

## Step 5: NPC Inheritance Hierarchies

Apply the same principles to create NPC hierarchies.

### Creating Base Humanoid

```
# Create base humanoid template:
medit base_humanoid

# Set properties:
# 1) Abstract: yes
# 2) Inherits from prototypes: (empty)
# 3) Name: a humanoid
# 4) Keywords: humanoid
# 6) Room description: A humanoid stands here.
# 8) Description: This is a basic humanoid template.
# R) Change race: human
# G) Change Gender: neuter
```

In **C) Extra code**:

```python
# Base humanoid setup
import auxiliary

humanoid_data = {
    "creature_type": "humanoid",
    "intelligence_level": "average",
    "social_behavior": "neutral",
    "combat_training": "basic",
    "special_abilities": []
}

auxiliary.charSetAuxiliaryData(me, "creature_stats", str(humanoid_data))
```

### Creating Guard Template

```
# Create guard template:
medit base_guard

# Set properties:
# 1) Abstract: yes
# 2) Inherits from prototypes: base_humanoid
# 3) Name: a guard
# 4) Keywords: guard humanoid
# 6) Room description: A guard stands at attention here.
# 8) Description: This guard is trained to protect and serve.
```

In **C) Extra code**:

```python
# Guard specialization
import auxiliary

creature_data_str = auxiliary.charGetAuxiliaryData(me, "creature_stats")
if creature_data_str:
    import ast
    creature_data = ast.literal_eval(creature_data_str)
    
    # Modify for guards
    creature_data["creature_type"] = "guard"
    creature_data["combat_training"] = "professional"
    creature_data["social_behavior"] = "lawful"
    creature_data["special_abilities"].extend(["patrol", "alert", "arrest"])
    
    auxiliary.charSetAuxiliaryData(me, "creature_stats", str(creature_data))

# Add guard-specific behavior
guard_data = {
    "patrol_route": [],
    "alert_level": "normal",
    "jurisdiction": "city",
    "arrest_authority": True
}

auxiliary.charSetAuxiliaryData(me, "guard_behavior", str(guard_data))
```

### Creating City Guard

```
# Create specific city guard:
medit city_guard

# Set properties:
# 1) Abstract: no
# 2) Inherits from prototypes: base_guard
# 3) Name: a city guard
# 4) Keywords: guard city humanoid
# 6) Room description: A city guard patrols here, watching for trouble.
# 8) Description: This guard wears the uniform of the city watch.
```

In **C) Extra code**:

```python
# City guard customization
import auxiliary

# Customize guard behavior
guard_data_str = auxiliary.charGetAuxiliaryData(me, "guard_behavior")
if guard_data_str:
    import ast
    guard_data = ast.literal_eval(guard_data_str)
    
    guard_data["jurisdiction"] = "city_limits"
    guard_data["patrol_route"] = ["main_street", "market_square", "city_gate"]
    
    auxiliary.charSetAuxiliaryData(me, "guard_behavior", str(guard_data))
```

## Step 6: Room Inheritance for Environmental Systems

Create room hierarchies for consistent environmental behavior.

### Creating Base Indoor Room

```
# Create base indoor template:
redit base_indoor

# Set properties:
# 1) Abstract: yes
# 2) Inherits from prototypes: (empty)
# 3) Name: An Indoor Room
# 4) Description: This is a basic indoor space.
# L) Land type: inside
```

In **C) Extra code**:

```python
# Base indoor room setup
import auxiliary

room_data = {
    "environment_type": "indoor",
    "lighting": "artificial",
    "temperature_control": "moderate",
    "weather_protection": True,
    "acoustic_properties": "normal"
}

auxiliary.roomSetAuxiliaryData(me, "environment_stats", str(room_data))
```

### Creating Tavern Template

```
# Create tavern template:
redit base_tavern

# Set properties:
# 1) Abstract: yes
# 2) Inherits from prototypes: base_indoor
# 3) Name: A Tavern
# 4) Description: This cozy tavern welcomes weary travelers.
```

In **C) Extra code**:

```python
# Tavern specialization
import auxiliary

# Enhance environment for taverns
room_data_str = auxiliary.roomGetAuxiliaryData(me, "environment_stats")
if room_data_str:
    import ast
    room_data = ast.literal_eval(room_data_str)
    
    room_data["environment_type"] = "tavern"
    room_data["lighting"] = "warm_candlelight"
    room_data["acoustic_properties"] = "lively"
    
    auxiliary.roomSetAuxiliaryData(me, "environment_stats", str(room_data))

# Add tavern-specific features
tavern_data = {
    "serves_food": True,
    "serves_drinks": True,
    "has_entertainment": True,
    "atmosphere": "friendly",
    "noise_level": "moderate"
}

auxiliary.roomSetAuxiliaryData(me, "tavern_features", str(tavern_data))
```

## Step 7: Using Auxiliary Data with Inheritance

Auxiliary data works seamlessly with inheritance, allowing you to extend inherited behavior.

### Creating Behavior Extensions

```python
# File: lib/pymodules/weapon_behaviors.py

import auxiliary
import char
import obj

def get_weapon_stats(weapon):
    """Get weapon statistics from auxiliary data."""
    
    weapon_data_str = auxiliary.objGetAuxiliaryData(weapon, "weapon_stats")
    if not weapon_data_str:
        return None
    
    try:
        import ast
        return ast.literal_eval(weapon_data_str)
    except:
        return None

def get_magical_stats(weapon):
    """Get magical weapon statistics."""
    
    magical_data_str = auxiliary.objGetAuxiliaryData(weapon, "magical_stats")
    if not magical_data_str:
        return None
    
    try:
        import ast
        return ast.literal_eval(magical_data_str)
    except:
        return None

def calculate_weapon_damage(weapon, wielder):
    """Calculate total weapon damage including all bonuses."""
    
    weapon_stats = get_weapon_stats(weapon)
    if not weapon_stats:
        return "1d4"  # Default damage
    
    base_damage = weapon_stats.get("damage_dice", "1d4")
    damage_bonus = weapon_stats.get("damage_bonus", 0)
    
    # Add magical bonuses if present
    magical_stats = get_magical_stats(weapon)
    if magical_stats:
        damage_bonus += magical_stats.get("magic_bonus", 0)
    
    # Add wielder bonuses (strength, skills, etc.)
    if wielder:
        strength_bonus = (char.charGetStr(wielder) - 10) // 2
        damage_bonus += strength_bonus
    
    if damage_bonus > 0:
        return f"{base_damage}+{damage_bonus}"
    elif damage_bonus < 0:
        return f"{base_damage}{damage_bonus}"
    else:
        return base_damage

def weapon_special_attack(weapon, wielder, target):
    """Handle special weapon attacks based on properties."""
    
    weapon_stats = get_weapon_stats(weapon)
    if not weapon_stats:
        return False
    
    special_properties = weapon_stats.get("special_properties", [])
    
    if "flaming" in special_properties:
        char.charSend(target, "The flaming weapon sears your flesh!")
        char.charSendRoom(target, f"{char.charGetName(target)} is burned by the flaming weapon!")
        # Apply fire damage
        return True
    
    if "frost" in special_properties:
        char.charSend(target, "The icy weapon chills you to the bone!")
        # Apply cold damage and slow effect
        return True
    
    return False
```

## Step 8: Testing Your Inheritance Hierarchy

Test that inheritance is working correctly.

### Loading and Testing Objects

```
# Test the inheritance chain:
load object iron_sword

# Check that it has all inherited properties:
oview iron_sword

# Test magical weapon:
load object flaming_sword

# Verify it has both weapon and magical properties
```

### Verifying Auxiliary Data

```python
# Create a test trigger to examine auxiliary data:
tedit test_weapon_stats

# In the trigger code:
import auxiliary
import ast

weapon_data_str = auxiliary.objGetAuxiliaryData(me, "weapon_stats")
if weapon_data_str:
    weapon_data = ast.literal_eval(weapon_data_str)
    char.charSend(actor, f"Weapon type: {weapon_data.get('weapon_type', 'unknown')}")
    char.charSend(actor, f"Damage: {weapon_data.get('damage_dice', '1d4')}")
    char.charSend(actor, f"Properties: {weapon_data.get('special_properties', [])}")

magical_data_str = auxiliary.objGetAuxiliaryData(me, "magical_stats")
if magical_data_str:
    magical_data = ast.literal_eval(magical_data_str)
    char.charSend(actor, f"Magic bonus: {magical_data.get('magic_bonus', 0)}")
    char.charSend(actor, f"Magical properties: {magical_data.get('magical_properties', [])}")
```

## Best Practices for Prototype Inheritance

### 1. Design Your Hierarchy First

Plan your inheritance structure before creating prototypes:

```
# Good hierarchy design:
base_creature (abstract)
├── humanoid (abstract)
│   ├── guard (abstract)
│   │   ├── city_guard
│   │   └── palace_guard
│   └── merchant (abstract)
│       ├── shopkeeper
│       └── trader
└── monster (abstract)
    ├── undead (abstract)
    └── beast (abstract)
```

### 2. Use Abstract Prototypes for Common Properties

- Make parent prototypes abstract when they shouldn't be loaded directly
- Put common properties in abstract parents
- Let children override specific properties

### 3. Keep Auxiliary Data Simple

```python
# Good: Simple data structures
weapon_data = {
    "damage": "1d8",
    "type": "sword",
    "material": "iron"
}

# Avoid: Overly complex nested structures
weapon_data = {
    "combat": {
        "damage": {
            "base": "1d8",
            "modifiers": {
                "strength": True,
                "magic": 0
            }
        }
    }
}
```

### 4. Document Your Inheritance Chains

```python
# Document inheritance in comments:
# iron_sword inherits from:
#   melee_weapon (damage, range, combat type)
#     base_weapon (durability, value, basic stats)
```

### 5. Test Inheritance Thoroughly

- Load instances and verify all properties are inherited
- Test that child properties override parent properties correctly
- Ensure auxiliary data is properly initialized at each level

## Common Patterns

### Mixin Pattern

Use multiple inheritance to add specific capabilities:

```
# Create capability mixins:
oedit fire_enchantment (abstract: yes)
oedit ice_enchantment (abstract: yes)
oedit poison_coating (abstract: yes)

# Combine with base weapons:
oedit flaming_ice_sword
# Inherits from: melee_weapon, fire_enchantment, ice_enchantment
```

### Template Method Pattern

Define behavior in parent, customize in children:

```python
# In base_weapon extra code:
def weapon_attack(self, wielder, target):
    # Base attack logic
    damage = self.calculate_damage()
    self.apply_damage(target, damage)
    self.handle_special_effects(wielder, target)  # Override in children

def handle_special_effects(self, wielder, target):
    # Default: no special effects
    pass

# In flaming_sword extra code:
def handle_special_effects(self, wielder, target):
    # Override: add fire damage
    self.apply_fire_damage(target)
```

## Next Steps

Now that you understand complex prototype inheritance:

1. **Create your own inheritance hierarchies** for weapons, NPCs, or rooms
2. **Learn [Advanced Auxiliary Data Patterns](../advanced-auxiliary-data-patterns/)** for sophisticated data management
3. **Study [Debugging and Troubleshooting](../debugging-troubleshooting/)** to debug inheritance issues
4. **Move large code examples to the Examples section** for reference

## Summary

You've learned to:
- Create abstract prototype templates
- Build inheritance hierarchies for weapons, NPCs, and rooms
- Use auxiliary data to extend inherited behavior
- Apply multiple inheritance for mixin capabilities
- Follow best practices for maintainable prototype design

Complex prototype inheritance enables you to create rich, varied game content while maintaining clean, reusable code structures.