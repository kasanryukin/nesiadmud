# MUD System Architecture & Integration Reference

## Core Foundation Layer (Currently Implemented/In Progress)

### 1. Entities System ✓ Implemented
- **Manages:** Races, body positions, body sizes
- **Dependencies:** None (foundation)
- **Required by:** ALL character/NPC systems
- **C Integration:** Already exists (`world.c`)
- **Status:** Working, integrated with attributes

### 2. Attributes System ✓ Implemented
- **Manages:** Base stats (STR, REF, AGI, CHA, DIS, WIS, INT, STA), TDP
- **Dependencies:** Entities (racial modifiers)
- **Required by:** Vitality, Skills, Combat, Character Gen
- **C Integration:** Python-only, uses auxiliary data
- **Status:** Complete with TDP training system

### 3. Vitality System ✓ Implemented - Stage One, Assignment, Regereration and Attribute Calculations
- **Manages:** HP, SP, EP, regeneration
- **Dependencies:** Attributes (for calculations), Entities (body positions for injury)
- **Required by:** Combat, Injury, Death
- **C Integration:** Likely needs C hooks for damage events
- **Status:** Complete, waiting on combat, injury, and death systems.

---

## Character Development Layer

### 4. Experience Pools
- **Manages:** Multiple XP pools, level progression
- **Dependencies:** Attributes (INT affects pool size), Guild/Class
- **Required by:** Skills, Guilds, Character advancement
- **C Integration:** Python-only likely sufficient
- **Integration Points:**
  - Attribute INT affects pool size
  - Guild determines available pools
  - TDP granted per level

### 5. Skills System
- **Manages:** Skill learning, usage, proficiency
- **Dependencies:** Attributes (modifiers), Experience Pools, TDP (training)
- **Required by:** Combat, Crafting, Social systems
- **C Integration:** May need C for performance-critical skill checks in combat
- **Integration Points:**
  - Attributes modify skill checks
  - TDP can be used for skill training
  - Experience pools fuel skill advancement
  - Guild restricts available skills

### 6. Guilds/Classes/Professions
- **Manages:** Character archetypes, restrictions, abilities
- **Dependencies:** Attributes (requirements), Skills (guild skills), Experience
- **Required by:** Special Abilities, Skill availability
- **C Integration:** Python-only sufficient
- **Integration Points:**
  - Attribute requirements for joining
  - Modifies attribute effectiveness
  - Grants skill access
  - Affects vitality calculations (HP/SP/EP bonuses)

---

## Combat & Conflict Layer

### 7. Combat System
- **Manages:** Attack resolution, damage calculation, combat rounds
- **Dependencies:** Attributes, Skills, Vitality, Gear, Body positions
- **Required by:** PvE, PvP, Death
- **C Integration:** **STRONGLY RECOMMENDED** - combat loops need performance
- **Integration Points:**
  - STR/AGI affect accuracy and damage
  - Skills determine combat options
  - Vitality tracks damage taken
  - Gear modifies stats
  - Body positions for targeted attacks

### 8. Injury System
- **Manages:** Body part damage, status effects, wounds
- **Dependencies:** Vitality, Entities (body positions), Combat
- **Required by:** Death, Healing, Movement restrictions
- **C Integration:** Python sufficient if using existing damage hooks
- **Integration Points:**
  - Body positions determine injury locations
  - Vitality manages wound severity
  - Attributes (STA) affect injury resistance
  - Combat causes injuries

### 9. Death & Resurrection
- **Manages:** Character death, corpses, penalties, revival
- **Dependencies:** Vitality, Combat, Injury
- **Required by:** Corpse recovery, Experience penalties
- **C Integration:** Hooks into existing death system (likely C-based)
- **Integration Points:**
  - Vitality HP reaches 0
  - Experience loss on death
  - Attribute penalties possible
  - Guild-specific death mechanics

---

## Gear & Equipment Layer

### 10. Gear System (Partially Implemented)
- **Manages:** Weapons, armor, equipment stats
- **Dependencies:** Entities (body positions for wear locations), Attributes (requirements)
- **Required by:** Combat, Economy
- **C Integration:** Python-only appears sufficient
- **Integration Points:**
  - Body positions determine wear slots
  - Attribute requirements to equip
  - Stat bonuses to attributes
  - Combat damage/AC calculations

### 11. Crafting System
- **Manages:** Item creation, resource gathering, recipes
- **Dependencies:** Skills, Gear, Economy
- **Required by:** Economy, Player progression
- **C Integration:** Python-only sufficient
- **Integration Points:**
  - Skills determine craft success
  - Attributes affect craft quality
  - Experience pools for mastery

---

## Magic & Abilities Layer

### 12. Magic/Spell System
- **Manages:** Spell casting, mana costs, effects
- **Dependencies:** Attributes (INT/WIS), Vitality (SP), Skills, Guilds
- **Required by:** Combat, Healing, Utility
- **C Integration:** Python for spells, but may need C hooks for combat integration
- **Integration Points:**
  - INT/WIS determine spell power
  - Vitality SP as mana pool
  - Skills for spell learning
  - Guild determines available spells
  - Attributes affect spell success

### 13. Special Abilities (Class/Guild Powers)
- **Manages:** Non-spell special moves, techniques
- **Dependencies:** Guilds, Attributes, Vitality (EP), Skills
- **Required by:** Combat, Class identity
- **C Integration:** Python-only likely sufficient
- **Integration Points:**
  - Guild grants abilities
  - Attributes determine effectiveness
  - Vitality EP as resource
  - Skills as prerequisites

---

## World Interaction Layer

### 14. Economy System
- **Manages:** Currency, shops, prices, trading
- **Dependencies:** Attributes (CHA affects prices), Guilds (discounts)
- **Required by:** Crafting, Gear acquisition, Mail (postage?)
- **C Integration:** Python-only sufficient
- **Integration Points:**
  - CHA affects shop prices
  - Guild discounts
  - Crafting creates sellable items

### 15. Social System
- **Manages:** Factions, reputation, relationships
- **Dependencies:** Attributes (CHA), Guilds, Actions
- **Required by:** Quests, Shop prices, NPC interactions
- **C Integration:** Python-only sufficient
- **Integration Points:**
  - CHA affects social interactions
  - Guild affects faction standing
  - Actions modify reputation

### 16. Quest System
- **Manages:** Quest tracking, objectives, rewards
- **Dependencies:** Experience, Economy, Social, Skills
- **Required by:** Player progression, Content delivery
- **C Integration:** Python-only sufficient
- **Integration Points:**
  - Experience rewards
  - Economy rewards
  - Skill checks for completion
  - Reputation changes

---

## Communication Layer

### 17. Mail System
- **Manages:** Player-to-player messages
- **Dependencies:** Economy (postage cost?)
- **Required by:** Social interaction
- **C Integration:** Python-only (example proves this)

### 18. Bulletin Boards/Forums
- **Manages:** Public message boards
- **Dependencies:** None (standalone)
- **Required by:** Communication, Guilds (internal boards)
- **C Integration:** Python-only sufficient

---

## Recommended Implementation Order

### Phase 1: Core Mechanics (Current Focus)
1. ✅ Entities
2. ✅ Attributes & TDP
3. ✅ Vitality** (HP/SP/EP from attributes)
4. **→ Injury** (Simple version with vitality)
5. **→ Death basics** (hook into existing system)

### Phase 2: Character Development
6. Experience Pools (integrate with attributes)
7. Skills (basic framework, attribute modifiers)
8. Guilds/Classes (basic framework, attribute requirements)

### Phase 3: Combat Foundation
9. Combat System (**C integration priority**)
10. Gear integration with combat (attribute bonuses)
11. Enhanced Injury (body part specific)

### Phase 4: Magic & Abilities
12. Magic System basics (INT/WIS/SP)
13. Special Abilities framework (EP usage)
14. Integration with combat

### Phase 5: World Systems
15. Economy (CHA integration)
16. Crafting (skill integration)
17. Social/Reputation
18. Quests

### Phase 6: Quality of Life
19. Mail
20. Bulletin boards
21. Advanced features

---

## Critical Integration Points

### Where C Code is Strongly Recommended:
1. **Combat System** - Performance critical, called every combat round
2. **Damage Hooks** - Need to fire reliably and quickly
3. **Skill Check Core** - If skills are checked frequently in combat
4. **Action Queue** - If implementing action-based combat
5. **Regeneration Pulses** - For HP/SP/EP regeneration

### Where Python is Sufficient:
1. **All data management** (attributes, races, etc.)
2. **UI/Display systems** (stats command, etc.)
3. **Non-combat calculations**
4. **Social systems**
5. **Economy**
6. **Quest tracking**
7. **Auxiliary data** (character data storage)

---

## Future-Proofing Recommendations

### In Vitality Module (Next Priority):
```python
# Add hooks for future systems
def calculate_max_hp(ch):
    base = calculate_from_attributes(ch)
    # TODO: Add guild bonuses
    # TODO: Add equipment bonuses
    # TODO: Add temporary buffs
    return base

def take_damage(ch, amount, damage_type="physical", body_part=None):
    # body_part parameter ready for injury system
    # damage_type ready for resistances
    pass

def regenerate(ch):
    # Calculate regen rate from attributes
    # TODO: Add guild modifiers
    # TODO: Add equipment bonuses
    # TODO: Add status effect modifiers
    pass
```

### In Attributes Module (Add These):
```python
# Add placeholder for gear bonuses
def get_effective_attribute(ch, attr_name):
    base = aux.get_attribute(attr_name)
    # TODO: Add gear bonuses
    # TODO: Add temporary buffs/debuffs
    # TODO: Add guild modifications
    return base

# Hook for when attributes change (training, gear, etc.)
def on_attribute_changed(ch, attr_name, old_value, new_value):
    # TODO: Recalculate vitality
    # TODO: Update combat stats
    # TODO: Trigger any dependent systems
    pass
```

### In Entity Config:
- ✅ Already has attributes
- **Add:** Racial skill bonuses (placeholder dict)
- **Add:** Racial special abilities (placeholder list)
- **Add:** Racial resistances (placeholder dict)
- **Add:** Racial vitality modifiers (HP/SP/EP multipliers)

### In Character Gen:
- ✅ Already initializes attributes
- **Add:** Guild selection (after races)
- **Add:** Starting skills distribution
- **Add:** Starting equipment
- **Add:** Initial vitality calculation

---

## System Integration Map

```
┌─────────────┐
│  ENTITIES   │ ← Foundation: Races, body types
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ ATTRIBUTES  │ ← Stats: STR, REF, AGI, etc.
└──────┬──────┘
       │
       ├──────────────┐
       ▼              ▼
┌─────────────┐  ┌─────────────┐
│  VITALITY   │  │   SKILLS    │
│  HP/SP/EP   │  │  & GUILDS   │
└──────┬──────┘  └──────┬──────┘
       │                │
       └────────┬───────┘
                ▼
         ┌─────────────┐
         │   COMBAT    │
         └──────┬──────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│   INJURY    │   │    MAGIC    │
│   & DEATH   │   │  & SPECIAL  │
└─────────────┘   └─────────────┘
```

---

## Systems You Might Be Forgetting

1. **Container System** - Bags, chests, inventory management
2. **Food/Drink** - Hunger/thirst if you want survival elements
3. **Weather/Time** - Environmental effects on stats/combat
4. **Mounts/Vehicles** - Transportation
5. **Pets/Followers** - Companion system
6. **Achievement System** - Player accomplishments
7. **Tutorial System** - New player guidance
8. **Admin Tools** - Character editing, debugging (use OLC pattern)
9. **Logging System** - Player action history for debugging/restoration
10. **Backup/Restore** - Character rollback capability
11. **Status Effects** - Buffs, debuffs, conditions
12. **Emote System** - Social expressions
13. **Channel System** - Communication channels (gossip, auction, etc.)
14. **Banking System** - Currency storage
15. **Housing System** - Player-owned spaces

---

## Notes on Auxiliary Data Pattern

This is the core pattern used throughout the codebase:

```python
# Define the class
class MyAuxData:
    def __init__(self, set=None):
        # Initialize or load from storage set
        pass
    
    def copy(self):
        # Return a copy of this data
        pass
    
    def copyTo(self, other):
        # Copy to another instance
        pass
    
    def store(self):
        # Return a StorageSet for saving
        pass

# Install it
import auxiliary
auxiliary.install("my_data", MyAuxData, "character")

# Access it
aux = ch.getAuxiliary("my_data")
```

This pattern is used for:
- ✅ Attributes (attribute_data)
- → Vitality (hp_data, sp_data, ep_data)
- → Skills (skill_data)
- → Guild membership (guild_data)
- → Quest progress (quest_data)
- → And any other character-specific data

---

## Current Status Summary

**Working:**
- Entities system with races
- Attributes with TDP training
- Character generation with attribute initialization
- Entity config OLC with attribute editor
- Storage/loading of character attributes

**Next Immediate Steps:**
1. Vitality system (HP/SP/EP calculations from attributes)
2. Basic injury tracking
3. Death system integration
4. Simple regeneration

**After That:**
1. Experience pools
2. Basic skills framework
3. Guild system basics
4. Combat system (major milestone)
