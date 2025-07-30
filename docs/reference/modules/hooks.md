---
layout: default
title: hooks Module
parent: Modules
grand_parent: API Reference
nav_order: 12
---

# hooks Module

The `hooks` module provides the Python interface for registering and running hooks. Hooks are a powerful event-driven programming system that allows scripts to respond to various game events automatically.

**Module Type**: Core EFuns (External Functions)  
**Import**: `import hooks`

## Overview

The hooks module handles:
- Event-driven programming through hook registration
- Automatic execution of functions when events occur
- Information passing between the game engine and hook functions
- Modular and extensible event handling
- Decoupled system components through event notifications

Hooks allow different parts of the MUD to communicate without tight coupling. When something happens in the game (like a character entering a room, an object being picked up, or a player logging in), hooks can automatically trigger appropriate responses.

## Core Functions

### add(type, function)

**Returns**: `None`

Registers a new hook function for the specified event type.

**Parameters**:
- `type` (str): The hook type/event name
- `function` (function): Function to call when the hook fires

**Hook Function Signature**:
Hook functions must accept one argument: an information string that can be parsed with `hooks.parse_info()`.

**Example**:
```python
import hooks

def player_login_hook(info):
    """Handle player login events"""
    # Parse the hook information
    parsed = hooks.parse_info(info)
    character = parsed[0]  # First argument is usually the character
    
    if character:
        character.send("Welcome back to the game!")
        # Log the login
        import mud
        mud.log_string(f"Player {character.name} logged in")

# Register the hook
hooks.add("player_login", player_login_hook)
```

### remove(type, function)

**Returns**: `None`

Unregisters a hook function from the specified event type.

**Parameters**:
- `type` (str): The hook type/event name
- `function` (function): The function to remove

**Example**:
```python
import hooks

# Remove a previously registered hook
hooks.remove("player_login", player_login_hook)
```

### run(hooktypes)

**Returns**: `None`

Runs all hooks registered to the given type(s).

**Parameters**:
- `hooktypes` (str): The hook type or comma-separated list of hook types

**Example**:
```python
import hooks

# Run a specific hook type
hooks.run("player_death")

# Run multiple hook types
hooks.run("combat_start,combat_round")
```

## Information Handling

### parse_info(info)

**Returns**: `tuple`

Parses hook information string into a tuple of values.

**Parameters**:
- `info` (str): The information string passed to the hook function

**Example**:
```python
import hooks

def combat_hook(info):
    """Handle combat events"""
    parsed = hooks.parse_info(info)
    attacker, defender, weapon, damage = parsed
    
    if attacker and defender:
        print(f"{attacker.name} attacks {defender.name} for {damage} damage")

hooks.add("combat_hit", combat_hook)
```

### build_info(format, args)

**Returns**: `str`

Creates hook information from a format string and tuple of values.

**Parameters**:
- `format` (str): Format string with space-separated argument types
- `args` (tuple): Tuple of values matching the format

**Format Arguments**:
- `ch` - Character
- `rm` - Room
- `obj` - Object
- `ex` - Exit
- `sk` - Socket
- `str` - String
- `int` - Integer
- `dbl` - Double/Float

**Example**:
```python
import hooks

# Build hook information
character = get_character()
room = get_room()
damage = 25

info = hooks.build_info("ch rm int", (character, room, damage))

# This info can then be passed to hook functions
```

## Common Hook Types

While hook types are defined by the MUD's C code and can be extended, here are some common hook types you might encounter:

### Character Hooks
- `player_login` - When a player logs in
- `player_logout` - When a player logs out
- `player_death` - When a player dies
- `player_level` - When a player gains a level
- `char_enter_room` - When a character enters a room
- `char_leave_room` - When a character leaves a room

### Combat Hooks
- `combat_start` - When combat begins
- `combat_end` - When combat ends
- `combat_hit` - When an attack hits
- `combat_miss` - When an attack misses
- `combat_kill` - When something is killed

### Object Hooks
- `obj_get` - When an object is picked up
- `obj_drop` - When an object is dropped
- `obj_give` - When an object is given to someone
- `obj_equip` - When an object is equipped
- `obj_unequip` - When an object is unequipped

### System Hooks
- `server_startup` - When the server starts
- `server_shutdown` - When the server shuts down
- `server_copyover` - When a copyover occurs
- `mud_hour` - Every game hour
- `mud_day` - Every game day

## Usage Patterns

### Player Statistics Tracking

```python
import hooks, auxiliary, storage

class PlayerStats:
    """Track player statistics"""
    
    def __init__(self, storage_set=None):
        if storage_set:
            self.logins = storage_set.readInt("logins")
            self.deaths = storage_set.readInt("deaths")
            self.kills = storage_set.readInt("kills")
            self.rooms_visited = storage_set.readInt("rooms_visited")
            self.objects_picked_up = storage_set.readInt("objects_picked_up")
        else:
            self.logins = 0
            self.deaths = 0
            self.kills = 0
            self.rooms_visited = 0
            self.objects_picked_up = 0
    
    def store(self):
        set = storage.StorageSet()
        set.storeInt("logins", self.logins)
        set.storeInt("deaths", self.deaths)
        set.storeInt("kills", self.kills)
        set.storeInt("rooms_visited", self.rooms_visited)
        set.storeInt("objects_picked_up", self.objects_picked_up)
        return set
    
    def copy(self):
        new_stats = PlayerStats()
        new_stats.logins = self.logins
        new_stats.deaths = self.deaths
        new_stats.kills = self.kills
        new_stats.rooms_visited = self.rooms_visited
        new_stats.objects_picked_up = self.objects_picked_up
        return new_stats
    
    def copyTo(self, to):
        to.logins = self.logins
        to.deaths = self.deaths
        to.kills = self.kills
        to.rooms_visited = self.rooms_visited
        to.objects_picked_up = self.objects_picked_up

# Install the auxiliary data
auxiliary.install("player_stats", PlayerStats, "character")

def track_login(info):
    """Track player logins"""
    parsed = hooks.parse_info(info)
    character = parsed[0]
    
    if character and character.is_pc:
        stats = character.aux("player_stats")
        if stats:
            stats.logins += 1

def track_death(info):
    """Track player deaths"""
    parsed = hooks.parse_info(info)
    character = parsed[0]
    
    if character and character.is_pc:
        stats = character.aux("player_stats")
        if stats:
            stats.deaths += 1

def track_kill(info):
    """Track player kills"""
    parsed = hooks.parse_info(info)
    killer, victim = parsed[0], parsed[1]
    
    if killer and killer.is_pc and victim:
        stats = killer.aux("player_stats")
        if stats:
            stats.kills += 1

def track_room_visit(info):
    """Track room visits"""
    parsed = hooks.parse_info(info)
    character, room = parsed[0], parsed[1]
    
    if character and character.is_pc:
        stats = character.aux("player_stats")
        if stats:
            stats.rooms_visited += 1

def track_object_pickup(info):
    """Track object pickups"""
    parsed = hooks.parse_info(info)
    character, obj = parsed[0], parsed[1]
    
    if character and character.is_pc:
        stats = character.aux("player_stats")
        if stats:
            stats.objects_picked_up += 1

# Register all the tracking hooks
hooks.add("player_login", track_login)
hooks.add("player_death", track_death)
hooks.add("combat_kill", track_kill)
hooks.add("char_enter_room", track_room_visit)
hooks.add("obj_get", track_object_pickup)
```

### Dynamic Economy System

```python
import hooks, mud

class EconomyManager:
    """Manage dynamic economy based on player actions"""
    
    def __init__(self):
        self.item_demand = {}  # Track item demand
        self.room_traffic = {}  # Track room traffic
        self.setup_hooks()
    
    def setup_hooks(self):
        """Set up economy tracking hooks"""
        hooks.add("obj_get", self.track_item_demand)
        hooks.add("obj_drop", self.track_item_supply)
        hooks.add("char_enter_room", self.track_room_traffic)
        hooks.add("player_buy", self.track_purchase)
        hooks.add("player_sell", self.track_sale)
    
    def track_item_demand(self, info):
        """Track when items are picked up (demand)"""
        parsed = hooks.parse_info(info)
        character, obj = parsed[0], parsed[1]
        
        if obj and obj.prototypes:
            item_type = obj.prototypes.split(',')[0]
            self.item_demand[item_type] = self.item_demand.get(item_type, 0) + 1
            
            # Adjust prices based on demand
            self.adjust_item_price(item_type, 1.02)  # 2% price increase
    
    def track_item_supply(self, info):
        """Track when items are dropped (supply)"""
        parsed = hooks.parse_info(info)
        character, obj = parsed[0], parsed[1]
        
        if obj and obj.prototypes:
            item_type = obj.prototypes.split(',')[0]
            # Increase supply, decrease price
            self.adjust_item_price(item_type, 0.98)  # 2% price decrease
    
    def track_room_traffic(self, info):
        """Track room traffic for shop placement"""
        parsed = hooks.parse_info(info)
        character, room = parsed[0], parsed[1]
        
        if room:
            room_key = room.proto
            self.room_traffic[room_key] = self.room_traffic.get(room_key, 0) + 1
    
    def adjust_item_price(self, item_type, multiplier):
        """Adjust item price based on supply/demand"""
        current_price = mud.get_global(f"price_{item_type}") or 100
        new_price = int(current_price * multiplier)
        
        # Keep prices within reasonable bounds
        new_price = max(10, min(1000, new_price))
        
        mud.set_global(f"price_{item_type}", new_price)
    
    def get_popular_rooms(self, limit=10):
        """Get most popular rooms by traffic"""
        sorted_rooms = sorted(self.room_traffic.items(), 
                            key=lambda x: x[1], reverse=True)
        return sorted_rooms[:limit]
    
    def get_item_price(self, item_type):
        """Get current price for an item type"""
        return mud.get_global(f"price_{item_type}") or 100

# Initialize the economy system
economy = EconomyManager()
```

### Quest System Integration

```python
import hooks, auxiliary, storage

class QuestTracker:
    """Track quest progress through hooks"""
    
    def __init__(self, storage_set=None):
        if storage_set:
            self.active_quests = {}
            quest_list = storage_set.readList("quests")
            for quest_set in quest_list.sets():
                quest_id = quest_set.readString("id")
                progress = quest_set.readInt("progress")
                self.active_quests[quest_id] = progress
        else:
            self.active_quests = {}
    
    def add_quest(self, quest_id):
        """Add a new quest"""
        self.active_quests[quest_id] = 0
    
    def update_progress(self, quest_id, amount=1):
        """Update quest progress"""
        if quest_id in self.active_quests:
            self.active_quests[quest_id] += amount
            return True
        return False
    
    def complete_quest(self, quest_id):
        """Mark quest as complete"""
        if quest_id in self.active_quests:
            del self.active_quests[quest_id]
            return True
        return False
    
    def store(self):
        set = storage.StorageSet()
        quest_list = storage.StorageList()
        
        for quest_id, progress in self.active_quests.items():
            quest_set = storage.StorageSet()
            quest_set.storeString("id", quest_id)
            quest_set.storeInt("progress", progress)
            quest_list.add(quest_set)
        
        set.storeList("quests", quest_list)
        return set
    
    def copy(self):
        new_tracker = QuestTracker()
        new_tracker.active_quests = self.active_quests.copy()
        return new_tracker
    
    def copyTo(self, to):
        to.active_quests = self.active_quests.copy()

# Install quest tracking
auxiliary.install("quest_tracker", QuestTracker, "character")

def check_kill_quest(info):
    """Check for kill-based quest progress"""
    parsed = hooks.parse_info(info)
    killer, victim = parsed[0], parsed[1]
    
    if killer and killer.is_pc and victim:
        tracker = killer.aux("quest_tracker")
        if not tracker:
            return
        
        # Check various kill quests
        if "kill_orcs" in tracker.active_quests and "orc" in victim.race.lower():
            tracker.update_progress("kill_orcs")
            progress = tracker.active_quests["kill_orcs"]
            
            if progress >= 10:  # Quest complete
                killer.send("Quest complete: Kill 10 orcs!")
                tracker.complete_quest("kill_orcs")
                # Give reward
                killer.send("You receive 500 gold!")
        
        elif "kill_dragons" in tracker.active_quests and "dragon" in victim.race.lower():
            tracker.update_progress("kill_dragons")
            killer.send("Dragon slain! Quest progress updated.")

def check_room_quest(info):
    """Check for exploration-based quests"""
    parsed = hooks.parse_info(info)
    character, room = parsed[0], parsed[1]
    
    if character and character.is_pc and room:
        tracker = character.aux("quest_tracker")
        if not tracker:
            return
        
        # Check exploration quests
        if "explore_dungeon" in tracker.active_quests:
            if "dungeon" in room.proto.lower():
                tracker.update_progress("explore_dungeon")
                progress = tracker.active_quests["explore_dungeon"]
                
                if progress >= 5:  # Visited 5 dungeon rooms
                    character.send("Quest complete: Explore the dungeon!")
                    tracker.complete_quest("explore_dungeon")

def check_item_quest(info):
    """Check for item collection quests"""
    parsed = hooks.parse_info(info)
    character, obj = parsed[0], parsed[1]
    
    if character and character.is_pc and obj:
        tracker = character.aux("quest_tracker")
        if not tracker:
            return
        
        # Check item collection quests
        if "collect_gems" in tracker.active_quests:
            if "gem" in obj.name.lower() or "ruby" in obj.name.lower():
                tracker.update_progress("collect_gems")
                progress = tracker.active_quests["collect_gems"]
                character.send(f"Gem collected! ({progress}/3)")
                
                if progress >= 3:
                    character.send("Quest complete: Collect 3 gems!")
                    tracker.complete_quest("collect_gems")

# Register quest hooks
hooks.add("combat_kill", check_kill_quest)
hooks.add("char_enter_room", check_room_quest)
hooks.add("obj_get", check_item_quest)
```

### Server Monitoring and Alerts

```python
import hooks, mud, char, time

class ServerMonitor:
    """Monitor server health and send alerts"""
    
    def __init__(self):
        self.player_count_history = []
        self.error_count = 0
        self.last_alert_time = 0
        self.setup_monitoring()
    
    def setup_monitoring(self):
        """Set up monitoring hooks"""
        hooks.add("player_login", self.track_login)
        hooks.add("player_logout", self.track_logout)
        hooks.add("server_error", self.track_error)
        hooks.add("mud_hour", self.hourly_report)
        hooks.add("server_startup", self.server_started)
        hooks.add("server_shutdown", self.server_stopping)
    
    def track_login(self, info):
        """Track player logins"""
        current_players = len([ch for ch in char.char_list() if ch.socket])
        self.player_count_history.append((time.time(), current_players))
        
        # Keep only last 24 hours of data
        cutoff_time = time.time() - 86400
        self.player_count_history = [
            (t, count) for t, count in self.player_count_history 
            if t > cutoff_time
        ]
        
        # Alert on high player count
        if current_players > 50:  # Threshold
            self.send_alert(f"High player count: {current_players} players online")
    
    def track_logout(self, info):
        """Track player logouts"""
        current_players = len([ch for ch in char.char_list() if ch.socket])
        self.player_count_history.append((time.time(), current_players))
    
    def track_error(self, info):
        """Track server errors"""
        self.error_count += 1
        
        # Alert on error spikes
        if self.error_count % 10 == 0:  # Every 10 errors
            self.send_alert(f"Error count reached: {self.error_count}")
    
    def hourly_report(self, info):
        """Generate hourly server report"""
        current_players = len([ch for ch in char.char_list() if ch.socket])
        
        # Calculate average players over last hour
        hour_ago = time.time() - 3600
        recent_counts = [count for t, count in self.player_count_history if t > hour_ago]
        avg_players = sum(recent_counts) / len(recent_counts) if recent_counts else 0
        
        report = f"""
Hourly Server Report:
- Current Players: {current_players}
- Average Players (last hour): {avg_players:.1f}
- Errors (last hour): {self.error_count}
- Server Time: {time.ctime()}
"""
        
        mud.log_string(report)
        
        # Reset hourly counters
        self.error_count = 0
    
    def server_started(self, info):
        """Handle server startup"""
        mud.log_string("Server monitoring started")
        self.send_alert("MUD server has started successfully")
    
    def server_stopping(self, info):
        """Handle server shutdown"""
        current_players = len([ch for ch in char.char_list() if ch.socket])
        self.send_alert(f"MUD server shutting down with {current_players} players online")
    
    def send_alert(self, message):
        """Send alert to administrators"""
        current_time = time.time()
        
        # Rate limit alerts (max 1 per minute)
        if current_time - self.last_alert_time < 60:
            return
        
        self.last_alert_time = current_time
        
        # Log the alert
        mud.log_string(f"ALERT: {message}")
        
        # Send to online administrators
        admins = [ch for ch in char.char_list() 
                 if ch.socket and ch.isInGroup("admin")]
        
        if admins:
            mud.send(admins, f"[ALERT] {message}")
    
    def get_status_report(self):
        """Get current server status"""
        current_players = len([ch for ch in char.char_list() if ch.socket])
        
        if self.player_count_history:
            recent_avg = sum(count for t, count in self.player_count_history[-10:]) / min(10, len(self.player_count_history))
        else:
            recent_avg = 0
        
        return f"""
Server Status:
- Current Players: {current_players}
- Recent Average: {recent_avg:.1f}
- Total Errors: {self.error_count}
- Monitoring Since: {time.ctime(self.player_count_history[0][0]) if self.player_count_history else 'Unknown'}
"""

# Initialize server monitoring
monitor = ServerMonitor()

# Command to check server status
def server_status_command(ch, cmd, arg):
    """Show server status to administrators"""
    if not ch.isInGroup("admin"):
        ch.send("You don't have permission to view server status.")
        return
    
    status = monitor.get_status_report()
    ch.send(status)
```

### Hook-Based Plugin System

```python
import hooks

class PluginManager:
    """Manage plugins through the hook system"""
    
    def __init__(self):
        self.plugins = {}
        self.plugin_hooks = {}
    
    def register_plugin(self, name, plugin_class):
        """Register a new plugin"""
        if name in self.plugins:
            return False, f"Plugin {name} already registered"
        
        try:
            plugin_instance = plugin_class()
            self.plugins[name] = plugin_instance
            
            # Register plugin hooks if it has them
            if hasattr(plugin_instance, 'register_hooks'):
                plugin_hooks = plugin_instance.register_hooks()
                self.plugin_hooks[name] = plugin_hooks
                
                # Add hooks to the system
                for hook_type, hook_func in plugin_hooks.items():
                    hooks.add(hook_type, hook_func)
            
            return True, f"Plugin {name} registered successfully"
        
        except Exception as e:
            return False, f"Failed to register plugin {name}: {str(e)}"
    
    def unregister_plugin(self, name):
        """Unregister a plugin"""
        if name not in self.plugins:
            return False, f"Plugin {name} not found"
        
        try:
            # Remove plugin hooks
            if name in self.plugin_hooks:
                for hook_type, hook_func in self.plugin_hooks[name].items():
                    hooks.remove(hook_type, hook_func)
                del self.plugin_hooks[name]
            
            # Clean up plugin
            plugin = self.plugins[name]
            if hasattr(plugin, 'cleanup'):
                plugin.cleanup()
            
            del self.plugins[name]
            return True, f"Plugin {name} unregistered successfully"
        
        except Exception as e:
            return False, f"Failed to unregister plugin {name}: {str(e)}"
    
    def list_plugins(self):
        """List all registered plugins"""
        return list(self.plugins.keys())
    
    def get_plugin(self, name):
        """Get a plugin instance"""
        return self.plugins.get(name)

# Example plugin
class WelcomePlugin:
    """Plugin that welcomes new players"""
    
    def register_hooks(self):
        """Return hooks this plugin wants to register"""
        return {
            'player_login': self.welcome_player,
            'player_death': self.console_player
        }
    
    def welcome_player(self, info):
        """Welcome players on login"""
        parsed = hooks.parse_info(info)
        character = parsed[0]
        
        if character:
            character.send("Welcome to our MUD! Type 'help newbie' for beginner tips.")
    
    def console_player(self, info):
        """Console players on death"""
        parsed = hooks.parse_info(info)
        character = parsed[0]
        
        if character:
            character.send("Don't worry about dying - it's part of the learning experience!")
    
    def cleanup(self):
        """Clean up when plugin is unregistered"""
        pass

# Initialize plugin manager
plugin_manager = PluginManager()

# Register the welcome plugin
success, message = plugin_manager.register_plugin("welcome", WelcomePlugin)
print(message)
```

## See Also

- [event Module](event.md) - Event system for timed events
- [mudsys Module](mudsys.md) - Core system functions
- [auxiliary Module](auxiliary.md) - Auxiliary data system
- [mud Module](mud.md) - General utility functions
- [Core Concepts: Event-Driven Programming](../../core-concepts/event-driven-programming.md)
- [Tutorials: Using Hooks](../../tutorials/using-hooks.md)