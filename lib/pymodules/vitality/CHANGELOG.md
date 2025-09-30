# Vitality Module v1.0.0
Initial vitality system for NakedMud

### ADDED
- Complete vitality system with HP/SP/EP stats, regeneration, and death handling
- VitalityAuxData class with health, spell points, energy points, and death state tracking
- Automatic regeneration via heartbeat hook with configurable rates and frequency
- Death handling with transport to configurable death room and revival system
- Prayer revival system with divine bypass for privileged users
- Comprehensive command set: `hp`, `damage`, `heal`, `pray`
- Hook integration system with pre/post damage, healing, death, and revival hooks
- Configurable display options for regeneration feedback

### FEATURES
- **Core Stats**: Health (HP), Spell Points (SP), Energy Points (EP) with max values and regen rates
- **Death System**: Automatic death at 0 HP with transport to death room and revival mechanics
- **Prayer Revival**: `pray` command for revival in death room, `pray divine` for admin anywhere access
- **Admin Commands**: `damage` and `heal` commands with smart target finding and validation
- **Status Display**: `hp` command shows current vitality with descriptive status messages
- **Regeneration**: Configurable heartbeat-based regeneration with optional display feedback
- **Configuration**: Persistent storage via `misc/vitality-config` with OLC-style management
- **Hooks**: Full hook system for vitality events (damage, healing, death, revival, stat changes)

### COMMANDS
- **`hp`** - Display current vitality status with descriptive condition messages
- **`damage <target> <amount> [stat]`** - Admin command to damage characters (hp/sp/ep)
- **`heal <target> <amount> [stat]`** - Admin command to heal characters with smart logic
- **`pray [divine]`** - Revival command (divine works anywhere for admin/wizard/scripter/builder)

### CONFIGURATION OPTIONS
- **`hp_hitdie`** - Starting/base HP value (default: 10)
- **`sp_hitdie`** - Starting/base SP value (default: 10) 
- **`ep_hitdie`** - Starting/base EP value (default: 10)
- **`regen_heartbeat`** - Heartbeats between regeneration ticks (default: 10)
- **`hp_regen`** - HP regenerated per tick (default: 1)
- **`sp_regen`** - SP regenerated per tick (default: 1)
- **`ep_regen`** - EP regenerated per tick (default: 1)
- **`death_room`** - Room for dead players (default: limbo@limbo)
- **`corpse_object`** - Corpse object template (default: corpse@limbo) *[Not yet implemented]*
- **`regen_display`** - Show per-tick regen status (default: False)
- **`regen_display_full`** - Show 100% completion messages (default: True)

### HOOKS AVAILABLE
- **`vitality_pre_damage`** - Before damage is applied
- **`vitality_post_damage`** - After damage is applied
- **`vitality_pre_healing`** - Before healing is applied
- **`vitality_post_healing`** - After healing is applied
- **`vitality_stat_change`** - When any vitality stat changes
- **`vitality_death`** - When a character dies
- **`vitality_revival`** - When a character is revived

### TECHNICAL DETAILS
- Uses proper NakedMud `hooks.run()` instead of custom hook system
- Room comparison uses `str(ch.room)` not `ch.room.vnum`
- User privilege checking uses `ch.isInGroup()` not `ch.isName()`
- Target finding uses `mud.generic_find()` with "all", "immediate" parameters
- StorageSet saving uses direct `.write()` not `.copyFrom()`
- Message sending uses `ch.sendaround()` not `ch.send_around()`
- Python command fallthrough support with return -1 for non-applicable usage

### INSTALL NOTES
- New installations get default vitality configuration automatically
- Auto-creates `misc/vitality-config` with sensible defaults if missing
- Configuration includes comprehensive status messages for all vitality levels
- Integrates with NakedMud's auxiliary data system and heartbeat hooks
- Compatible with existing character generation and world systems
