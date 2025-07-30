---
title: Scripting Best Practices
layout: default
nav_order: 5
parent: Core Concepts
description: "Guidelines for writing effective and safe NakedMud Python scripts"
---

# Scripting Best Practices

Writing effective NakedMud scripts requires understanding not just the API, but also the patterns and practices that lead to maintainable, performant, and secure code. This guide covers essential best practices for Python scripting in NakedMud.

## Code Organization Principles

### Single Responsibility Principle

Each script should have one clear, focused purpose:

```python
# Good: Focused on greeting behavior
def greet_player(ch, visitor):
    """Handle player greeting interactions."""
    if visitor.isPlayer():
        ch.send(f"Welcome, {visitor.name}!")
        visitor.send(f"{ch.name} greets you warmly.")

# Bad: Mixed responsibilities
def handle_player_interaction(ch, visitor):
    """Handle all player interactions."""
    # Greeting logic
    ch.send(f"Welcome, {visitor.name}!")
    # Combat logic
    if visitor.isHostile():
        ch.attack(visitor)
    # Trading logic
    if visitor.hasGold():
        ch.trade(visitor)
    # Too many responsibilities!
```

### Modular Design

Break complex functionality into smaller, reusable components:

```python
# Good: Modular approach
def validate_target(ch, target_name):
    """Validate and return target character."""
    if not target_name:
        ch.send("Target whom?")
        return None
    
    target = ch.room.get_char(target_name)
    if not target:
        ch.send("They aren't here.")
        return None
    
    return target

def perform_heal(healer, target, amount):
    """Perform healing action."""
    target.hp = min(target.hp + amount, target.max_hp)
    healer.send(f"You heal {target.name} for {amount} points.")
    target.send(f"{healer.name} heals you for {amount} points.")

def cmd_heal(ch, cmd, arg):
    """Heal command implementation."""
    target = validate_target(ch, arg)
    if target:
        perform_heal(ch, target, 50)
```

### Clear Naming Conventions

Use descriptive names that clearly indicate purpose:

```python
# Good: Clear, descriptive names
def calculate_spell_damage(caster_level, spell_power, target_resistance):
    base_damage = caster_level * spell_power
    resistance_factor = max(0.1, 1.0 - (target_resistance / 100.0))
    return int(base_damage * resistance_factor)

# Bad: Unclear, abbreviated names
def calc_dmg(lvl, pwr, res):
    bd = lvl * pwr
    rf = max(0.1, 1.0 - (res / 100.0))
    return int(bd * rf)
```

## Error Handling Strategies

### Defensive Programming

Always validate inputs and handle edge cases:

```python
def transfer_item(from_char, to_char, item_name):
    """Safely transfer an item between characters."""
    # Validate inputs
    if not from_char or not to_char:
        return False, "Invalid characters"
    
    if not item_name:
        return False, "No item specified"
    
    # Find the item
    item = from_char.get_obj(item_name)
    if not item:
        return False, f"{from_char.name} doesn't have {item_name}"
    
    # Check if transfer is allowed
    if item.no_drop:
        return False, f"{item.name} cannot be dropped"
    
    # Perform transfer
    try:
        item.to_char(to_char)
        return True, f"Transferred {item.name}"
    except Exception as e:
        return False, f"Transfer failed: {e}"
```

### Graceful Degradation

When something goes wrong, fail gracefully rather than breaking:

```python
def load_npc_equipment(npc, equipment_list):
    """Load equipment for an NPC, continuing even if some items fail."""
    loaded_items = []
    failed_items = []
    
    for item_key in equipment_list:
        try:
            item = load_obj(item_key)
            item.to_char(npc)
            loaded_items.append(item_key)
        except Exception as e:
            failed_items.append((item_key, str(e)))
            # Continue loading other items
    
    # Log failures but don't stop the process
    if failed_items:
        for item_key, error in failed_items:
            mud.log_string(f"Failed to load {item_key} for {npc.name}: {error}")
    
    return loaded_items, failed_items
```

### Comprehensive Error Messages

Provide helpful error messages for debugging:

```python
def cast_spell(caster, spell_name, target=None):
    """Cast a spell with comprehensive error reporting."""
    try:
        # Validate caster
        if not caster.canCast():
            return f"Error: {caster.name} cannot cast spells (silenced/stunned/etc.)"
        
        # Validate spell
        spell = caster.getSpell(spell_name)
        if not spell:
            return f"Error: {caster.name} doesn't know spell '{spell_name}'"
        
        # Validate mana
        if caster.mana < spell.cost:
            return f"Error: {caster.name} needs {spell.cost} mana but only has {caster.mana}"
        
        # Validate target if required
        if spell.requires_target and not target:
            return f"Error: Spell '{spell_name}' requires a target"
        
        # Cast the spell
        spell.cast(caster, target)
        return f"Success: {caster.name} casts {spell_name}"
        
    except Exception as e:
        return f"Error: Spell casting failed - {e}"
```

## Performance Optimization

### Efficient Data Access

Minimize expensive operations and cache results when appropriate:

```python
# Good: Cache expensive lookups
class RoomManager:
    def __init__(self):
        self._room_cache = {}
    
    def get_room(self, room_key):
        if room_key not in self._room_cache:
            self._room_cache[room_key] = load_room(room_key)
        return self._room_cache[room_key]

# Bad: Repeated expensive operations
def find_all_players_in_zone(zone_name):
    players = []
    for room_key in get_zone_rooms(zone_name):  # Expensive
        room = load_room(room_key)              # Expensive
        for ch in room.chars:
            if ch.isPlayer():
                players.append(ch)
    return players
```

### Lazy Evaluation

Defer expensive operations until they're actually needed:

```python
class QuestData:
    def __init__(self):
        self._objectives = None
        self._rewards = None
    
    @property
    def objectives(self):
        """Load objectives only when accessed."""
        if self._objectives is None:
            self._objectives = self._load_objectives()
        return self._objectives
    
    @property
    def rewards(self):
        """Load rewards only when accessed."""
        if self._rewards is None:
            self._rewards = self._load_rewards()
        return self._rewards
```

### Batch Operations

Group related operations together to reduce overhead:

```python
# Good: Batch operations
def update_player_stats(players, stat_changes):
    """Update multiple players' stats in a batch."""
    for player in players:
        # Apply all changes at once
        for stat, change in stat_changes.items():
            current = getattr(player, stat)
            setattr(player, stat, current + change)
        
        # Send one update message
        player.send("Your stats have been updated.")

# Bad: Individual operations
def update_player_stat(player, stat, change):
    """Update one stat for one player."""
    current = getattr(player, stat)
    setattr(player, stat, current + change)
    player.send(f"Your {stat} has changed by {change}.")
```

## Security Considerations

### Input Validation

Always validate and sanitize user input:

```python
def set_player_description(ch, new_desc):
    """Set player description with validation."""
    # Check length
    if len(new_desc) > 1000:
        ch.send("Description too long (max 1000 characters).")
        return False
    
    # Check for forbidden content
    forbidden_words = ["admin", "wizard", "god"]
    desc_lower = new_desc.lower()
    for word in forbidden_words:
        if word in desc_lower:
            ch.send(f"Description cannot contain '{word}'.")
            return False
    
    # Sanitize HTML/special characters
    clean_desc = sanitize_text(new_desc)
    
    ch.desc = clean_desc
    ch.send("Description updated.")
    return True
```

### Resource Management

Prevent resource exhaustion and abuse:

```python
def create_objects_for_player(ch, object_type, count):
    """Create objects with resource limits."""
    # Enforce reasonable limits
    max_objects = 50
    if count > max_objects:
        ch.send(f"Cannot create more than {max_objects} objects at once.")
        return
    
    # Check player's carrying capacity
    if len(ch.inv) + count > ch.max_carry:
        ch.send("You cannot carry that many items.")
        return
    
    # Create objects with error handling
    created = 0
    for i in range(count):
        try:
            obj = load_obj(object_type)
            obj.to_char(ch)
            created += 1
        except Exception as e:
            mud.log_string(f"Failed to create object {i}: {e}")
            break
    
    ch.send(f"Created {created} objects.")
```

### Safe External Data Handling

When working with external data, be extra cautious:

```python
def load_player_data(player_name):
    """Load player data with safety checks."""
    # Validate player name format
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,15}$', player_name):
        raise ValueError("Invalid player name format")
    
    # Construct safe file path
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '', player_name)
    data_file = f"players/{safe_name}.dat"
    
    # Check file exists and is readable
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Player data not found: {player_name}")
    
    # Load with size limits
    max_size = 1024 * 1024  # 1MB limit
    if os.path.getsize(data_file) > max_size:
        raise ValueError("Player data file too large")
    
    # Parse safely
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        return validate_player_data(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid player data format: {e}")
```

## Testing and Debugging

### Comprehensive Testing

Write testable code and test thoroughly:

```python
def calculate_experience_gain(player_level, monster_level, base_exp):
    """Calculate experience gain with level differences."""
    level_diff = monster_level - player_level
    
    # Level difference modifiers
    if level_diff > 10:
        modifier = 0.1  # Very low exp for easy monsters
    elif level_diff > 5:
        modifier = 0.5
    elif level_diff >= -5:
        modifier = 1.0  # Normal exp
    elif level_diff >= -10:
        modifier = 1.5  # Bonus for harder monsters
    else:
        modifier = 2.0  # High bonus for very hard monsters
    
    return int(base_exp * modifier)

# Test function
def test_experience_calculation():
    """Test experience calculation function."""
    # Test normal case
    assert calculate_experience_gain(10, 10, 100) == 100
    
    # Test easy monster
    assert calculate_experience_gain(20, 5, 100) == 10
    
    # Test hard monster
    assert calculate_experience_gain(10, 25, 100) == 200
    
    print("All experience calculation tests passed!")
```

### Debug-Friendly Code

Write code that's easy to debug:

```python
def process_combat_round(attacker, defender):
    """Process one round of combat with debug information."""
    debug = True  # Toggle for debug output
    
    if debug:
        mud.log_string(f"Combat: {attacker.name} vs {defender.name}")
        mud.log_string(f"Attacker HP: {attacker.hp}/{attacker.max_hp}")
        mud.log_string(f"Defender HP: {defender.hp}/{defender.max_hp}")
    
    # Calculate attack
    attack_roll = random.randint(1, 20) + attacker.attack_bonus
    defense_roll = random.randint(1, 20) + defender.defense_bonus
    
    if debug:
        mud.log_string(f"Attack roll: {attack_roll}, Defense roll: {defense_roll}")
    
    if attack_roll > defense_roll:
        damage = calculate_damage(attacker, defender)
        defender.hp -= damage
        
        if debug:
            mud.log_string(f"Hit for {damage} damage!")
        
        return f"{attacker.name} hits {defender.name} for {damage} damage!"
    else:
        if debug:
            mud.log_string("Attack missed!")
        
        return f"{attacker.name} misses {defender.name}!"
```

## Documentation Standards

### Function Documentation

Document all functions with clear docstrings:

```python
def transfer_gold(from_char, to_char, amount):
    """
    Transfer gold between two characters.
    
    Args:
        from_char (PyChar): Character giving gold
        to_char (PyChar): Character receiving gold
        amount (int): Amount of gold to transfer
    
    Returns:
        tuple: (success: bool, message: str)
            success: True if transfer completed successfully
            message: Description of what happened
    
    Raises:
        ValueError: If amount is negative or zero
        TypeError: If characters are not PyChar objects
    
    Example:
        success, msg = transfer_gold(player, merchant, 100)
        if success:
            player.send(f"You give {merchant.name} 100 gold.")
        else:
            player.send(f"Transfer failed: {msg}")
    """
    # Validate inputs
    if not isinstance(from_char, PyChar) or not isinstance(to_char, PyChar):
        raise TypeError("Both characters must be PyChar objects")
    
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    # Check if sender has enough gold
    if from_char.gold < amount:
        return False, f"{from_char.name} doesn't have {amount} gold"
    
    # Perform transfer
    from_char.gold -= amount
    to_char.gold += amount
    
    return True, f"Transferred {amount} gold successfully"
```

### Code Comments

Use comments to explain complex logic and design decisions:

```python
def calculate_spell_resistance(target, spell_school):
    """Calculate target's resistance to a spell school."""
    base_resistance = target.getResistance(spell_school)
    
    # Apply racial bonuses (elves resist enchantment, dwarves resist magic)
    if target.race == "elf" and spell_school == "enchantment":
        base_resistance += 25  # Elven resistance to mind effects
    elif target.race == "dwarf":
        base_resistance += 10  # Dwarven magic resistance
    
    # Equipment bonuses are multiplicative, not additive
    # This prevents stacking resistance items from making characters immune
    equipment_bonus = target.getEquipmentResistance(spell_school)
    total_resistance = base_resistance * (1 + equipment_bonus / 100)
    
    # Cap resistance at 95% to ensure spells always have some chance
    return min(total_resistance, 95)
```

## Common Patterns and Idioms

### The Guard Pattern

Use early returns to reduce nesting:

```python
# Good: Guard pattern
def process_player_command(ch, cmd, arg):
    """Process a player command with guard clauses."""
    # Guard clauses handle edge cases early
    if not ch.isPlayer():
        return  # NPCs can't use this command
    
    if ch.isAsleep():
        ch.send("You can't do that while sleeping.")
        return
    
    if not arg:
        ch.send("Usage: command <argument>")
        return
    
    # Main logic only runs if all conditions are met
    process_command_logic(ch, cmd, arg)

# Bad: Nested conditions
def process_player_command_bad(ch, cmd, arg):
    """Process a player command with nested conditions."""
    if ch.isPlayer():
        if not ch.isAsleep():
            if arg:
                process_command_logic(ch, cmd, arg)
            else:
                ch.send("Usage: command <argument>")
        else:
            ch.send("You can't do that while sleeping.")
    # NPCs silently ignored
```

### The Factory Pattern

Use factory functions for complex object creation:

```python
def create_weapon(weapon_type, quality="normal", enchantment=None):
    """Factory function for creating weapons."""
    # Base weapon creation
    if weapon_type == "sword":
        weapon = load_obj("base_sword@weapons")
    elif weapon_type == "axe":
        weapon = load_obj("base_axe@weapons")
    else:
        raise ValueError(f"Unknown weapon type: {weapon_type}")
    
    # Apply quality modifications
    quality_mods = {
        "poor": {"damage": 0.8, "value": 0.5},
        "normal": {"damage": 1.0, "value": 1.0},
        "fine": {"damage": 1.2, "value": 2.0},
        "masterwork": {"damage": 1.5, "value": 5.0}
    }
    
    if quality in quality_mods:
        mods = quality_mods[quality]
        weapon.damage = int(weapon.damage * mods["damage"])
        weapon.value = int(weapon.value * mods["value"])
        weapon.name = f"{quality} {weapon.name}"
    
    # Apply enchantments
    if enchantment:
        apply_enchantment(weapon, enchantment)
    
    return weapon
```

### The Observer Pattern

Use events and triggers for loose coupling:

```python
# Event system for decoupled notifications
class EventManager:
    def __init__(self):
        self.listeners = {}
    
    def register(self, event_type, callback):
        """Register a callback for an event type."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def trigger(self, event_type, *args, **kwargs):
        """Trigger all callbacks for an event type."""
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    mud.log_string(f"Event callback error: {e}")

# Usage example
events = EventManager()

# Register listeners
events.register("player_death", update_death_statistics)
events.register("player_death", create_corpse)
events.register("player_death", notify_guild_members)

# Trigger event
def handle_player_death(player):
    events.trigger("player_death", player)
```

## See Also

- [Security Model](security-model.md) - Understanding script security
- [Python Integration Overview](python-integration.md) - How C and Python interact
- [API Reference](../reference/) - Complete function documentation
- [Examples](../examples/) - Working code samples