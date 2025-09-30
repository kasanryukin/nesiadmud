# NakedMud Vitality System Module

A comprehensive vitality system for NakedMud that provides health, spell points, energy points, regeneration, death handling, and revival mechanics through a clean auxiliary data structure and configurable parameters.

## Installation

### Option 1: Download and Extract
1. Download the vitality module files
2. Extract to your `lib/pymodules/vitality/` directory
3. Restart your MUD or reload Python modules

### Option 2: Git Submodule
```bash
cd lib/pymodules/
git submodule add <repository-url> vitality
git submodule update --init --recursive
```

## Commands Added

The module adds these commands:

- **`hp`** - Display current vitality status (player level)
- **`damage <target> <amount> [stat]`** - Damage a character (admin level)
- **`heal <target> <amount> [stat]`** - Heal a character (admin level)
- **`pray [divine]`** - Revive from death (player level, divine for privileged users)

## Configuration Files

- **Runtime config**: `lib/misc/vitality-config` - Active configuration (auto-created with defaults)

## What It Does

This NakedMud module provides extensible vitality mechanics with a comprehensive three-stat system (Health/Spell/Energy) that includes automatic regeneration, death handling, revival mechanics, and extensive customization options. It adds a foundation for combat, magic, and physical activity systems to the barebones NakedMud codebase.

### Core Vitality Stats

The vitality system tracks three essential character statistics that form the foundation of gameplay mechanics. **Health Points (HP)** represent a character's physical condition and life force - when HP drops to zero, the character dies and enters the death/revival cycle. **Spell Points (SP)** track magical energy and mental focus, providing the resource pool for spellcasting and mental abilities. **Energy Points (EP)** measure physical stamina and endurance, consumed by strenuous activities like combat maneuvers, running, or physical skills.

Each stat has both current and maximum values, allowing for temporary boosts or permanent improvements through gameplay progression. The system provides comprehensive status messages that give players clear feedback about their character's condition at any vitality level.

### Death and Revival System

When a character's health drops to zero, they automatically die and are transported to a configurable **death room** where they await revival. The primary revival mechanism is the `pray` command, which allows dead characters to return to life when used in the death room. For administrative convenience, privileged users (admins, wizards, scripters, and builders) can use `pray divine` to revive themselves anywhere in the world.

The death system includes an extensible **hook framework** that allows other modules to customize death and revival behavior. This enables features like equipment loss, experience penalties, or special resurrection mechanics to be added without modifying the core vitality system. A **corpse system** is planned for a future minor version update to handle physical remains and item recovery.

### Regeneration System

Characters automatically recover vitality over time through a **heartbeat-based regeneration** system. The regeneration frequency and rates are fully configurable - administrators can set how many heartbeats pass between regeneration ticks and how much each stat recovers per tick. Each vitality stat (HP, SP, EP) has its own regeneration rate, allowing for balanced recovery that matches the game's intended pacing.

The system includes **smart regeneration** that only processes stats below their maximum values, and provides optional **display feedback** to keep players informed of their recovery. Players can see either detailed per-tick status updates or just completion messages when they reach 100% in any stat, depending on configuration preferences.

## Usage Examples

### Basic Player Usage
```
> hp
Health: You are in good condition.
Spell:  You are mentally alert.
Energy: You are feeling vigorous.

> pray
Your prayers are answered! You feel life returning to your body.
```

### Admin Commands
```
> damage wizard 5 hp
Damaged wizard for 5 hp.

> heal wizard 10 sp
Healed wizard for 10 sp.

> heal wizard 50
Tried to heal wizard for 50 hp, but only 15 was needed.
```

### Divine Revival
```
> pray divine
Your divine powers restore your life force!
```

## Technical Details

### Architecture

The module uses NakedMud's auxiliary data system:
- **`VitalityAuxData`** - Core data class attached to characters
- **`VitalityConfig`** - Configuration management with persistent storage
- **Hook Integration** - Comprehensive event system for extensibility

### Storage Format

Configuration is stored using NakedMud's StorageSet system:
```
defaults:-
  hp_hitdie: 10
  sp_hitdie: 10
  ep_hitdie: 10
  regen_heartbeat: 10
  hp_regen: 1
  sp_regen: 1
  ep_regen: 1
  death_room: limbo@limbo
  regen_display: False
  regen_display_full: True
  -
status:-
  hp_status:-
    messages:=
      threshold: 100
      message: You are in perfect condition.
      -
```

### API Functions

#### Core Functions
```python
import vitality.vitality_system as vitality

# Damage and healing
vitality.damage_character(ch, 10, "hp")
vitality.heal_character(ch, 5, "sp")

# Status checking
aux = ch.getAuxiliary("vitality_data")
current_hp = aux.hp
max_hp = aux.maxhp
is_dead = aux.dead
```

#### Configuration Access
```python
import vitality.vitality_config as vitality_config

# Get configuration
config = vitality_config.get_vitality_config()
death_room = config.death_room
regen_rate = config.hp_regen

# Status messages
hp_message = config.get_status_message("hp", current_hp, max_hp)
```

### Hook System

The module provides extensive hooks for customization:

```python
import hooks

# Pre-damage hook (can modify or cancel damage)
def my_pre_damage_hook(info):
    ch, amount, stat_type = hooks.parse_info(info)
    # Custom logic here
    
hooks.add("vitality_pre_damage", my_pre_damage_hook)

# Death hook (custom death handling)
def my_death_hook(info):
    ch, = hooks.parse_info(info)
    ch.send("You feel your life force ebbing away...")
    
hooks.add("vitality_death", my_death_hook)
```

Available hooks:
- `vitality_pre_damage` - Before damage application
- `vitality_post_damage` - After damage application  
- `vitality_pre_healing` - Before healing application
- `vitality_post_healing` - After healing application
- `vitality_stat_change` - When any stat changes
- `vitality_death` - When character dies
- `vitality_revival` - When character is revived

### Script Integration

From within NakedMud scripts:

```python
# In a combat script
import vitality.vitality_system as vitality

# Apply weapon damage
weapon_damage = 15
vitality.damage_character(target, weapon_damage, "hp")

# Spell costs
spell_cost = 8
vitality.damage_character(caster, spell_cost, "sp")

# Stamina costs  
stamina_cost = 5
vitality.damage_character(ch, stamina_cost, "ep")
```

```python
# In a healing potion script
import vitality.vitality_system as vitality

# Heal the drinker
heal_amount = 25
vitality.heal_character(ch, heal_amount, "hp")
ch.send("You feel much better!")
```

```python
# In a room script (death room)
import vitality.vitality_config as vitality_config

# Check if this is the death room
config = vitality_config.get_vitality_config()
if str(ch.room) == config.death_room:
    ch.send("You sense the presence of death here...")
```

### Configuration Options

All options are configurable via the `misc/vitality-config` file:

#### Core Stats
- **`hp_hitdie`** - Starting HP (default: 10)
- **`sp_hitdie`** - Starting SP (default: 10)
- **`ep_hitdie`** - Starting EP (default: 10)

#### Regeneration
- **`regen_heartbeat`** - Heartbeats between regen (default: 10)
- **`hp_regen`** - HP per regen tick (default: 1)
- **`sp_regen`** - SP per regen tick (default: 1)  
- **`ep_regen`** - EP per regen tick (default: 1)

#### Death System
- **`death_room`** - Where dead players go (default: limbo@limbo)
- **`corpse_object`** - Corpse template (default: corpse@limbo)

#### Display Options
- **`regen_display`** - Show per-tick status (default: False)
- **`regen_display_full`** - Show 100% messages (default: True)

#### Status Messages
Comprehensive status messages for all vitality levels (0-100% in 10% increments) for each stat type, fully customizable through the configuration file.

### Command Fallthrough

The `pray` command uses NakedMud's command fallthrough system:
- Living players outside death room: Returns -1 for fallthrough to other `pray` commands
- Living divine users: Get appropriate message
- Dead players: Handle revival appropriately

This allows integration with other prayer/religion systems without conflicts.

### Backward Compatibility

The module is designed to integrate cleanly with existing NakedMud installations without breaking existing functionality. All vitality data is stored in auxiliary data that doesn't interfere with core character systems.

### Performance Considerations

- Regeneration only processes living player characters
- Status messages use efficient threshold-based lookup
- Configuration is cached and only reloaded when changed
- Hooks are only called when relevant events occur
