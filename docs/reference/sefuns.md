---
layout: default
title: SEFuns (System External Functions)
parent: API Reference
nav_order: 4
---

# SEFuns (System External Functions)

SEFuns (System External Functions) are Python-defined global functions that extend the MUD's functionality beyond the core C-derived EFuns. These functions are implemented entirely in Python and provide higher-level abstractions, utility functions, and extensible frameworks for common MUD operations.

## Overview

SEFuns represent the Python layer of functionality built on top of the C engine. They provide:
- High-level utility functions
- Common operation abstractions
- Extensible frameworks and systems
- Library-wide functionality
- Global function registration systems

Unlike EFuns (which are C-derived) and EObjs (which are C-defined classes), SEFuns are pure Python implementations that can be easily modified, extended, and customized by MUD developers.

## Current SEFun Implementation

### Core SEFun: register_routine_check()

**Module**: `routine.py`  
**Purpose**: Global function registration for routine validation  
**Type**: Framework Extension Function

```python
def register_routine_check(check):
    '''adds a routine check to the global list. Must be a function taking one
       argument, which is the character doing the routine. Return should be
       True if the check succeeded (i.e., we should not do a routine)'''
    __global_routine_checks__.append(check)
```

**Usage**:
```python
import routine

def check_character_health(ch):
    """Don't allow routines if character is below 25% health"""
    if hasattr(ch, 'hit_points') and hasattr(ch, 'max_hit_points'):
        return ch.hit_points < (ch.max_hit_points * 0.25)
    return False

def check_character_busy(ch):
    """Don't allow routines if character is in combat"""
    return hasattr(ch, 'fighting') and ch.fighting is not None

# Register the checks globally
routine.register_routine_check(check_character_health)
routine.register_routine_check(check_character_busy)
```

### Method Extension SEFuns

**Module**: Various  
**Purpose**: Extend EObj classes with new methods  
**Type**: Class Extension Functions

The mudsys module provides SEFun-like functionality through method extension:

```python
import mudsys

def set_routine(ch, routine, repeat=False, checks=None):
    """Set a routine for a character"""
    # Implementation details...
    pass

# This becomes a SEFun-like global method
mudsys.add_char_method("set_routine", set_routine)

# Now available on all characters as:
# character.set_routine(routine_list, repeat=True)
```

## SEFun Categories

### Utility SEFuns

These provide common utility operations used throughout the MUD:

#### String and Parsing Utilities
```python
# From utils.py
def parse_keywords(kw):
    '''turns a comma-separated list of strings to a list of keywords'''
    list = kw.lower().split(",")
    for i in range(len(list)):
        list[i] = list[i].strip()
    return list

def is_keyword(kw, word, abbrev_ok=False):
    '''returns whether or not the word (or list of words) is a keyword'''
    kw = parse_keywords(kw)
    word = parse_keywords(word)
    
    for one_word in word:
        if is_one_keyword(kw, one_word, abbrev_ok):
            return True
    return False

def aan(word):
    '''return "a" or "an", depending on the word.'''
    if len(word) == 0 or not word[0].lower() in "aeiou":
        return "a " + word
    return "an " + word
```

#### Search and Find Utilities
```python
# From utils.py
def find_char(looker, list, num, name, proto=None, must_see=True):
    '''returns the numth char to match the supplied constraints'''
    count = 0
    for ch in list:
        if must_see and not looker.cansee(ch):
            continue
        elif name != None and is_keyword(ch.keywords, name, True):
            count = count + 1
        elif proto != None and ch.isinstance(proto):
            count = count + 1
        if count == num:
            return ch
    return None

def find_obj(looker, list, num, name, proto=None, must_see=True):
    '''returns the numth object to match the supplied constraints'''
    count = 0
    for obj in list:
        if must_see and not looker.cansee(obj):
            continue
        elif name != None and is_keyword(obj.keywords, name, True):
            count = count + 1
        elif proto != None and obj.isinstance(proto):
            count = count + 1
        if count == num:
            return obj
    return None
```

#### Display and Formatting Utilities
```python
# From utils.py
def build_show_list(ch, list, s_func, m_func=None, joiner="\r\n", and_end=False):
    '''builds a list of things to show a character. s_func is the description if
       there is only a single item of the type. m_func is the description if
       there are multiple occurences of the thing in the list'''
    
    buf = []
    counts = {}
    
    # Build up counts
    for thing in list:
        if s_func(thing) in counts:
            counts[s_func(thing)] = counts[s_func(thing)] + 1
        else:
            counts[s_func(thing)] = 1
    
    # Generate display
    for thing in list:
        if s_func(thing) in counts:
            count = counts.pop(s_func(thing))
            
            if count == 1:
                buf.append(s_func(thing))
            elif m_func == None or m_func(thing) == "":
                buf.append("(" + str(count) + ") " + s_func(thing))
            else:
                buf.append(m_func(thing) % count)
    
    if and_end and len(buf) > 1:
        last = buf.pop()
        return joiner.join(buf) + " and " + last
    return joiner.join(buf)

def show_list(ch, list, s_func, m_func=None):
    '''shows a list of things to the character'''
    ch.send(build_show_list(ch, list, s_func, m_func, "\r\n"))
```

### Framework SEFuns

These provide extensible frameworks for common MUD systems:

#### Routine System Framework
```python
# From routine.py
def set_routine(ch, routine, repeat=False, checks=None):
    '''Sets a routine to a character. Routine steps can contain commands
       (character strings), functions (one argument, ch), or tuples
       (delay, string | function). If a tuple is not supplied, the default
       step time is used'''
    aux = ch.getAuxiliary("routine_data")
    aux.checks = None
    if checks != None:
        aux.checks = [x for x in checks]
    aux.repeat = repeat
    aux.routine = None
    aux.step = None
    if routine != None:
        aux.routine = [x for x in routine]
        aux.step = 0
        start_routine(ch)

# Usage example:
def patrol_function(ch):
    ch.act("look")
    ch.send("All clear here.")

routine = [
    "north",
    "look", 
    (5.0, patrol_function),  # 5 second delay, then function
    "south",
    (10.0, "emote adjusts his equipment")
]

character.set_routine(routine, repeat=True)
```

#### Check System Framework
```python
# From routine.py - extensible check system
__global_routine_checks__ = []

def register_routine_check(check):
    '''adds a routine check to the global list'''
    __global_routine_checks__.append(check)

def try_step(ch):
    '''Checks to see if we can perform a step in the routine'''
    aux = ch.getAuxiliary("routine_data")
    
    if aux.routine == None:
        return False
    
    # Build a list of the checks we need to perform
    checks = __global_routine_checks__
    if aux.checks != None:
        checks = checks + aux.checks
    
    # If we have checks, run them
    if checks != None:
        for check in checks:
            if check(ch) == True:
                # queue us back up to try again later
                start_routine(ch)
                return False
    
    # If we had no checks or they were all passed, do the step
    do_step(ch)
    return True
```

### System Integration SEFuns

These integrate with various MUD systems:

#### OLC Integration Utilities
```python
# From utils.py
def olc_display_table(sock, list, num_cols, disp=lambda x: x):
    '''used by OLC functions to display a list of options in a table form.
       Also displays each option's position number and colorizes everything.'''
    print_room = (80 - 10*num_cols)/num_cols
    fmt = "  {c%%2d{y) {g%%-%ds%%s" % print_room
    i = 0
    
    # display each cell
    for item in list:
        endtag = "   "
        if i % num_cols == (num_cols - 1):
            endtag = "\r\n"
        sock.send_raw(fmt % (i, disp(item), endtag))
        i += 1
    
    # do we need to end this with a newline?
    if i % num_cols != 0:
        sock.send_raw("\r\n")
```

#### Inventory and Equipment Utilities
```python
# From utils.py
def has_proto(ch, proto):
    '''returns whether or not the character has on his or her person an object
       that inherits from the given prototype'''
    for obj in ch.inv + ch.eq:
        if obj.isinstance(proto):
            return True
    return False

def get_count(str):
    '''separates a name and a count, and returns the two'''
    parts = str.lower().split(".", 1)
    
    # did we get two, or one?
    if len(parts) == 1 and parts[0] == "all":
        return "all", ""
    elif len(parts) == 1:
        return 1, str
    
    if parts[0] == "all":
        return "all", parts[1]
    try:
        return int(parts[0]), parts[1]
    except:
        return 1, str
```

## Creating Custom SEFuns

### Basic SEFun Pattern
```python
# my_sefuns.py

def calculate_experience_needed(level):
    """Calculate experience points needed for a given level"""
    return level * 1000 + (level * level * 50)

def format_time_duration(seconds):
    """Format seconds into a human-readable duration"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hours, {minutes} minutes"

def find_players_by_level(min_level, max_level=None):
    """Find all players within a level range"""
    import char
    
    players = []
    for ch in char.char_list():
        if ch.is_pc and hasattr(ch, 'level'):
            if max_level is None:
                if ch.level >= min_level:
                    players.append(ch)
            else:
                if min_level <= ch.level <= max_level:
                    players.append(ch)
    
    return players

# Make functions globally available
import mud
mud.calculate_experience_needed = calculate_experience_needed
mud.format_time_duration = format_time_duration
mud.find_players_by_level = find_players_by_level
```

### Framework SEFun Pattern
```python
# quest_system.py

# Global quest registry
__global_quest_handlers__ = {}
__global_quest_checks__ = []

def register_quest_handler(quest_type, handler_func):
    """Register a handler for a specific quest type"""
    __global_quest_handlers__[quest_type] = handler_func

def register_quest_check(check_func):
    """Register a global quest validation check"""
    __global_quest_checks__.append(check_func)

def process_quest_event(character, event_type, event_data):
    """Process a quest-related event"""
    # Run global checks first
    for check in __global_quest_checks__:
        if not check(character, event_type, event_data):
            return False
    
    # Process with registered handlers
    if event_type in __global_quest_handlers__:
        return __global_quest_handlers__[event_type](character, event_data)
    
    return False

def complete_quest(character, quest_id):
    """Complete a quest for a character"""
    quest_data = character.aux("quest_tracker")
    if quest_data and quest_id in quest_data.active_quests:
        # Remove from active quests
        del quest_data.active_quests[quest_id]
        
        # Process completion
        return process_quest_event(character, "quest_complete", {"quest_id": quest_id})
    
    return False

# Usage example:
def kill_quest_handler(character, event_data):
    """Handle kill-type quests"""
    victim = event_data.get("victim")
    if victim and "orc" in victim.race.lower():
        quest_data = character.aux("quest_tracker")
        if "kill_orcs" in quest_data.active_quests:
            quest_data.active_quests["kill_orcs"] += 1
            if quest_data.active_quests["kill_orcs"] >= 10:
                complete_quest(character, "kill_orcs")
                return True
    return False

register_quest_handler("kill", kill_quest_handler)
```

### Method Extension SEFun Pattern
```python
# character_extensions.py

import mudsys

def get_total_wealth(self):
    """Calculate character's total wealth including inventory"""
    total = self.getvar("gold") or 0
    
    # Add value of inventory items
    for obj in self.inv:
        item_value = obj.getvar("value") or 0
        total += item_value
    
    return total

def is_encumbered(self):
    """Check if character is carrying too much weight"""
    max_carry = self.getvar("max_carry_weight") or 100.0
    current_weight = sum(obj.weight for obj in self.inv)
    return current_weight > max_carry

def get_skill_level(self, skill_name):
    """Get character's skill level"""
    skills = self.aux("character_skills")
    if skills and hasattr(skills, skill_name):
        return getattr(skills, skill_name)
    return 0

def improve_skill(self, skill_name, amount=1):
    """Improve a character's skill"""
    skills = self.aux("character_skills")
    if skills:
        current = getattr(skills, skill_name, 0)
        setattr(skills, skill_name, current + amount)
        return True
    return False

# Add methods to PyChar class
mudsys.add_char_method("get_total_wealth", get_total_wealth)
mudsys.add_char_method("is_encumbered", is_encumbered)
mudsys.add_char_method("get_skill_level", get_skill_level)
mudsys.add_char_method("improve_skill", improve_skill)

# Now available as:
# wealth = character.get_total_wealth()
# encumbered = character.is_encumbered()
# skill = character.get_skill_level("swordsmanship")
# character.improve_skill("swordsmanship", 2)
```

## SEFun Best Practices

### Global Function Registration
```python
# Good: Register functions in a central location
import mud

def my_utility_function():
    pass

# Make it globally available
mud.my_utility_function = my_utility_function

# Or create a utilities module
class MudUtilities:
    @staticmethod
    def calculate_damage(attacker, defender):
        pass
    
    @staticmethod
    def format_currency(amount):
        pass

mud.utils = MudUtilities()
```

### Framework Design
```python
# Good: Extensible framework pattern
__global_handlers__ = {}
__global_checks__ = []

def register_handler(event_type, handler):
    """Allow other modules to register handlers"""
    if event_type not in __global_handlers__:
        __global_handlers__[event_type] = []
    __global_handlers__[event_type].append(handler)

def register_check(check_func):
    """Allow other modules to register validation checks"""
    __global_checks__.append(check_func)

def process_event(event_type, *args, **kwargs):
    """Process an event through all registered handlers"""
    # Run checks first
    for check in __global_checks__:
        if not check(event_type, *args, **kwargs):
            return False
    
    # Run handlers
    if event_type in __global_handlers__:
        for handler in __global_handlers__[event_type]:
            if handler(*args, **kwargs):
                return True
    
    return False
```

### Error Handling
```python
# Good: Robust error handling in SEFuns
def safe_sefun(character, *args):
    """Example of safe SEFun implementation"""
    try:
        # Validate inputs
        if not character:
            return False
        
        if not hasattr(character, 'name'):
            return False
        
        # Perform operation
        result = perform_operation(character, *args)
        return result
        
    except Exception as e:
        # Log error but don't crash
        import mud
        mud.log_string(f"Error in safe_sefun: {str(e)}")
        return False

def perform_operation(character, *args):
    """Actual operation implementation"""
    pass
```

## Future SEFun Expansion

The SEFun system provides a framework for expanding MUD functionality:

### Planned SEFun Areas
- **Combat System SEFuns**: Damage calculation, combat mechanics
- **Economy SEFuns**: Price calculation, trade systems
- **Social SEFuns**: Guild management, player relationships
- **World SEFuns**: Weather systems, time-based events
- **Communication SEFuns**: Channel systems, mail systems

### SEFun Development Guidelines
1. **Modularity**: Keep SEFuns focused and modular
2. **Extensibility**: Design for easy extension and customization
3. **Documentation**: Provide clear documentation and examples
4. **Error Handling**: Include robust error handling
5. **Performance**: Consider performance implications
6. **Integration**: Ensure smooth integration with existing systems

## See Also

- [EFuns (External Functions)](efuns.md) - C-derived Python functions
- [EObjs (External Objects)](eobjs.md) - C-defined Python classes
- [Module Reference](modules/) - Individual module documentation
- [Core Concepts: Python Integration](../core-concepts/python-integration.md)
- [Tutorials: Creating Custom Functions](../../tutorials/creating-custom-functions.md)