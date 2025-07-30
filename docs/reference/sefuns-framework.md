---
layout: default
title: SEFuns Framework
parent: API Reference
nav_order: 5
---

# SEFuns Framework Documentation

This document provides a comprehensive framework for expanding the System External Functions (SEFuns) in NakedMud. It outlines patterns, best practices, and implementation strategies for creating new Python-based global functions that extend the MUD's functionality.

## Framework Overview

The SEFuns framework is designed to provide:
- **Extensibility**: Easy addition of new global functions
- **Modularity**: Clean separation of concerns
- **Integration**: Seamless integration with existing systems
- **Performance**: Efficient execution and memory usage
- **Maintainability**: Clear code organization and documentation

## Core Framework Patterns

### 1. Global Function Registration Pattern

This pattern allows modules to register functions globally for system-wide access.

```python
# framework/global_registry.py

class GlobalFunctionRegistry:
    """Central registry for global functions"""
    
    def __init__(self):
        self._functions = {}
        self._categories = {}
    
    def register(self, name, function, category="general", description=""):
        """Register a global function"""
        if name in self._functions:
            raise ValueError(f"Function {name} already registered")
        
        self._functions[name] = {
            'function': function,
            'category': category,
            'description': description,
            'module': function.__module__
        }
        
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)
    
    def unregister(self, name):
        """Unregister a global function"""
        if name in self._functions:
            category = self._functions[name]['category']
            self._categories[category].remove(name)
            del self._functions[name]
    
    def get_function(self, name):
        """Get a registered function"""
        return self._functions.get(name, {}).get('function')
    
    def list_functions(self, category=None):
        """List all functions or functions in a category"""
        if category:
            return self._categories.get(category, [])
        return list(self._functions.keys())
    
    def get_info(self, name):
        """Get information about a function"""
        return self._functions.get(name, {})

# Global instance
global_functions = GlobalFunctionRegistry()

# Convenience functions
def register_global_function(name, function, category="general", description=""):
    """Register a function globally"""
    global_functions.register(name, function, category, description)

def get_global_function(name):
    """Get a global function"""
    return global_functions.get_function(name)

# Usage example:
def calculate_damage(attacker, defender, weapon=None):
    """Calculate combat damage"""
    base_damage = 10
    # Complex damage calculation logic here
    return base_damage

register_global_function(
    "calculate_damage", 
    calculate_damage, 
    "combat", 
    "Calculate damage for combat encounters"
)
```

### 2. Event Handler Registration Pattern

This pattern provides a framework for registering event handlers that respond to game events.

```python
# framework/event_handlers.py

class EventHandlerRegistry:
    """Registry for event handlers"""
    
    def __init__(self):
        self._handlers = {}
        self._priorities = {}
    
    def register_handler(self, event_type, handler, priority=100):
        """Register an event handler with priority"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
            self._priorities[event_type] = []
        
        # Insert handler in priority order (lower numbers = higher priority)
        inserted = False
        for i, existing_priority in enumerate(self._priorities[event_type]):
            if priority < existing_priority:
                self._handlers[event_type].insert(i, handler)
                self._priorities[event_type].insert(i, priority)
                inserted = True
                break
        
        if not inserted:
            self._handlers[event_type].append(handler)
            self._priorities[event_type].append(priority)
    
    def unregister_handler(self, event_type, handler):
        """Unregister an event handler"""
        if event_type in self._handlers:
            try:
                index = self._handlers[event_type].index(handler)
                self._handlers[event_type].pop(index)
                self._priorities[event_type].pop(index)
            except ValueError:
                pass  # Handler not found
    
    def process_event(self, event_type, event_data):
        """Process an event through all registered handlers"""
        if event_type not in self._handlers:
            return []
        
        results = []
        for handler in self._handlers[event_type]:
            try:
                result = handler(event_data)
                results.append(result)
                
                # If handler returns False, stop processing
                if result is False:
                    break
                    
            except Exception as e:
                import mud
                mud.log_string(f"Error in event handler: {str(e)}")
        
        return results
    
    def list_handlers(self, event_type=None):
        """List handlers for an event type or all handlers"""
        if event_type:
            return self._handlers.get(event_type, [])
        return dict(self._handlers)

# Global instance
event_handlers = EventHandlerRegistry()

# Convenience functions
def register_event_handler(event_type, handler, priority=100):
    """Register an event handler"""
    event_handlers.register_handler(event_type, handler, priority)

def process_game_event(event_type, event_data):
    """Process a game event"""
    return event_handlers.process_event(event_type, event_data)

# Usage example:
def handle_player_death(event_data):
    """Handle player death events"""
    character = event_data.get('character')
    if character:
        # Death penalty logic
        character.setvar('death_count', character.getvar('death_count') + 1)
        character.send("You have died! Your death count is now {}.".format(
            character.getvar('death_count')
        ))
    return True

register_event_handler('player_death', handle_player_death, priority=50)
```

### 3. Validation Framework Pattern

This pattern provides a flexible system for validating actions and states.

```python
# framework/validation.py

class ValidationFramework:
    """Framework for action and state validation"""
    
    def __init__(self):
        self._validators = {}
        self._global_validators = []
    
    def register_validator(self, action_type, validator, description=""):
        """Register a validator for a specific action type"""
        if action_type not in self._validators:
            self._validators[action_type] = []
        
        self._validators[action_type].append({
            'validator': validator,
            'description': description
        })
    
    def register_global_validator(self, validator, description=""):
        """Register a validator that applies to all actions"""
        self._global_validators.append({
            'validator': validator,
            'description': description
        })
    
    def validate(self, action_type, context):
        """Validate an action with context"""
        errors = []
        
        # Run global validators first
        for validator_info in self._global_validators:
            try:
                result = validator_info['validator'](action_type, context)
                if result is not True:
                    if isinstance(result, str):
                        errors.append(result)
                    else:
                        errors.append(f"Global validation failed: {validator_info['description']}")
            except Exception as e:
                errors.append(f"Validator error: {str(e)}")
        
        # Run specific validators
        if action_type in self._validators:
            for validator_info in self._validators[action_type]:
                try:
                    result = validator_info['validator'](context)
                    if result is not True:
                        if isinstance(result, str):
                            errors.append(result)
                        else:
                            errors.append(f"Validation failed: {validator_info['description']}")
                except Exception as e:
                    errors.append(f"Validator error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def list_validators(self, action_type=None):
        """List validators"""
        if action_type:
            return self._validators.get(action_type, [])
        return {
            'global': self._global_validators,
            'specific': dict(self._validators)
        }

# Global instance
validation_framework = ValidationFramework()

# Convenience functions
def register_action_validator(action_type, validator, description=""):
    """Register a validator for an action type"""
    validation_framework.register_validator(action_type, validator, description)

def register_global_validator(validator, description=""):
    """Register a global validator"""
    validation_framework.register_global_validator(validator, description)

def validate_action(action_type, context):
    """Validate an action"""
    return validation_framework.validate(action_type, context)

# Usage examples:
def validate_character_alive(context):
    """Ensure character is alive"""
    character = context.get('character')
    if character and hasattr(character, 'is_dead') and character.is_dead():
        return "You cannot do that while dead."
    return True

def validate_combat_action(context):
    """Validate combat-specific actions"""
    character = context.get('character')
    if character and not character.getvar('in_combat'):
        return "You must be in combat to perform this action."
    return True

register_global_validator(validate_character_alive, "Character must be alive")
register_action_validator('attack', validate_combat_action, "Must be in combat to attack")
```

### 4. Configuration Management Pattern

This pattern provides a centralized configuration system for SEFuns.

```python
# framework/config.py

class ConfigurationManager:
    """Centralized configuration management"""
    
    def __init__(self):
        self._config = {}
        self._defaults = {}
        self._validators = {}
        self._change_handlers = {}
    
    def register_setting(self, key, default_value, validator=None, description=""):
        """Register a configuration setting"""
        self._defaults[key] = default_value
        self._config[key] = default_value
        
        if validator:
            self._validators[key] = validator
        
        # Store metadata
        if not hasattr(self, '_metadata'):
            self._metadata = {}
        self._metadata[key] = {
            'description': description,
            'default': default_value,
            'type': type(default_value).__name__
        }
    
    def set(self, key, value):
        """Set a configuration value"""
        if key not in self._defaults:
            raise KeyError(f"Unknown configuration key: {key}")
        
        # Validate the value
        if key in self._validators:
            if not self._validators[key](value):
                raise ValueError(f"Invalid value for {key}: {value}")
        
        old_value = self._config.get(key)
        self._config[key] = value
        
        # Notify change handlers
        if key in self._change_handlers:
            for handler in self._change_handlers[key]:
                try:
                    handler(key, old_value, value)
                except Exception as e:
                    import mud
                    mud.log_string(f"Error in config change handler: {str(e)}")
    
    def get(self, key, default=None):
        """Get a configuration value"""
        return self._config.get(key, default)
    
    def reset(self, key):
        """Reset a setting to its default value"""
        if key in self._defaults:
            self.set(key, self._defaults[key])
    
    def register_change_handler(self, key, handler):
        """Register a handler for configuration changes"""
        if key not in self._change_handlers:
            self._change_handlers[key] = []
        self._change_handlers[key].append(handler)
    
    def list_settings(self):
        """List all configuration settings"""
        return dict(self._config)
    
    def get_metadata(self, key=None):
        """Get metadata about settings"""
        if key:
            return getattr(self, '_metadata', {}).get(key, {})
        return getattr(self, '_metadata', {})

# Global instance
config = ConfigurationManager()

# Convenience functions
def register_config_setting(key, default_value, validator=None, description=""):
    """Register a configuration setting"""
    config.register_setting(key, default_value, validator, description)

def get_config(key, default=None):
    """Get a configuration value"""
    return config.get(key, default)

def set_config(key, value):
    """Set a configuration value"""
    config.set(key, value)

# Usage examples:
def validate_positive_integer(value):
    """Validate that value is a positive integer"""
    return isinstance(value, int) and value > 0

def validate_percentage(value):
    """Validate that value is between 0 and 100"""
    return isinstance(value, (int, float)) and 0 <= value <= 100

register_config_setting(
    'combat.base_damage', 
    10, 
    validate_positive_integer,
    "Base damage for combat calculations"
)

register_config_setting(
    'economy.tax_rate',
    5.0,
    validate_percentage,
    "Tax rate for transactions (percentage)"
)

# Usage in other modules:
base_damage = get_config('combat.base_damage', 10)
tax_rate = get_config('economy.tax_rate', 5.0)
```

## Specialized SEFun Categories

### Combat System SEFuns

```python
# sefuns/combat.py

import random
from framework.global_registry import register_global_function
from framework.config import get_config

def calculate_hit_chance(attacker, defender, weapon=None):
    """Calculate the chance to hit in combat"""
    base_chance = get_config('combat.base_hit_chance', 75)
    
    # Factor in attacker skill
    attacker_skill = attacker.get_skill_level('combat') if hasattr(attacker, 'get_skill_level') else 50
    
    # Factor in defender agility
    defender_agility = defender.getvar('agility') or 50
    
    # Weapon accuracy bonus
    weapon_bonus = 0
    if weapon and hasattr(weapon, 'getvar'):
        weapon_bonus = weapon.getvar('accuracy_bonus') or 0
    
    # Calculate final chance
    hit_chance = base_chance + (attacker_skill - defender_agility) + weapon_bonus
    
    # Clamp between 5% and 95%
    return max(5, min(95, hit_chance))

def calculate_damage(attacker, defender, weapon=None):
    """Calculate damage for an attack"""
    base_damage = get_config('combat.base_damage', 10)
    
    # Factor in attacker strength
    strength_bonus = (attacker.getvar('strength') or 50) - 50
    
    # Weapon damage
    weapon_damage = 0
    if weapon and hasattr(weapon, 'getvar'):
        weapon_damage = weapon.getvar('damage') or 0
    
    # Random variance
    variance = random.randint(-2, 2)
    
    total_damage = base_damage + strength_bonus + weapon_damage + variance
    
    # Minimum damage of 1
    return max(1, total_damage)

def apply_combat_effects(attacker, defender, damage_dealt):
    """Apply effects after combat damage"""
    # Experience gain for attacker
    if hasattr(attacker, 'improve_skill'):
        attacker.improve_skill('combat', 1)
    
    # Check for special weapon effects
    weapon = None
    if hasattr(attacker, 'get_equip'):
        weapon = attacker.get_equip('right_hand')
    
    if weapon and weapon.getvar('poison_chance'):
        poison_chance = weapon.getvar('poison_chance')
        if random.randint(1, 100) <= poison_chance:
            defender.setvar('poisoned', 1)
            defender.send("You feel sick from the poisoned weapon!")

# Register combat SEFuns
register_global_function('calculate_hit_chance', calculate_hit_chance, 'combat')
register_global_function('calculate_damage', calculate_damage, 'combat')
register_global_function('apply_combat_effects', apply_combat_effects, 'combat')
```

### Economy System SEFuns

```python
# sefuns/economy.py

from framework.global_registry import register_global_function
from framework.config import get_config

def calculate_item_value(item):
    """Calculate the value of an item"""
    base_value = item.getvar('base_value') or 10
    
    # Factor in item condition
    condition = item.getvar('condition') or 100
    condition_multiplier = condition / 100.0
    
    # Factor in rarity
    rarity_multiplier = {
        'common': 1.0,
        'uncommon': 1.5,
        'rare': 2.5,
        'epic': 5.0,
        'legendary': 10.0
    }.get(item.getvar('rarity') or 'common', 1.0)
    
    # Market demand (could be dynamic)
    demand_multiplier = get_market_demand(item.prototypes.split(',')[0])
    
    final_value = int(base_value * condition_multiplier * rarity_multiplier * demand_multiplier)
    return max(1, final_value)

def get_market_demand(item_type):
    """Get current market demand for an item type"""
    # This could be dynamic based on player actions
    demand_data = get_config('economy.market_demand', {})
    return demand_data.get(item_type, 1.0)

def calculate_shop_price(item, shop_type='general'):
    """Calculate shop selling price"""
    base_value = calculate_item_value(item)
    
    # Shop markup
    markup_rates = {
        'general': 1.5,
        'weapon': 1.8,
        'armor': 1.8,
        'magic': 2.5,
        'luxury': 3.0
    }
    
    markup = markup_rates.get(shop_type, 1.5)
    shop_price = int(base_value * markup)
    
    return shop_price

def calculate_tax(amount, transaction_type='sale'):
    """Calculate tax on a transaction"""
    tax_rates = {
        'sale': get_config('economy.sales_tax', 5.0),
        'trade': get_config('economy.trade_tax', 2.0),
        'auction': get_config('economy.auction_tax', 10.0)
    }
    
    tax_rate = tax_rates.get(transaction_type, 5.0) / 100.0
    return int(amount * tax_rate)

# Register economy SEFuns
register_global_function('calculate_item_value', calculate_item_value, 'economy')
register_global_function('get_market_demand', get_market_demand, 'economy')
register_global_function('calculate_shop_price', calculate_shop_price, 'economy')
register_global_function('calculate_tax', calculate_tax, 'economy')
```

### Social System SEFuns

```python
# sefuns/social.py

from framework.global_registry import register_global_function
from framework.event_handlers import register_event_handler

def get_relationship_level(character1, character2):
    """Get relationship level between two characters"""
    if not character1 or not character2:
        return 'neutral'
    
    # Get relationship data
    relationships = character1.aux('relationships')
    if not relationships:
        return 'neutral'
    
    char2_id = str(character2.uid)
    return getattr(relationships, char2_id, 'neutral')

def modify_relationship(character1, character2, change):
    """Modify relationship between characters"""
    if not character1 or not character2:
        return False
    
    # Ensure relationship data exists
    relationships = character1.aux('relationships')
    if not relationships:
        return False
    
    char2_id = str(character2.uid)
    current_level = getattr(relationships, char2_id, 0)
    
    # Relationship levels: -100 (enemy) to 100 (ally)
    new_level = max(-100, min(100, current_level + change))
    setattr(relationships, char2_id, new_level)
    
    # Determine relationship category
    if new_level >= 75:
        category = 'ally'
    elif new_level >= 25:
        category = 'friend'
    elif new_level >= -25:
        category = 'neutral'
    elif new_level >= -75:
        category = 'dislike'
    else:
        category = 'enemy'
    
    return category

def can_perform_social_action(actor, target, action):
    """Check if a social action is allowed"""
    if not actor or not target:
        return False, "Invalid characters"
    
    # Check relationship requirements
    relationship = get_relationship_level(actor, target)
    
    action_requirements = {
        'hug': ['friend', 'ally'],
        'kiss': ['ally'],
        'slap': ['dislike', 'enemy'],
        'insult': ['dislike', 'enemy'],
        'compliment': ['neutral', 'friend', 'ally']
    }
    
    if action in action_requirements:
        if relationship not in action_requirements[action]:
            return False, f"Your relationship with {target.name} doesn't allow that action"
    
    return True, ""

def process_social_interaction(actor, target, action):
    """Process a social interaction between characters"""
    # Validate the action
    can_do, reason = can_perform_social_action(actor, target, action)
    if not can_do:
        return False, reason
    
    # Apply relationship changes
    relationship_changes = {
        'compliment': 2,
        'hug': 3,
        'kiss': 5,
        'insult': -3,
        'slap': -5
    }
    
    if action in relationship_changes:
        change = relationship_changes[action]
        new_category = modify_relationship(actor, target, change)
        
        # Also modify target's relationship with actor (usually less)
        reverse_change = int(change * 0.7)
        modify_relationship(target, actor, reverse_change)
    
    return True, f"Social action '{action}' completed"

# Register social SEFuns
register_global_function('get_relationship_level', get_relationship_level, 'social')
register_global_function('modify_relationship', modify_relationship, 'social')
register_global_function('can_perform_social_action', can_perform_social_action, 'social')
register_global_function('process_social_interaction', process_social_interaction, 'social')
```

## Integration Patterns

### Hook System Integration

```python
# integration/hooks.py

import hooks
from framework.event_handlers import process_game_event

def integrate_sefuns_with_hooks():
    """Integrate SEFuns with the existing hook system"""
    
    def combat_hook_handler(info):
        """Handle combat hooks through SEFun event system"""
        parsed = hooks.parse_info(info)
        attacker, defender = parsed[0], parsed[1]
        
        event_data = {
            'attacker': attacker,
            'defender': defender,
            'hook_info': info
        }
        
        # Process through SEFun event system
        results = process_game_event('combat_hit', event_data)
        return any(results)  # Return True if any handler succeeded
    
    def player_login_handler(info):
        """Handle player login through SEFun event system"""
        parsed = hooks.parse_info(info)
        character = parsed[0]
        
        event_data = {
            'character': character,
            'hook_info': info
        }
        
        process_game_event('player_login', event_data)
    
    # Register with existing hook system
    hooks.add('combat_hit', combat_hook_handler)
    hooks.add('player_login', player_login_handler)

# Call during initialization
integrate_sefuns_with_hooks()
```

### Command System Integration

```python
# integration/commands.py

import mudsys
from framework.global_registry import get_global_function
from framework.validation import validate_action

def create_sefun_command(command_name, sefun_name, user_group="player"):
    """Create a command that calls a SEFun"""
    
    def command_handler(ch, cmd, arg):
        """Generic command handler that calls a SEFun"""
        sefun = get_global_function(sefun_name)
        if not sefun:
            ch.send(f"SEFun '{sefun_name}' not found.")
            return
        
        # Validate the action
        context = {
            'character': ch,
            'command': cmd,
            'argument': arg
        }
        
        is_valid, errors = validate_action(command_name, context)
        if not is_valid:
            for error in errors:
                ch.send(error)
            return
        
        # Call the SEFun
        try:
            result = sefun(ch, arg)
            if isinstance(result, str):
                ch.send(result)
            elif result is False:
                ch.send("The action failed.")
        except Exception as e:
            ch.send(f"Error executing command: {str(e)}")
            import mud
            mud.log_string(f"Error in SEFun command {command_name}: {str(e)}")
    
    # Register the command
    mudsys.add_cmd(command_name, None, command_handler, user_group, False)

# Usage examples:
def social_command_sefun(character, argument):
    """SEFun for social commands"""
    if not argument:
        return "Usage: social <action> <target>"
    
    parts = argument.split(' ', 1)
    action = parts[0]
    target_name = parts[1] if len(parts) > 1 else ""
    
    if not target_name:
        return f"Who do you want to {action}?"
    
    # Find target
    target = None
    for ch in character.room.chars:
        if target_name.lower() in ch.name.lower():
            target = ch
            break
    
    if not target:
        return "They aren't here."
    
    # Process social interaction
    social_sefun = get_global_function('process_social_interaction')
    if social_sefun:
        success, message = social_sefun(character, target, action)
        return message
    
    return "Social system not available."

# Register the SEFun and create command
from framework.global_registry import register_global_function
register_global_function('social_command', social_command_sefun, 'social')
create_sefun_command('social', 'social_command', 'player')
```

## Testing Framework

```python
# testing/sefun_tests.py

class SEFunTestFramework:
    """Framework for testing SEFuns"""
    
    def __init__(self):
        self.test_results = []
    
    def run_test(self, test_name, test_function):
        """Run a single test"""
        try:
            result = test_function()
            if result:
                self.test_results.append((test_name, 'PASS', None))
                return True
            else:
                self.test_results.append((test_name, 'FAIL', 'Test returned False'))
                return False
        except Exception as e:
            self.test_results.append((test_name, 'ERROR', str(e)))
            return False
    
    def assert_equal(self, actual, expected, message=""):
        """Assert that two values are equal"""
        if actual != expected:
            raise AssertionError(f"Expected {expected}, got {actual}. {message}")
        return True
    
    def assert_true(self, condition, message=""):
        """Assert that condition is true"""
        if not condition:
            raise AssertionError(f"Condition was false. {message}")
        return True
    
    def run_all_tests(self):
        """Run all registered tests"""
        # Test combat SEFuns
        self.run_test("test_calculate_damage", self.test_calculate_damage)
        self.run_test("test_hit_chance", self.test_hit_chance)
        
        # Test economy SEFuns
        self.run_test("test_item_value", self.test_item_value)
        self.run_test("test_shop_price", self.test_shop_price)
        
        # Print results
        self.print_results()
    
    def test_calculate_damage(self):
        """Test damage calculation"""
        from framework.global_registry import get_global_function
        
        # Mock objects
        class MockCharacter:
            def getvar(self, name):
                return {'strength': 60}.get(name, 50)
        
        class MockWeapon:
            def getvar(self, name):
                return {'damage': 15}.get(name, 0)
        
        attacker = MockCharacter()
        defender = MockCharacter()
        weapon = MockWeapon()
        
        damage_func = get_global_function('calculate_damage')
        if not damage_func:
            return False
        
        damage = damage_func(attacker, defender, weapon)
        
        # Damage should be positive
        self.assert_true(damage > 0, "Damage should be positive")
        
        # Damage should be reasonable (base 10 + strength 10 + weapon 15 = ~35)
        self.assert_true(20 <= damage <= 50, f"Damage {damage} should be in reasonable range")
        
        return True
    
    def test_hit_chance(self):
        """Test hit chance calculation"""
        from framework.global_registry import get_global_function
        
        class MockCharacter:
            def get_skill_level(self, skill):
                return 75 if skill == 'combat' else 50
            
            def getvar(self, name):
                return {'agility': 40}.get(name, 50)
        
        attacker = MockCharacter()
        defender = MockCharacter()
        
        hit_func = get_global_function('calculate_hit_chance')
        if not hit_func:
            return False
        
        hit_chance = hit_func(attacker, defender)
        
        # Hit chance should be between 5 and 95
        self.assert_true(5 <= hit_chance <= 95, f"Hit chance {hit_chance} should be 5-95")
        
        return True
    
    def test_item_value(self):
        """Test item value calculation"""
        from framework.global_registry import get_global_function
        
        class MockItem:
            def __init__(self):
                self.prototypes = "sword,weapon"
            
            def getvar(self, name):
                return {
                    'base_value': 100,
                    'condition': 80,
                    'rarity': 'rare'
                }.get(name, None)
        
        item = MockItem()
        
        value_func = get_global_function('calculate_item_value')
        if not value_func:
            return False
        
        value = value_func(item)
        
        # Value should be positive
        self.assert_true(value > 0, "Item value should be positive")
        
        # With rare rarity and 80% condition, should be significant
        self.assert_true(value >= 100, f"Rare item value {value} should be substantial")
        
        return True
    
    def test_shop_price(self):
        """Test shop price calculation"""
        from framework.global_registry import get_global_function
        
        class MockItem:
            def __init__(self):
                self.prototypes = "sword,weapon"
            
            def getvar(self, name):
                return {
                    'base_value': 100,
                    'condition': 100,
                    'rarity': 'common'
                }.get(name, None)
        
        item = MockItem()
        
        price_func = get_global_function('calculate_shop_price')
        if not price_func:
            return False
        
        price = price_func(item, 'weapon')
        
        # Shop price should be higher than base value due to markup
        self.assert_true(price > 100, f"Shop price {price} should be higher than base value")
        
        return True
    
    def print_results(self):
        """Print test results"""
        print("\n=== SEFun Test Results ===")
        passed = 0
        failed = 0
        
        for test_name, status, error in self.test_results:
            print(f"{test_name}: {status}")
            if error:
                print(f"  Error: {error}")
            
            if status == 'PASS':
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal: {len(self.test_results)} tests")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

# Usage:
def run_sefun_tests():
    """Run all SEFun tests"""
    test_framework = SEFunTestFramework()
    test_framework.run_all_tests()

# Can be called from a command or during startup
# run_sefun_tests()
```

## Documentation Standards

### SEFun Documentation Template

```python
def example_sefun(parameter1, parameter2, optional_param=None):
    """
    Brief description of what this SEFun does.
    
    This SEFun provides functionality for [specific purpose]. It integrates
    with [relevant systems] and is commonly used for [use cases].
    
    Args:
        parameter1 (type): Description of parameter1
        parameter2 (type): Description of parameter2  
        optional_param (type, optional): Description of optional parameter.
            Defaults to None.
    
    Returns:
        type: Description of return value
    
    Raises:
        ValueError: When parameter validation fails
        RuntimeError: When system is in invalid state
    
    Examples:
        Basic usage:
        >>> result = example_sefun("value1", "value2")
        >>> print(result)
        
        With optional parameter:
        >>> result = example_sefun("value1", "value2", optional_param="custom")
        
        Error handling:
        >>> try:
        ...     result = example_sefun(None, "value2")
        ... except ValueError as e:
        ...     print(f"Error: {e}")
    
    See Also:
        related_sefun: Related functionality
        relevant_efun: Core function this builds upon
        
    Note:
        Any important notes about usage, performance, or limitations.
        
    Version:
        Added in version 1.0
        Modified in version 1.1 - Added optional_param
    """
    # Implementation here
    pass
```

## See Also

- [SEFuns (System External Functions)](sefuns.md) - Current SEFun implementation
- [EFuns (External Functions)](efuns.md) - C-derived functions
- [EObjs (External Objects)](eobjs.md) - C-defined classes
- [Core Concepts: Python Integration](../core-concepts/python-integration.md)
- [Tutorials: Creating Custom Functions](../../tutorials/creating-custom-functions.md)