# Vitality Regeneration System - Complete

## ✅ What's Implemented

### Core Regeneration Functions
- **HP Regeneration**: (stamina × 0.1) + (discipline × 0.05) per tick
- **SP Regeneration**: (intelligence × 0.15) + (wisdom × 0.1) per tick  
- **EP Regeneration**: (stamina × 0.12) + (discipline × 0.08) per tick

### Position Modifiers
- **Sleeping**: 200% regeneration rate
- **Resting**: 150% regeneration rate
- **Sitting**: 120% regeneration rate
- **Standing**: 100% regeneration rate (baseline)
- **Fighting**: 50% regeneration rate
- **Dead**: 0% regeneration rate

### Integration
- Hooks into MUD pulse system (every 10 seconds)
- Respects character position automatically
- Checks for death status
- Includes hooks for future systems (status effects, buffs, injuries)

### Commands
- `stats` - Now shows regeneration rates per tick
- `regeninfo [target]` - Detailed regeneration breakdown (admin/debug)

## 📊 Example Output

**Character Stats with Regen:**
```
╔═══════════════════════════════════════════════════════════╗
║              Character Statistics - TestChar              ║
╠═══════════════════════════════════════════════════════════╣
║                    Vitality Pools                         ║
╟───────────────────────────────────────────────────────────╢
║  Health:    87/  100   ( 87.0%) +2.5/tick                ║
║  Spell:     45/   50   ( 90.0%) +3.2/tick                ║
║  Energy:    72/   85   ( 84.7%) +2.8/tick                ║
╟───────────────────────────────────────────────────────────╢
```

**Regeneration Info:**
```
┌─────────────────────────────────────────┐
│        Regeneration Information         │
├─────────────────────────────────────────┤
│ Position: resting         (150%)        │
├─────────────────────────────────────────┤
│ Base HP Regen:    2.50/tick             │
│ Base SP Regen:    3.20/tick             │
│ Base EP Regen:    2.80/tick             │
├─────────────────────────────────────────┤
│ Actual HP Regen:  3.75/tick             │
│ Actual SP Regen:  4.80/tick             │
│ Actual EP Regen:  4.20/tick             │
└─────────────────────────────────────────┘
```

## 🔧 Technical Details

### Pulse System Integration
- Uses NakedMud's hook system (`hooks.add("pulse", pulse_hook)`)
- Automatically processes all active player characters
- Runs every 10 seconds (configurable via `REGEN_TICK_RATE`)
- Error handling prevents crashes

### Hook Points for Future Systems
```python
# Called after regeneration occurs
hooks.run("vitality_regenerated", hooks.build_info("ch dbl dbl dbl", 
          (ch, hp_gained, sp_gained, ep_gained)))
```

### Placeholder TODOs Ready
- Guild-based regeneration modifiers
- Equipment bonuses to regen
- Status effect modifiers (bleeding reduces regen, etc.)
- Meditation/concentration bonuses for SP
- Environmental factors (temperature, poison, etc.)

## 🎯 Files Modified

**New File:**
- `lib/pymodules/vitality/vitality_regen.py`

**Updated Files:**
- `lib/pymodules/vitality/__init__.py` - Registers regeneration
- `lib/pymodules/attributes/commands.py` - Enhanced stats display

## 🧪 Testing Commands

```python
# Check your regen rates
stats

# See detailed breakdown
regeninfo

# Test position changes
rest    # Should see regen rate increase in stats
stand   # Should see regen rate decrease
sleep   # Highest regen rate (200%)
```

## ⚙️ Configuration

To adjust regeneration parameters, edit `vitality_regen.py`:

```python
# Regeneration tick rate
REGEN_TICK_RATE = 10  # seconds

# Position modifiers
POSITION_MODIFIERS = {
    "sleeping": 2.0,   # Adjust multipliers here
    "resting": 1.5,
    # ... etc
}

# Base formulas in calculate_*_regen_rate() functions
```

## 🚀 Next Steps

Vitality system is now **COMPLETE** including:
- ✅ HP/SP/EP calculations from attributes
- ✅ Damage and healing functions
- ✅ Proportional recalculation when attributes change
- ✅ Color-coded display
- ✅ Position-based regeneration
- ✅ Integration with pulse system

**Ready to build:**
1. **Combat System** - Use vitality for damage/death
2. **Death System** - Hook into HP=0 event
3. **Injury System** - Body part damage tracking
4. **Skills System** - Use attributes for modifiers
5. **Experience Pools** - Foundation for progression

---

## 💾 Backup Files

Before proceeding, backup:
- `lib/pymodules/vitality/` (entire directory)
- `lib/pymodules/attributes/commands.py`
