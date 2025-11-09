# MUD System Architecture Analysis: Phase 1-4

## Overview

This is a sophisticated MUD engine architecture built with Python/C integration, implementing a character progression system with layered complexity. The phases build progressively, with each phase either deepening existing systems or introducing new mechanics that integrate with prior work.

---

## Phase 1: Vitality & Injury System ✓ (Complete)

### Components

**Vitality Core (vitality_damage.py)**
- HP/SP/EP management
- Damage application with type classification (physical, magical, fire, etc.)
- Death detection and resurrection system
- Hook-based architecture for external systems to intercept damage

**Injury System (vitality_injury.py)**
- Per-body-part wound tracking with severity levels (1-8)
- Wound types: surface, internal, nervous
- Wound status effects: bleeding, poisoned, diseased, burned, infected
- Wound progression mechanics (infection escalation, bleed severity increase)
- Scar persistence after wound healing

**Death Handler (death_handler.py)**
- Death messaging with customizable templates (%m, %n placeholders)
- Respawn mechanics with configurable delay
- Corpse framework (stubbed for future implementation)

**Injury Penalties (injury_penalties.py)**
- Comprehensive penalty mapping: body_part → severity → {skill: penalty}
- Dynamic skill modifier system (negative penalties = bonuses)
- Realistic penalties: eye scar penalizes ranged combat heavily; face scar penalizes persuasion but bonuses intimidation

**NPC Movement (pymud_movement.c)**
- Zone-bounded wandering to prevent NPCs leaving their designated areas
- Exit validation based on zone proto keys
- Configurable no-wander prototypes (statues, shopkeepers, immobiles)

### Architecture Patterns

- **Hook System**: Fire-and-forget events (on_damage, on_death) allow other systems to listen without tight coupling
- **Auxiliary Data**: Vitality and injury data stored as character auxiliaries, not core character struct
- **Heartbeat Callbacks**: Death countdown and wound progression checked at configurable intervals
- **C/Python Bridge**: Performance-critical movement code in C; game logic in Python

### Phase 1 → Phase 2 Integration Points

1. **Vitality as Derived Values**: HP/SP/EP become derived from Constitution/Willpower attributes (Phase 2)
2. **Injury Penalties Foundation**: Wounds already generate skill penalties; Phase 2 skills will consume these
3. **Death Flow**: Respawn system will link to character creation/loadout (Phase 2)
4. **Hook Consumer**: Death/damage hooks are ready for Phase 2 skill checks, Phase 3 combat calculations, Phase 4 magic triggers

---

## Phase 2: Experience, Skills, Classes/Guilds

### What Phase 2 Must Add

**Experience & Leveling**
- Experience pool tied to character kill/quest tracking
- Level-based progression with breakpoints
- Skill point allocation per level
- Attribute increases tied to leveling

**Attribute System** (NEW)
- Primary attributes: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
- Derived values: Max HP = (CON × base) + bonuses, Max SP = (WIS × base) + bonuses, etc.
- Attribute modifiers for skills: Climb check = Strength modifier + Skill rank

**Skills Framework**
- Skill rank system (typically 0-20 or similar)
- Skill check mechanics: d20 + rank + attribute_modifier + situational_modifiers
- Skill learning rates affected by class/guild (Phase 2 late addition)
- Integration with Phase 1 injury penalties automatically reduces effective skill ranks
  - Example: Character with Arcana skill rank 15 and -8 penalty from head scar effectively has rank 7

**Professions/Classes/Guilds** (Basic Framework)
- Attribute requirements (e.g., "Wizard" requires INT ≥ 14)
- Skill bonus learning rates (e.g., Rogues learn "Lockpicking" 50% faster)
- Restricted skill access (Warriors can't learn "Spellcraft")
- Kit allocation: starting gear, starting skills at rank 1-3

### Phase 2 Architecture

```
Character → Attributes (Str, Dex, Con, Int, Wis, Cha)
         ↓
         → Derived Values (HP from CON, Mana from WIS, etc.)
         ↓
         → Skills (each has Rank + Attribute link)
         ↓
         → Professions/Guild (modifies skill learning, restricts skills)
         ↓
         → Experience Pool (tracks progress toward next level)
```

### Phase 2 → Phase 3 Integration

1. **Skill Ranks in Combat**: Attack bonus = STR modifier + Weapon Skill rank + circumstances
2. **Defense Calculation**: Defense = DEX modifier + Dodge skill rank - injury penalties
3. **Combat Skills**: Melee Combat, Ranged Combat, Defense are skills that Phase 3 combat system calls
4. **Circumstance Modifiers**: Flanked = -2 to skill checks; injured = additional penalty from Phase 1 wounds

---

## Phase 3: Combat System & Enhanced Injury

### What Phase 3 Must Add

**Combat Mechanics**
- Initiative system: DEX modifier + Initiative skill rank + d20
- Action economy: standard action, move action, bonus action per round
- Attack resolution: Attacker Skill Check vs Defender Skill Check
- Damage calculation: Weapon damage + STR/DEX modifier + bonuses
- Called shots: ability to target specific body parts (replaces random targeting)

**Called Shots & Locational Damage**
- Attacker makes called shot skill check (higher DC than normal hit)
- If successful, damage applied to specific body part via Phase 1 injury system
- Critical hits might auto-apply bleeding or other wound status effects
- Limb-specific effects: crippling leg increases movement penalties, arm hit reduces melee combat

**Damage Type Integration**
- Weapon categories: slashing, piercing, blunt, magical, etc.
- Type affects wound classification: slashing → surface wounds, piercing → internal wounds
- Poison/disease risk depends on wound type

**Combat Hook Integration**
- on_damage hook (Phase 1) fires during combat with attacker/defender/weapon data
- Systems can listener to modify damage mid-combat (shields, spell absorption, armor)
- on_death hook (Phase 1) fires when combat reduces defender to 0 HP

### Combat Flow with Phase 1-2 Integration

```
Combat Round:
1. Roll Initiative (DEX mod + Initiative skill + d20)
2. Attacker's Turn:
   - Declare action: Attack (normal), Called Shot (specific body part), Defend, Cast Spell, etc.
   - If Attack: Roll = d20 + Melee Combat skill + STR mod + circumstances (injured? flanked?)
   - Phase 1 injury penalties automatically reduce effective skill
   - Compare vs Defender's Defense value
3. If Hit:
   - Roll damage: Weapon die + STR mod + enchantments
   - Fire on_damage hook (Phase 1)
   - Any system can intercept: armor absorbs 5, shield blocks 3, spell ward absorbs 2
   - Remaining damage applied to defender's HP (Phase 1 vitality)
4. If Called Shot Hit:
   - Apply wound to specific body part (Phase 1 injury)
   - Determine wound type/severity based on weapon
   - Trigger wound status effects (bleeding if slashing, infection risk if poisoned)
   - Wounds now penalize defender's future skill checks (Phase 2)
5. Defender Death Check:
   - If HP ≤ 0, fire on_death hook (Phase 1)
   - Death handler initiates respawn (Phase 1)
   - Killer gains experience (Phase 2)
```

### Phase 3 Architecture

```
Combat System (NEW)
├── Initiative Resolution
├── Action Declaration
├── Skill Check Resolution
│   ├── Attacker Skill Check (Melee/Ranged Combat skill + attribute mod)
│   ├── Defender Skill Check (Defense skill + attribute mod)
│   └── Compare vs DC (difficulty class)
├── Damage Calculation
│   ├── Base weapon damage
│   ├── + Attribute modifier (STR or DEX)
│   ├── + Bonuses (enchantments, buffs)
│   └── - Reductions (armor, abilities, on_damage hook modifications)
├── Applied to Vitality (Phase 1)
├── Wound Application (Phase 1 - locational from called shots)
└── Death Resolution (Phase 1)
```

---

## Phase 4: Magic System & Class Specials

### What Phase 4 Must Add

**Magic/Spellcasting Framework**
- Spell list: each spell has casting time, cost (mana/SP), range, duration
- Spellcasting check: d20 + Spellcraft skill + INT mod + class bonus
- Spell effects framework: damage, healing, buff, debuff, control, summon, etc.

**Class/Guild/Profession Specials**
- Class-specific abilities: Warrior's Cleave (attack all adjacent), Rogue's Backstab (2x damage if flanking)
- Resource pools for abilities: Warrior Action Points, Rogue Combo Points, Mage Spell Slots
- Cooldowns and restrictions: "Cleave" available after standard attack, limited to 1/round

**Integration with Prior Phases**

All spells/abilities hook into existing systems:
- Damage spells fire on_damage hook (Phase 1) → interception by shields, absorption
- Healing spells call Phase 1 heal_damage function
- Buffs modify Phase 2 attribute/skill modifiers
- Debuffs apply Phase 2 skill penalties or Phase 1 wound status effects
- AoE spells apply injuries to multiple targets in Phase 1
- Combat abilities (Cleave, Whirlwind Attack) check defense for each target using Phase 3 combat checks

### Phase 4 Combat Example: Fireball Spell

```
Mage casts Fireball on 3 enemies

1. Spellcasting Check: d20 + Spellcraft skill + INT mod vs enemy Dodge skill check (Phase 2 skills)
2. If hit, calculate damage: 4d6 fire damage + INT mod + spell level bonus
3. For each target:
   a. Fire on_damage hook with damage_type="fire" (Phase 1)
   b. Armor/shields intercept some damage via hook (Phase 3 combat)
   c. Remaining damage applied to HP (Phase 1 vitality)
   d. Check if HP ≤ 0 → on_death hook (Phase 1)
   e. Apply fire wound to random body part via Phase 1 injury system
   f. Fire wound automatically penalizes skills (Phase 2 injury penalties)
   g. If wound severity ≥ 5, add "burned" status effect (Phase 1 wound progression)
4. Mage's mana pool decreases, goes on cooldown
```

### Phase 4 Architecture

```
Magic System (NEW)
├── Spell Registry (name, cost, casting_time, range, damage/effect)
├── Spellcasting Resolution
│   ├── Spellcraft skill check (Phase 2 skills)
│   ├── Fire on_spell_cast hook (can be intercepted by counterspell)
│   └── Calculate effect
├── Spell Effects
│   ├── Damage → on_damage hook (Phase 1)
│   ├── Healing → heal_damage() (Phase 1)
│   ├── Buff → modify attribute/skill modifiers (Phase 2)
│   ├── Debuff → apply skill penalties (Phase 2) or wound effects (Phase 1)
│   └── Control → apply status effects (Phase 1 wound statuses)
├── Class Specials
│   ├── Registry of abilities per class (Phase 2)
│   ├── Resource pools (AP, CP, slots)
│   ├── Cooldown tracking
│   └── Trigger conditions (post-attack, while flanked, etc.)
└── All effects feed into existing systems (vitality, skills, injuries, combat checks)
```

---

## Cross-Phase Integration Map

### Phase 1 → Phase 2 Integration
- **Vitality as Derived**: HP = 10 + (CON × 5) + bonuses; SP = 5 + (WIS × 3) + bonuses
- **Injury Penalties**: Character skill checks automatically reduced by wound penalties
- **Death/Respawn**: Character respawns with full health but scars remain, applying penalties

### Phase 2 → Phase 3 Integration
- **Skill Checks in Combat**: All attacks/defense use Phase 2 skill system
- **Circumstance Modifiers**: Injury penalties automatically apply to combat skill checks
- **Called Shots**: Target selection uses skill check DC; hit applies Phase 1 wounds
- **Professions Affect Combat**: Rogues get +2 to Melee Combat vs humanoids, etc.

### Phase 3 → Phase 4 Integration
- **Spell Damage**: Fire on_damage hooks that combat system listens to
- **Ability Damage**: Warrior Cleave damage calculation identical to normal attack (uses Phase 3 system)
- **Spell Interception**: Shield spell can intercept both physical attacks and magic via on_damage hook
- **Area Effects**: Spells damage multiple targets using same Phase 3 combat resolution per target

### Bidirectional Dependencies
- **Combat → Injuries → Skills**: Attacker hits defender, applies wound, wound penalizes defender's next action
- **Skills → Combat → Magic**: Rogue's high Melee Combat skill enables successful Backstab ability (Phase 4), which deals extra damage
- **Magic → Vitality → Death**: Mage casts Fireball, damage applied (Phase 1), 0 HP triggers death (Phase 1), respawn flow (Phase 1)

---

## Key Architectural Decisions

### 1. Hook System as Connective Tissue
All damage flows through `on_damage` hook, allowing Phase 3 combat, Phase 4 spells, Phase 1 status effects to all modify damage without direct coupling.

### 2. Auxiliary Data Storage
Character attributes, skills, professions stored as auxiliaries, not core struct. Allows hot-reloading and extensibility.

### 3. Skill Checks as Universal Resolution
Every uncertain outcome (attack, defense, spell casting, skill checks) uses same d20 + modifier + d20 system.

### 4. Injury Penalties as Automatic Modifier
Phase 1 wounds automatically reduce Phase 2 skill effectiveness without explicit calls—wounds are "always on" penalties.

### 5. Called Shots as Bridge
Phase 3 called shots directly invoke Phase 1 injury application, creating combat-to-injury causality chain.

### 6. Stateful Progression
Characters don't reset between phases—attributes persist, skills persist, injuries persist. A veteran NPC has visible scars and reduced capabilities.

---

## Design Principles Observed

1. **Separation of Concerns**: Vitality ≠ Injury ≠ Death handler; each owns its domain
2. **Extensibility via Hooks**: External systems (combat, magic, buffs) don't modify core code
3. **Realistic Causality**: Damage → wound → penalty → failed check → narrative consequence
4. **Skill-Centric Resolution**: Every d20 roll uses same system with modifiers from attributes/skills/circumstances
5. **Persistent World State**: Scars remain, lessons learned, progression visible

---

## Implementation Roadmap for Phase 2

1. **Attributes System**: Add 6 attributes to character, initialize on creation, display in score command
2. **Derived Values**: Refactor vitality to calculate max_hp, max_sp, max_ep from attributes
3. **Skills System**: Create skill registry, add skill ranks to character, implement skill check function
4. **Skill-Injury Integration**: When calculating skill check, automatically subtract injury penalties from roll
5. **Professions Framework**: Create profession registry with attribute reqs, skill bonuses, restricted skills
6. **Experience System**: Track kills/quests, accumulate exp_points, calculate next_level_exp, level up on breakpoint
7. **Integration Test**: Create character, receive wound, attempt skill check, verify penalty applied

