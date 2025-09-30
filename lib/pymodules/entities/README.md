# NakedMud Entities Configuration Module

A comprehensive entity configuration system for NakedMud that provides centralized management of races, body types, body sizes, and body positions through a clean nested class structure and online editor.

This module breaks the dependence on hardcoded C lists by exposing new Python helpers to the C layer, allowing dynamic configuration of body position types and sizes that were previously static in `body.c`. The system provides clear separation between C logic and configuration data, enabling anyone to gradually migrate away from C-defined lists toward a fully Python-managed configuration system.

**Requires NakedMud 4.3.0 or higher** (includes modifications to `body.c` for dynamic list support).

## Installation

### Option 1: Download and Extract
1. Download the entities module files
2. Extract to your `lib/pymodules/entities/` directory
3. Restart your MUD or reload Python modules

### Option 2: Git Submodule
```bash
cd lib/pymodules/
git submodule add https://github.com/NakedMud/entities entities
git submodule update --init --recursive
```

## Commands Added

The module adds these admin commands:

- **`entityconfig`** - Online configuration editor for entity settings (admin level required)

## Configuration Files

- **Runtime config**: `lib/misc/entities-race-config` - Active race configuration (auto-created with defaults)
- **Runtime config**: `lib/misc/entities-body-config` - Active body configuration (auto-created with defaults)

## What It Does

The entities configuration module centralizes all race definitions, body types, body sizes, and body position types into a single manageable system. It replaces scattered hardcoded C lists with a structured, persistent Python configuration that can be modified at runtime through an intuitive menu system.

### Breaking C Dependencies

Previously, body position types and sizes were hardcoded in static C arrays within `body.c`, making expansion difficult and requiring C code changes for new races or body configurations. This module:

- **Exposes Python helpers to C**: New functions like `world.add_bodypos_type()` and `world.add_bodysize()` allow Python to dynamically register new types
- **Separates logic from data**: C code handles the mechanics while Python manages the configuration
- **Enables gradual migration**: Existing C-defined types continue to work while new Python-defined types extend the system
- **Provides clean expansion**: New races, body types, and sizes can be added without touching C code
- **Maintains compatibility**: All existing hardcoded definitions remain functional alongside dynamic additions

### Race Categories
- **Races**: elf, hill giant, dragon, centaur (with full body templates)
- **Body Sizes**: diminuitive, tiny, small, medium, large, huge, gargantuan, collosal, gigantic
- **Body Position Types**: head, face, ear, neck, torso, arm, wing, wrist, hand, finger, waist, leg, foot, hoof, claw, tail, held
- **Custom Body Types**: hands, legs, feet, wings, hooves (configurable extensions)

### Body Configuration
- **Built-in Position Types**: All standard C-defined body positions (floating about head, about body, head, face, etc.)
- **Custom Position Types**: Additional position types for specialized races (hands, legs, feet, wings, hooves)
- **Built-in Body Sizes**: Standard size categories from diminuitive to collosal
- **Custom Body Sizes**: Extended sizes like gigantic for massive creatures

## Usage Example

```
> entityconfig
Entities Configuration Editor
1) Body position types (26): floating about head, about body, head...
2) Body sizes (9): diminuitive, tiny, small, medium, large...
3) Races (4): elf, hill giant, dragon, centaur...
Q) Quit

Enter choice: 3
Races Configuration
Current races (4):
  * human (hum) - PC, 15 pos
  * hill giant (hgi) - NPC, 21 pos
  elf (elf) - PC, 21 pos
  dragon (dra) - NPC, 17 pos
  ...

1) Add race
2) Remove race
3) Edit race
Q) Return to main menu

Enter choice: 1
Enter new race name: orc
Created new race: orc
```

## Technical Details

### Architecture

The module uses a nested class structure:
- **`RaceConfig`** - Main race container class
- **`BodyConfig`** - Body configuration container
- **`Race`** - Individual race with body template and PC flag
- **`BodyPosition`** - Individual body position with name, type, and weight
- **`BodyTypes`** - Custom body position types and sizes

### Storage Format

Configuration is stored using NakedMud's StorageSet/StorageList system in a clean format:
```
races:=
  name: elf
  abbrev: elf
  pc_ok: True
  body_size: medium
  body_positions:=
    name: head
    type: head
    weight: 2
    -
```

### API Functions

#### Retrieval Functions
```python
import entities.entity_config as entity_config

# Get configuration objects
race_config = entity_config.get_race_config()
body_config = entity_config.get_body_config()

# Get race information
race_names = race_config.get_race_names()
elf_race = race_config.get_race("elf")
```

#### Modification Functions
```python
# Add/remove races
new_race = Race("orc", "orc", True)
race_config.add_race(new_race)
race_config.remove_race("orc")

# Add/remove body types
body_config.body_types.add_bodypart_type("tentacle")
body_config.body_types.add_bodysize("titanic")

# Save changes
entity_config.save_entity_configs()
```

#### Direct Access
```python
# Get the main configuration objects
race_config = entity_config.get_race_config()
body_config = entity_config.get_body_config()

# Access race data
all_races = race_config.races
elf = race_config.get_race("elf")
body_positions = elf.body_positions

# Access body configuration
custom_types = body_config.body_types.bodypart_types
custom_sizes = body_config.body_types.bodysizes
```

### Race and Body Integration

The module provides comprehensive race management that integrates with NakedMud's world system:

#### Race Definition
Each race includes:
- **`name`** - Full race name (e.g., "hill giant")
- **`abbrev`** - Short abbreviation (e.g., "hgi")
- **`pc_ok`** - Whether players can choose this race
- **`body_size`** - Size category (from body config sizes)
- **`body_positions`** - Complete body template with positions, types, and weights

#### Body Position System
Body positions define:
- **`name`** - Position name (e.g., "left arm")
- **`pos_type`** - Position type (e.g., "arm", must match C definitions or custom types)
- **`weight`** - Percentage weight for targeting (0-100)

### Script Integration

From within NakedMud scripts (see `html/tutorials/scripting/`):

```python
# In a mobile prototype script
import entities.entity_config as entity_config
import world

# Get available races
race_config = entity_config.get_race_config()
available_races = race_config.get_race_names()

# Set character race
me.race = mudsys.random_choice(available_races)

# Get race-specific body template
race = race_config.get_race(me.race)
if race:
    me.body_size = race.body_size
    # Body positions are automatically applied by world system
```

```python
# Check available body types and sizes
body_config = entity_config.get_body_config()
custom_types = body_config.body_types.get_bodypos_types()
custom_sizes = body_config.body_types.get_bodysizes()

# Validate position types
if "wings" in custom_types:
    # This race can have wings
    pass
```

### Backward Compatibility

All existing race and body functions are preserved. The module maintains full backward compatibility with existing code that relies on race and body configuration data.

### OLC Integration

The module follows NakedMud's OLC patterns with automatic save confirmation on exit, similar to `socedit` and other editors. Changes are immediately available to scripts and other modules without restart.
