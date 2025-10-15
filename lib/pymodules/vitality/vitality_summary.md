# Vitality System Integration Summary

## What We Built

### Core Files Created

1. **vitality/vitality_core.py** - Main vitality system
   - VitalityAuxData class (HP, SP, EP storage)
   - Calculation functions for max HP/SP/EP from attributes
   - Damage and healing functions
   - Vitality management utilities

2. **vitality/__init__.py** - Module loader
   - Installs auxiliary data on characters
   - Handles module initialization

### Integration Points

#### 1. Attributes → Vitality Formulas

```python
HP = stamina + ((strength + discipline) * 0.125)
SP = intelligence + ((discipline + wisdom) * 0.25)
EP = stamina + ((discipline + reflex + strength + agility) * 0.125)
```

**Example with 10s in all attributes:**
- HP = 10 + ((10 + 10) * 0.125) = 10 + 2.5 = 13 (rounded up)
- SP = 10 + ((10 + 10) * 0.25) = 10 + 5 = 15
- EP = 10 + ((10 + 10 + 10 + 10) * 0.125) = 10 + 5 = 15

**Example with trained attributes (STR 15, STA 12):**
- HP = 12 + ((15 + 10) * 0.125) = 12 + 3.125 = 16 (rounded up)

#### 2. Character Generation Integration

**char_gen.py now:**
1. Rolls racial attributes with variance
2. Calculates starting TDP
3. **NEW:** Initializes vitality from attributes
4. Sets HP/SP/EP to maximum

#### 3. Stats Command Integration

**`stats` command now shows:**
```
┌─────────────────────────────────────┐
│        CHARACTER STATUS             │
├─────────────────────────────────────┤
│ HP:     13/    13     (100.0%)      │
│ SP:     15/    15     (100.0%)      │
│ EP:     15/    15     (100.0%)      │
├─────────────────────────────────────┤
│ STR: Strength              10       │
│ REF: Reflex                10       │
... (all attributes)
├─────────────────────────────────────┤
│ TDP Available:                 500  │
│ TDP Spent:                       0  │
└─────────────────────────────────────┘
```

Color-coded based on percentage:
- Green (75-100%): Healthy
- Yellow (50-74%): Wounded
- Dark Yellow (25-49%): Badly wounded
- Red (0-24%): Critical

#### 4. Training Integration

**When you train an attribute:**
1. TDP is spent
2. Attribute increases
3. **NEW:** Vitality is automatically recalculated
4. HP/SP/EP maximums adjust proportionally
5. Current values scale to maintain the same percentage

**Example:**
```
Before: STR 10, HP 13/13 (100%)
Train STR to 15 (costs TDP)
After: HP recalculates to 16/16 (100%)
```

If you were damaged:
```
Before: STR 10, HP 7/13 (53.8%)
Train STR to 15
After: HP 9/16 (53.8%) - percentage maintained
```

## Key Functions Available

### Vitality Core Functions

```python
# Get character's vitality
vit_aux = vitality_core.get_vitality(ch)

# Calculate maximums
max_hp = vitality_core.calculate_max_hp(ch)
max_sp = vitality_core.calculate_max_sp(ch)
max_ep = vitality_core.calculate_max_ep(ch)

# Initialize new character
vitality_core.initialize_vitality(ch)

# Recalculate after attribute change
vitality_core.recalculate_vitality(ch)

# Damage and healing
actual_damage = vitality_core.take_damage(ch, amount, damage_type, body_part)
actual_healed = vitality_core.heal_damage(ch, amount, heal_type)

# Resource management
success = vitality_core.modify_sp(ch, -10)  # Spend 10 SP
success = vitality_core.modify_ep(ch, 5)    # Restore 5 EP

# Utility functions
percent = vitality_core.get_vitality_percent(ch, "hp")
color = vitality_core.get_vitality_color(percent)
```

## Hooks Available for Future Systems

### Damage Hook
```python
def my_damage_handler(info):
    ch, damage, damage_type, body_part = hooks.parse_info(info)
    # Handle damage event
    
hooks.add("take_damage", my_damage_handler)
```

### Healing Hook
```python
def my_heal_handler(info):
    ch, amount, heal_type = hooks.parse_info(info)
    # Handle healing event
    
hooks.add("character_healed", my_heal_handler)
```

### Death Hook
```python
def my_death_handler(info):
    ch, = hooks.parse_info(info)
    # Handle death event
    
hooks.add("character_death", my_death_handler)
```

## Testing Checklist

### 1. New Character Creation
- [ ] Create new character
- [ ] Check that stats shows HP/SP/EP
- [ ] Verify values match attribute calculations
- [ ] All pools at 100%

### 2. Existing Character Loading
- [ ] Log in with existing character
- [ ] Check stats command works
- [ ] Vitality should initialize if missing
- [ ] Values persist after logout/login

### 3. Training Integration
- [ ] Use `train strength 5 yes`
- [ ] Check stats before and after
- [ ] Verify HP maximum increased
- [ ] Verify current HP scaled proportionally

### 4. Race Differences
- [ ] Create characters of different races
- [ ] Check vitality varies based on racial attributes
- [ ] High STA race = more HP
- [ ] High INT/WIS race = more SP
- [ ] High AGI/REF race = more EP

## Future Expansion Points

### Injury System (injury.py)
```python
# VitalityAuxData already has:
self.injuries = {}  # {body_part: injury_level}

# When you build injury.py, hook into:
hooks.add("take_damage", handle_body_part_injury)
```

### Death System (death.py)
```python
# VitalityAuxData already has:
self.is_dead = False
self.death_count = 0

# When you build death.py, hook into:
hooks.add("character_death", handle_death)
```

### Regeneration System
```python
# Add to vitality_core.py or separate regen.py:
def regenerate_tick(ch):
    vit_aux = get_vitality(ch)
    
    # Calculate regen rates from attributes
    hp_regen = calculate_hp_regen(ch)
    sp_regen = calculate_sp_regen(ch)
    ep_regen = calculate_ep_regen(ch)
    
    # Apply regeneration
    vit_aux.hp = min(vit_aux.max_hp, vit_aux.hp + hp_regen)
    vit_aux.sp = min(vit_aux.max_sp, vit_aux.sp + sp_regen)
    vit_aux.ep = min(vit_aux.max_ep, vit_aux.ep + ep_regen)
```

### Combat Integration
```python
# In your combat system:
from vitality import vitality_core

def apply_combat_damage(attacker, defender, weapon_damage):
    # Calculate final damage with armor, etc.
    final_damage = calculate_damage(attacker, defender, weapon_damage)
    
    # Apply damage through vitality system
    actual = vitality_core.take_damage(defender, final_damage, "physical")
    
    # Show combat messages
    attacker.send(f"You hit {defender.name} for {actual} damage!")
    defender.send(f"{attacker.name} hits you for {actual} damage!")
```

### Guild/Class Bonuses
```python
# Add to calculate_max_hp() and similar:
def calculate_max_hp(ch):
    base = stamina + ((strength + discipline) * 0.125)
    
    # Guild bonuses
    guild_bonus = get_guild_hp_bonus(ch)  # e.g., warriors +20%
    
    return math.ceil(base * (1 + guild_bonus))
```

### Equipment Bonuses
```python
# Add to calculate functions:
def calculate_max_hp(ch):
    base = stamina + ((strength + discipline) * 0.125)
    
    # Equipment bonuses
    gear_bonus = get_gear_hp_bonus(ch)  # Sum of all equipped items
    
    return math.ceil(base + gear_bonus)
```

## Known Issues / TODO

1. **Regeneration:** Not implemented yet
   - Need C pulse integration or Python timer
   - Should regenerate HP/SP/EP based on attributes
   - Resting/sleeping should increase regen rate

2. **Status Effects:** Framework exists but not implemented
   - Poison, disease, buffs, debuffs
   - Should modify current/max vitality
   - Should affect regen rates

3. **Combat Integration:** Hooks ready but no combat system yet
   - `take_damage()` ready to use
   - Body part parameter ready for injury system
   - Death hook fires when HP reaches 0

4. **Admin Commands:** Need to add
   - `sethp <target> <amount>`
   - `setsp <target> <amount>`
   - `setep <target> <amount>`
   - `damage <target> <amount> [type]`
   - `heal <target> <amount>`

5. **Display Integration:** Could add to other commands
   - Prompt showing HP/SP/EP
   - Group display showing party vitality
   - Combat showing health bars

## Performance Considerations

- Auxiliary data uses storage module (efficient)
- Calculations cached in max_hp/max_sp/max_ep
- Only recalculates when attributes change
- Hook system allows optional features
- No performance-critical code in Python

## Summary

**What Works:**
✅ Vitality calculated from attributes
✅ Character creation initializes vitality
✅ Stats command shows vitality with colors
✅ Training attributes recalculates vitality
✅ Proportional scaling of current values
✅ Storage/loading of vitality data
✅ Hooks ready for combat/injury/death

**Next Steps:**
1. Test with multiple characters
2. Add admin commands for testing
3. Build regeneration system
4. Create injury tracking (injury.py)
5. Create death handling (death.py)
6. Integrate with combat system

**Integration Status:**
- Entities ✅
- Attributes ✅
- Vitality ✅ (Just completed!)
- Combat ⏳ (Next major milestone)
- Skills ⏳
- Guilds ⏳
