---
title: Prototype System
layout: default
nav_order: 2
parent: Core Concepts
description: "Understanding NakedMud's template-based object creation and inheritance"
---

# Prototype System

NakedMud's prototype system provides a powerful template-based approach to creating game content. Instead of manually defining every character, room, and object from scratch, you create reusable prototypes that can be instantiated and inherited from. This system supports single and multiple inheritance, abstract prototypes, and dynamic scripting.

## Overview

The prototype system allows you to:

- **Create templates** for characters (mobs), rooms, and objects
- **Use inheritance** to share common properties between related content
- **Define abstract prototypes** that serve as base classes but cannot be instantiated
- **Script behavior** using Python code that runs when prototypes are instantiated
- **Support multiple inheritance** where content can inherit from multiple parents

## The Philosophy Behind Prototypes

Traditional MUD development often involves creating each piece of content from scratch or copying and modifying existing content. This leads to several problems:

1. **Duplication**: Similar content is recreated multiple times
2. **Inconsistency**: Small variations in similar content create maintenance nightmares
3. **Inflexibility**: Changes to common patterns require updating many individual pieces
4. **Complexity**: Managing large amounts of content becomes unwieldy

NakedMud's prototype system addresses these issues by treating content creation like object-oriented programming, where you define classes (prototypes) and create instances from them.

## Understanding Prototype Execution

When you instantiate a prototype, a sophisticated execution process occurs:

### 1. Dependency Resolution
The system first identifies all parent prototypes and builds an execution order:

```
Child Prototype: castle_guard@castle
├── Parents: guard@templates, human@templates
│   ├── guard@templates parents: npc@templates
│   └── human@templates parents: creature@templates
└── Execution order: creature@templates → npc@templates → human@templates → guard@templates → castle_guard@castle
```

### 2. Script Environment Setup
For each prototype in the execution chain:

```python
# A restricted Python environment is created
dict = restricted_script_dict()

# The object being created is added as 'me'
dict['me'] = PyChar(new_character)  # or PyRoom, PyObj

# The script runs in this controlled environment
```

### 3. Inheritance Chain Execution
Scripts execute in dependency order, allowing children to override parent properties:

```python
# creature@templates runs first
me.max_hp = 100
me.race = "unknown"

# npc@templates runs next
me.level = 1
me.add_trigger("death", "npc_death@triggers")

# human@templates runs next
me.race = "human"  # Overrides creature@templates

# guard@templates runs next
me.level = 10      # Overrides npc@templates
me.max_hp = 150    # Overrides creature@templates

# castle_guard@castle runs last
me.name = "a castle guard"
me.keywords = "guard castle"
# Inherits: race=human, level=10, max_hp=150, death trigger
```

### 4. Property Resolution
The final object has properties from the entire inheritance chain, with later prototypes overriding earlier ones.

## Abstract vs Concrete Prototypes

Understanding the distinction between abstract and concrete prototypes is crucial:

### Abstract Prototypes
Abstract prototypes are templates that cannot be instantiated directly. They exist solely to provide common functionality to their children:

```python
# generic_npc@templates (abstract)
me.add_trigger("death", "handle_death@triggers")
me.setvar("respawn_time", 300)

# This prototype defines common NPC behavior but cannot be instantiated
# load_mob("generic_npc@templates")  # This would fail!
```

**Why use abstract prototypes?**
- **Shared Functionality**: Define common behavior once
- **Consistency**: Ensure all children have required properties
- **Maintainability**: Change behavior in one place affects all children
- **Organization**: Create logical hierarchies of functionality

### Concrete Prototypes
Concrete prototypes can be instantiated and represent actual game content:

```python
# town_guard@npcs (concrete, inherits from generic_npc@templates)
me.name = "a town guard"
me.desc = "A vigilant guard watches over the town."

# This can be instantiated
guard = load_mob("town_guard@npcs")  # This works!
```

## The Power of Multiple Inheritance

Multiple inheritance allows prototypes to combine functionality from multiple sources:

### Mixin Pattern
```python
# flying@traits (abstract mixin)
me.add_trigger("move", "flying_move@triggers")
me.setvar("can_fly", True)

# magical@traits (abstract mixin)
me.add_trigger("cast", "magical_cast@triggers")
me.setvar("mana_pool", 100)

# flying_wizard@npcs (concrete, inherits from both)
# Parents: wizard@templates, flying@traits, magical@traits
me.name = "a flying wizard"
# Gets: wizard properties + flying ability + magical ability
```

### Composition Over Inheritance
Multiple inheritance enables composition-like patterns:

```python
# Instead of creating many specialized classes:
# - FlyingGuard, MagicalGuard, FlyingMagicalGuard, etc.

# Create composable traits:
# guard@templates + flying@traits = flying guard
# guard@templates + magical@traits = magical guard  
# guard@templates + flying@traits + magical@traits = flying magical guard
```

## Prototype Scripting Environment

Each prototype script runs in a carefully controlled environment:

### Available Objects
- **me**: The object being created (PyChar, PyRoom, or PyObj)
- **Standard modules**: mud, char, room, obj, event, storage, etc.
- **Utility functions**: load_obj, load_mob, random, etc.

### Security Restrictions
- **No file system access**: Cannot read/write files
- **No network access**: Cannot make external connections
- **No dangerous functions**: eval, exec, import restrictions
- **Resource limits**: Script execution time and memory limits

### Best Practices for Prototype Scripts
1. **Keep scripts focused**: Each prototype should have a single, clear purpose
2. **Use descriptive names**: Make prototype purposes obvious
3. **Document complex logic**: Add comments explaining non-obvious behavior
4. **Handle errors gracefully**: Use try/except for operations that might fail
5. **Avoid side effects**: Don't modify global state or other objects

## Core Concepts

### Prototype Types

NakedMud supports three main prototype types:

- **mproto** - Mobile/character prototypes (NPCs and character templates)
- **rproto** - Room prototypes (locations and areas)
- **oproto** - Object prototypes (items, equipment, containers)

### Key Properties

Every prototype has these essential properties:

- **Key** - Unique identifier (e.g., `"guard@castle"`, `"sword@weapons"`)
- **Parents** - List of prototypes to inherit from
- **Abstract** - Whether this prototype can be instantiated directly
- **Script** - Python code that defines the prototype's properties and behavior

### Inheritance Chain

When a prototype is instantiated:

1. **Parent prototypes run first** (in order specified)
2. **Inheritance is hierarchical** - parents' parents also run
3. **Current prototype runs last** - can override parent properties
4. **Multiple inheritance supported** - can inherit from multiple parents

## Creating Prototypes

### Basic Prototype Structure

```python
# Example room prototype script
me.name = "A Dark Forest"
me.desc = "Tall trees block out most of the sunlight here."
me.keywords = "forest dark trees"

# Set room properties
me.terrain = "forest"
me.light_level = 2

# Add extra descriptions
me.add_extra_desc("trees", "The ancient oaks tower overhead.")
me.add_extra_desc("ground", "The forest floor is covered in fallen leaves.")
```

### Character Prototype Example

```python
# Example mobile prototype - forest guard
me.name = "a forest guard"
me.keywords = "guard forest ranger"
me.desc = "A sturdy ranger keeps watch over the forest paths."

# Set character stats
me.race = "human"
me.sex = "male"
me.level = 15

# Set attributes
me.max_hp = 200
me.hp = me.max_hp
me.max_mana = 100
me.mana = me.max_mana

# Equipment and inventory
load_obj("leather_armor@equipment").to_char(me)
load_obj("iron_sword@weapons").to_char(me)

# Behavior scripts
me.add_trigger("greet", "greet_visitors@triggers")
me.add_trigger("death", "guard_death@triggers")
```

### Object Prototype Example

```python
# Example object prototype - magic sword
me.name = "a gleaming silver sword"
me.keywords = "sword silver gleaming magic"
me.desc = "This finely crafted sword gleams with magical energy."

# Object properties
me.item_type = "weapon"
me.weight = 5
me.value = 500

# Weapon properties
me.weapon_type = "sword"
me.damage_dice = "2d6+3"
me.weapon_flags = ["magic", "silver"]

# Special properties
me.setvar("enchantment_level", 2)
me.add_trigger("wield", "sword_wield@triggers")
```

## Inheritance Examples

### Single Inheritance

```python
# Parent prototype: generic_guard@templates
me.name = "a guard"
me.race = "human"
me.level = 10
me.max_hp = 150
me.add_trigger("greet", "generic_greet@triggers")

# Child prototype: castle_guard@castle (inherits from generic_guard@templates)
# Parents: generic_guard@templates
me.name = "a castle guard"  # Override parent name
me.keywords = "guard castle royal"
me.desc = "A well-armed guard protects the castle."
# Inherits: race, level, max_hp, greet trigger from parent
```

### Multiple Inheritance

```python
# Parent 1: warrior@templates
me.max_hp = 200
me.combat_skill = 80
me.add_trigger("combat", "warrior_combat@triggers")

# Parent 2: spellcaster@templates  
me.max_mana = 150
me.magic_skill = 70
me.add_trigger("cast", "spellcaster_cast@triggers")

# Child: battlemage@npcs (inherits from both)
# Parents: warrior@templates, spellcaster@templates
me.name = "a battlemage"
me.desc = "A warrior-mage skilled in both sword and spell."
# Inherits: hp from warrior, mana from spellcaster, both trigger sets
```

### Abstract Prototypes

```python
# Abstract prototype: generic_room@templates
# Abstract: yes (cannot be instantiated directly)
me.add_trigger("death", "handle_death@triggers")
me.setvar("graveyard", "graveyard@world")

# All rooms inheriting from this get the death trigger
# But this prototype itself cannot be instantiated

# Concrete child: forest_clearing@forest
# Parents: generic_room@templates
# Abstract: no (can be instantiated)
me.name = "A Forest Clearing"
me.desc = "Sunlight filters through the canopy above."
# Inherits the death trigger from generic_room@templates
```

## Advanced Features

### Hierarchical Inheritance

```python
# Inheritance chain: base -> intermediate -> specific

# Base: generic_npc@templates (abstract)
me.race = "human"
me.add_trigger("death", "npc_death@triggers")

# Intermediate: guard@templates (abstract, inherits from generic_npc)
# Parents: generic_npc@templates
me.level = 10
me.max_hp = 150
me.add_trigger("greet", "guard_greet@triggers")

# Specific: gate_guard@castle (concrete, inherits from guard)
# Parents: guard@templates
me.name = "a gate guard"
me.desc = "A vigilant guard watches the castle gate."
# Inherits: race, death trigger (from generic_npc)
#          level, hp, greet trigger (from guard)
```

### Dynamic Property Setting

```python
# Use variables and conditions in prototypes
import random

# Randomize guard equipment
weapons = ["sword@weapons", "spear@weapons", "axe@weapons"]
chosen_weapon = random.choice(weapons)
load_obj(chosen_weapon).to_char(me)

# Conditional behavior based on time
import mud
if mud.get_time_hour() < 6 or mud.get_time_hour() > 20:
    me.add_trigger("patrol", "night_patrol@triggers")
else:
    me.add_trigger("patrol", "day_patrol@triggers")
```

### Cross-Reference Between Prototypes

```python
# Room prototype that references other prototypes
me.name = "The Armory"
me.desc = "Weapons and armor line the walls of this chamber."

# Load specific objects
load_obj("iron_sword@weapons").to_room(me)
load_obj("leather_armor@armor").to_room(me)
load_obj("shield@armor").to_room(me)

# Spawn a guard
load_mob("armory_guard@castle").to_room(me)
```

## Working with Prototypes

### Instantiation

```python
# Create instances from prototypes
guard = load_mob("castle_guard@castle")
sword = load_obj("magic_sword@weapons") 
room = load_room("forest_clearing@forest")

# Instance rooms with custom keys
custom_room = mudroom.instance("forest_clearing@forest", "clearing_01@myzone")
```

### Checking Inheritance

```python
# Check if an object inherits from a prototype
if obj.isinstance("weapon@templates"):
    print("This is a weapon")

if ch.isinstance("guard@templates"):
    print("This character is some kind of guard")

# Find objects by prototype
weapons = find_all_objs(ch, ch.inv, None, "weapon@templates")
guards = find_all_chars(ch, ch.room.chars, None, "guard@templates")
```

### Prototype Information

```python
# Get prototype information
print(f"Room prototype: {room.proto}")
print(f"Character class: {ch.char_class}")
print(f"Object prototypes: {obj.prototypes}")

# Check if prototype exists
if mudsys.proto_exists("mproto", "new_guard@castle"):
    guard = load_mob("new_guard@castle")
```

## Best Practices

### Organization

- **Use zones for organization**: `guard@castle`, `sword@weapons`, `forest@wilderness`
- **Create abstract base classes**: `generic_npc@templates`, `weapon@templates`
- **Group related prototypes**: Keep all castle content in `@castle` zone

### Inheritance Design

- **Start with abstract bases**: Define common properties in abstract prototypes
- **Use single inheritance when possible**: Easier to understand and debug
- **Multiple inheritance for mixins**: Combine specific behaviors (e.g., `flying@traits`)
- **Keep inheritance chains shallow**: Avoid deep hierarchies that are hard to follow

### Naming Conventions

```python
# Good naming patterns
"generic_room@templates"     # Abstract base class
"forest_room@templates"      # Specific abstract type
"dark_forest@wilderness"     # Concrete instance
"guard@templates"            # Abstract NPC type
"castle_guard@castle"        # Specific NPC instance
```

### Script Organization

```python
# Keep scripts focused and modular
# Good: Specific, focused behavior
me.name = "a merchant"
me.add_trigger("greet", "merchant_greet@triggers")
me.add_trigger("buy", "merchant_buy@triggers")

# Avoid: Overly complex scripts in prototypes
# Move complex logic to separate trigger files
```

## Common Patterns

### Template Hierarchies

```python
# Common inheritance pattern
generic_npc@templates (abstract)
├── civilian@templates (abstract)
│   ├── merchant@templates (abstract)
│   │   └── weapon_merchant@shops
│   └── citizen@templates (abstract)
│       └── town_citizen@town
└── combatant@templates (abstract)
    ├── guard@templates (abstract)
    │   └── castle_guard@castle
    └── monster@templates (abstract)
        └── forest_wolf@wilderness
```

### Room Template System

```python
# Room inheritance for consistent areas
generic_room@templates (abstract)
├── indoor_room@templates (abstract)
│   ├── castle_room@templates (abstract)
│   │   ├── throne_room@castle
│   │   └── guard_room@castle
│   └── shop_room@templates (abstract)
│       └── weapon_shop@shops
└── outdoor_room@templates (abstract)
    ├── forest_room@templates (abstract)
    │   └── dark_forest@wilderness
    └── road_room@templates (abstract)
        └── main_road@roads
```

### Equipment Sets

```python
# Weapon inheritance for consistent properties
weapon@templates (abstract)
├── melee_weapon@templates (abstract)
│   ├── sword@templates (abstract)
│   │   ├── iron_sword@weapons
│   │   └── magic_sword@weapons
│   └── axe@templates (abstract)
│       └── battle_axe@weapons
└── ranged_weapon@templates (abstract)
    └── bow@templates (abstract)
        └── longbow@weapons
```

## Troubleshooting

### Common Issues

**Prototype not found**: Check the key format and ensure the zone exists.
```python
# Wrong: "guard" (missing zone)
# Right: "guard@castle"
```

**Inheritance loops**: Avoid circular inheritance.
```python
# Wrong: A inherits from B, B inherits from A
# Right: Use proper hierarchy with abstract bases
```

**Abstract instantiation**: Cannot directly instantiate abstract prototypes.
```python
# Wrong: load_mob("generic_guard@templates")  # if abstract
# Right: load_mob("castle_guard@castle")      # concrete child
```

**Script errors**: Check Python syntax and available functions.
```python
# Use try/except for error handling in prototype scripts
try:
    load_obj("rare_item@special").to_char(me)
except:
    # Fallback if rare item doesn't exist
    load_obj("common_item@basic").to_char(me)
```

### Debugging Tips

```python
# Add debug output to prototype scripts
print(f"Loading prototype: {me.proto}")
print(f"Parents: {me.parents}")

# Check inheritance chain
def debug_inheritance(obj):
    print(f"Object: {obj.name}")
    print(f"Prototype: {obj.proto}")
    print(f"Inherits from: {obj.prototypes}")
```

## See Also

- [Auxiliary Data System](auxiliary-data.md) - For extending prototypes with custom data
- [Python Integration](python-integration.md) - Understanding the scripting environment
- [OLC System](../tutorials/olc-guide.md) - Online creation and editing of prototypes
- [Scripting Guide](../tutorials/scripting-basics.md) - Writing effective prototype scripts