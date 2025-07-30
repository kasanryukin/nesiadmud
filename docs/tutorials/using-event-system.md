---
layout: default
title: Using the Event System
parent: Build Complexity
grand_parent: Tutorials
nav_order: 4
permalink: /tutorials/using-event-system/
---

# Using the Event System

Learn to create sophisticated timed behaviors and scheduled actions using NakedMud's event system for complex game mechanics.

## Overview

This tutorial teaches you how to use NakedMud's event system to create timed actions, scheduled behaviors, and complex sequences. You'll learn to build everything from simple delays to sophisticated scheduling systems that manage complex game mechanics over time.

## Prerequisites

- Completed [Basic Triggers and Scripts](basic-triggers-scripts/)
- Understanding of [Core Concepts](/core-concepts/)
- Familiarity with Python functions and callbacks
- Intermediate Python programming skills

## What You'll Learn

- Understanding the event system architecture
- Creating simple timed events
- Building complex event sequences
- Managing recurring events and schedules
- Creating event-driven game mechanics
- Performance optimization for event systems

## Step 1: Event System Fundamentals

Let's start by understanding how the event system works:

```python
# File: lib/pymodules/advanced_event_systems.py

import mudsys
import char
import room
import obj
import auxiliary
import event
import random

def basic_event_examples():
    """Examples of basic event system usage."""
    
    # Simple delayed action (5 seconds)
    def delayed_message(target, message):
        """Send a delayed message."""
        if target and message:
            char.charSend(target, message)
    
    # Schedule the delayed message
    # event.start_event(target_object, delay_seconds, callback_function, *args)
    
    # Example usage in a command or trigger:
    def cmd_delayed_hello(ch, cmd, arg):
        """Command that sends a delayed greeting."""
        
        delay = 5  # 5 seconds
        message = "Hello! This message was delayed by 5 seconds."
        
        char.charSend(ch, "A delayed message has been scheduled...")
        event.start_event(ch, delay, delayed_message, ch, message)
    
    # Register the command
    mudsys.add_cmd("delayed_hello", None, cmd_delayed_hello, "player", 1)

def event_with_multiple_parameters():
    """Example of events with multiple parameters."""
    
    def complex_event_handler(room_ref, actor, message, repeat_count):
        """Handle a complex event with multiple parameters."""
        
        if not room_ref or not actor:
            return
        
        actor_name = char.charGetName(actor)
        
        # Send the message
        room.roomSendMessage(room_ref, f"{actor_name}: {message}")
        
        # If we should repeat, schedule another event
        if repeat_count > 1:
            next_delay = random.randint(3, 8)  # Random delay between 3-8 seconds
            event.start_event(room_ref, next_delay, complex_event_handler, 
                            room_ref, actor, message, repeat_count - 1)
    
    def cmd_echo_sequence(ch, cmd, arg):
        """Command that creates an echo sequence."""
        
        if not arg:
            char.charSend(ch, "Usage: echo_sequence <message>")
            return
        
        rm = char.charGetRoom(ch)
        if not rm:
            return
        
        # Start a sequence of 3 echoes
        char.charSend(ch, "Starting echo sequence...")
        event.start_event(rm, 2, complex_event_handler, rm, ch, arg, 3)
    
    mudsys.add_cmd("echo_sequence", None, cmd_echo_sequence, "player", 1)

# Initialize basic examples
basic_event_examples()
event_with_multiple_parameters()
```

## Step 2: Building Event Sequences

Create complex sequences of timed events:

```python
# Add to advanced_event_systems.py

class EventSequence:
    """Manage complex sequences of timed events."""
    
    def __init__(self, sequence_id, target_object):
        self.sequence_id = sequence_id
        self.target = target_object
        self.steps = []
        self.current_step = 0
        self.is_running = False
    
    def add_step(self, delay, callback, *args, **kwargs):
        """Add a step to the sequence."""
        step = {
            "delay": delay,
            "callback": callback,
            "args": args,
            "kwargs": kwargs
        }
        self.steps.append(step)
    
    def start_sequence(self):
        """Start executing the sequence."""
        if self.is_running:
            return False
        
        self.is_running = True
        self.current_step = 0
        
        if self.steps:
            self.execute_next_step()
        
        return True
    
    def execute_next_step(self):
        """Execute the next step in the sequence."""
        if self.current_step >= len(self.steps):
            # Sequence complete
            self.is_running = False
            return
        
        step = self.steps[self.current_step]
        
        # Schedule the step
        event.start_event(self.target, step["delay"], self.step_callback, 
                         step["callback"], step["args"], step["kwargs"])
    
    def step_callback(self, callback_func, args, kwargs):
        """Handle execution of a sequence step."""
        
        try:
            # Execute the step's callback
            callback_func(*args, **kwargs)
        except Exception as e:
            mudsys.log_string(f"Error in event sequence {self.sequence_id}: {e}")
        
        # Move to next step
        self.current_step += 1
        
        if self.current_step < len(self.steps):
            # Schedule next step
            self.execute_next_step()
        else:
            # Sequence complete
            self.is_running = False

def ritual_casting_sequence(caster, spell_name):
    """Create a complex spell casting sequence."""
    
    caster_name = char.charGetName(caster)
    caster_room = char.charGetRoom(caster)
    
    if not caster_room:
        return
    
    # Create the casting sequence
    sequence = EventSequence(f"ritual_{spell_name}", caster)
    
    # Step 1: Begin ritual (immediate)
    def begin_ritual():
        char.charSend(caster, f"You begin the complex ritual to cast {spell_name}.")
        char.charSendRoom(caster, f"{caster_name} begins chanting and making mystical gestures.")
    
    sequence.add_step(0, begin_ritual)
    
    # Step 2: Gather energy (3 seconds)
    def gather_energy():
        char.charSend(caster, "You feel magical energy gathering around you.")
        char.charSendRoom(caster, f"Mystical energy swirls around {caster_name}.")
    
    sequence.add_step(3, gather_energy)
    
    # Step 3: Focus power (4 seconds)
    def focus_power():
        char.charSend(caster, "You focus the gathered energy into a coherent pattern.")
        char.charSendRoom(caster, f"The energy around {caster_name} begins to take shape.")
    
    sequence.add_step(4, focus_power)
    
    # Step 4: Final incantation (3 seconds)
    def final_incantation():
        char.charSend(caster, f"You speak the final words of {spell_name}!")
        char.charSendRoom(caster, f"{caster_name} shouts the final incantation!")
    
    sequence.add_step(3, final_incantation)
    
    # Step 5: Cast spell (2 seconds)
    def cast_spell():
        char.charSend(caster, f"The {spell_name} spell is complete!")
        char.charSendRoom(caster, f"{caster_name} completes the {spell_name} ritual!")
        
        # Apply spell effects here
        apply_ritual_spell_effects(caster, spell_name)
    
    sequence.add_step(2, cast_spell)
    
    # Start the sequence
    sequence.start_sequence()

def apply_ritual_spell_effects(caster, spell_name):
    """Apply the effects of a completed ritual spell."""
    
    caster_name = char.charGetName(caster)
    caster_room = char.charGetRoom(caster)
    
    if spell_name == "sanctuary":
        # Create a sanctuary effect
        char.charSend(caster, "A protective aura surrounds you!")
        char.charSendRoom(caster, f"A shimmering protective barrier appears around {caster_name}!")
        
        # Set temporary protection (would integrate with actual protection system)
        auxiliary.charSetAuxiliaryData(caster, "sanctuary_protection", str(mudsys.current_time() + 300))
    
    elif spell_name == "illumination":
        # Light up the area
        if caster_room:
            room.roomSendMessage(caster_room, "Brilliant light fills the area!")
            auxiliary.roomSetAuxiliaryData(caster_room, "magical_light", str(mudsys.current_time() + 600))
    
    elif spell_name == "teleportation":
        # Teleport the caster (simplified)
        char.charSend(caster, "Reality bends around you as you are transported elsewhere!")
        char.charSendRoom(caster, f"{caster_name} vanishes in a flash of light!")
        
        # In a real implementation, this would actually move the character

def cmd_cast_ritual(ch, cmd, arg):
    """Command to cast a ritual spell."""
    
    if not arg:
        char.charSend(ch, "Usage: cast_ritual <spell_name>")
        char.charSend(ch, "Available rituals: sanctuary, illumination, teleportation")
        return
    
    spell_name = arg.lower().strip()
    valid_spells = ["sanctuary", "illumination", "teleportation"]
    
    if spell_name not in valid_spells:
        char.charSend(ch, f"Unknown ritual: {spell_name}")
        char.charSend(ch, f"Available rituals: {', '.join(valid_spells)}")
        return
    
    # Check if already casting
    if auxiliary.charGetAuxiliaryData(ch, "casting_ritual"):
        char.charSend(ch, "You are already in the middle of casting a ritual!")
        return
    
    # Mark as casting
    auxiliary.charSetAuxiliaryData(ch, "casting_ritual", "true")
    
    # Start the ritual sequence
    ritual_casting_sequence(ch, spell_name)
    
    # Clear casting flag after total duration (12 seconds + buffer)
    event.start_event(ch, 15, clear_casting_flag, ch)

def clear_casting_flag(ch):
    """Clear the casting flag."""
    auxiliary.charSetAuxiliaryData(ch, "casting_ritual", "")

mudsys.add_cmd("cast_ritual", None, cmd_cast_ritual, "player", 1)
```

## Step 3: Recurring Events and Schedules

Create events that repeat on schedules:

```python
# Add to advanced_event_systems.py

class RecurringEventManager:
    """Manage recurring events and schedules."""
    
    def __init__(self):
        self.recurring_events = {}
    
    def add_recurring_event(self, event_id, target, interval, callback, *args, **kwargs):
        """Add a recurring event."""
        
        event_data = {
            "target": target,
            "interval": interval,
            "callback": callback,
            "args": args,
            "kwargs": kwargs,
            "active": True
        }
        
        self.recurring_events[event_id] = event_data
        
        # Schedule the first occurrence
        event.start_event(target, interval, self.recurring_event_handler, event_id)
    
    def recurring_event_handler(self, event_id):
        """Handle a recurring event occurrence."""
        
        if event_id not in self.recurring_events:
            return
        
        event_data = self.recurring_events[event_id]
        
        if not event_data["active"]:
            return
        
        try:
            # Execute the callback
            callback = event_data["callback"]
            args = event_data["args"]
            kwargs = event_data["kwargs"]
            
            callback(*args, **kwargs)
            
            # Schedule the next occurrence
            target = event_data["target"]
            interval = event_data["interval"]
            
            event.start_event(target, interval, self.recurring_event_handler, event_id)
            
        except Exception as e:
            mudsys.log_string(f"Error in recurring event {event_id}: {e}")
    
    def stop_recurring_event(self, event_id):
        """Stop a recurring event."""
        if event_id in self.recurring_events:
            self.recurring_events[event_id]["active"] = False
    
    def remove_recurring_event(self, event_id):
        """Remove a recurring event completely."""
        if event_id in self.recurring_events:
            del self.recurring_events[event_id]

# Global recurring event manager
recurring_manager = RecurringEventManager()

def weather_system_events():
    """Set up recurring weather events."""
    
    def update_weather():
        """Update weather conditions across all rooms."""
        
        # This would integrate with your weather system
        # For now, just log the weather update
        mudsys.log_string("Weather system update triggered")
        
        # In a real implementation, you'd update weather in all outdoor rooms
        # update_global_weather()
    
    def seasonal_change():
        """Handle seasonal changes."""
        
        mudsys.log_string("Seasonal change event triggered")
        
        # This would handle season transitions, temperature changes, etc.
        # handle_seasonal_transition()
    
    # Weather updates every 10 minutes (600 seconds)
    recurring_manager.add_recurring_event("weather_update", None, 600, update_weather)
    
    # Seasonal changes every 24 hours (86400 seconds) - simplified
    recurring_manager.add_recurring_event("seasonal_change", None, 86400, seasonal_change)

def npc_behavior_schedules():
    """Set up scheduled NPC behaviors."""
    
    def npc_daily_routine(npc_name):
        """Handle daily routine for an NPC."""
        
        # This would find the NPC and update their behavior
        mudsys.log_string(f"Daily routine triggered for NPC: {npc_name}")
        
        # In a real implementation:
        # npc = find_npc_by_name(npc_name)
        # if npc:
        #     update_npc_daily_schedule(npc)
    
    def shopkeeper_restock():
        """Handle shopkeeper restocking."""
        
        mudsys.log_string("Shopkeeper restocking event triggered")
        
        # This would restock all shops
        # restock_all_shops()
    
    # NPC routines every 2 hours (7200 seconds)
    recurring_manager.add_recurring_event("npc_routines", None, 7200, npc_daily_routine, "all_npcs")
    
    # Shop restocking every 6 hours (21600 seconds)
    recurring_manager.add_recurring_event("shop_restock", None, 21600, shopkeeper_restock)

# Initialize recurring events
weather_system_events()
npc_behavior_schedules()
```

## Step 4: Event-Driven Game Mechanics

Create complex game mechanics using events:

```python
# Add to advanced_event_systems.py

class QuestEventSystem:
    """Manage quest-related events and timers."""
    
    def __init__(self):
        self.active_quests = {}
    
    def start_timed_quest(self, player, quest_id, time_limit):
        """Start a quest with a time limit."""
        
        player_name = char.charGetName(player)
        
        # Store quest data
        quest_data = {
            "player": player,
            "quest_id": quest_id,
            "start_time": mudsys.current_time(),
            "time_limit": time_limit,
            "completed": False
        }
        
        quest_key = f"{player_name}_{quest_id}"
        self.active_quests[quest_key] = quest_data
        
        # Schedule quest expiration
        event.start_event(player, time_limit, self.quest_timeout_handler, quest_key)
        
        # Schedule warning events
        warning_times = [time_limit * 0.75, time_limit * 0.9]  # 75% and 90% of time elapsed
        
        for warning_time in warning_times:
            if warning_time > 0:
                event.start_event(player, warning_time, self.quest_warning_handler, 
                                quest_key, time_limit - warning_time)
    
    def quest_warning_handler(self, quest_key, time_remaining):
        """Handle quest time warnings."""
        
        if quest_key not in self.active_quests:
            return
        
        quest_data = self.active_quests[quest_key]
        player = quest_data["player"]
        quest_id = quest_data["quest_id"]
        
        if quest_data["completed"]:
            return
        
        minutes_remaining = int(time_remaining / 60)
        
        if minutes_remaining > 1:
            char.charSend(player, f"Quest '{quest_id}': {minutes_remaining} minutes remaining!")
        else:
            char.charSend(player, f"Quest '{quest_id}': Less than a minute remaining!")
    
    def quest_timeout_handler(self, quest_key):
        """Handle quest timeout."""
        
        if quest_key not in self.active_quests:
            return
        
        quest_data = self.active_quests[quest_key]
        player = quest_data["player"]
        quest_id = quest_data["quest_id"]
        
        if quest_data["completed"]:
            return
        
        # Quest failed due to timeout
        char.charSend(player, f"Quest '{quest_id}' has failed due to timeout!")
        
        # Apply failure consequences
        self.apply_quest_failure(player, quest_id)
        
        # Remove quest
        del self.active_quests[quest_key]
    
    def complete_quest(self, player, quest_id):
        """Mark a quest as completed."""
        
        player_name = char.charGetName(player)
        quest_key = f"{player_name}_{quest_id}"
        
        if quest_key in self.active_quests:
            self.active_quests[quest_key]["completed"] = True
            char.charSend(player, f"Quest '{quest_id}' completed successfully!")
            
            # Apply success rewards
            self.apply_quest_success(player, quest_id)
    
    def apply_quest_failure(self, player, quest_id):
        """Apply consequences for quest failure."""
        
        # This would implement actual failure consequences
        mudsys.log_string(f"Quest {quest_id} failed for player {char.charGetName(player)}")
    
    def apply_quest_success(self, player, quest_id):
        """Apply rewards for quest success."""
        
        # This would implement actual success rewards
        mudsys.log_string(f"Quest {quest_id} completed by player {char.charGetName(player)}")

# Global quest system
quest_system = QuestEventSystem()

def combat_event_system():
    """Event-driven combat mechanics."""
    
    def apply_damage_over_time(target, damage_per_tick, duration, damage_type="poison"):
        """Apply damage over time effect."""
        
        if not target:
            return
        
        target_name = char.charGetName(target)
        
        # Apply immediate damage
        char.charSend(target, f"You take {damage_per_tick} {damage_type} damage!")
        char.charSendRoom(target, f"{target_name} writhes in pain from {damage_type}!")
        
        # Schedule next damage tick if duration remains
        if duration > 1:
            event.start_event(target, 3, apply_damage_over_time, 
                            target, damage_per_tick, duration - 1, damage_type)
        else:
            # Effect ends
            char.charSend(target, f"The {damage_type} effect wears off.")
    
    def delayed_explosion(room_ref, damage, delay_message=""):
        """Create a delayed explosion in a room."""
        
        if not room_ref:
            return
        
        if delay_message:
            room.roomSendMessage(room_ref, delay_message)
        
        # Explosion after delay
        room.roomSendMessage(room_ref, "A massive explosion rocks the area!")
        
        # Apply damage to everyone in the room
        chars_in_room = room.roomGetChars(room_ref)
        for character in chars_in_room:
            if not char.charIsNPC(character):
                char.charSend(character, f"The explosion hits you for {damage} damage!")
    
    def regeneration_effect(target, heal_per_tick, duration):
        """Apply healing over time effect."""
        
        if not target:
            return
        
        target_name = char.charGetName(target)
        
        # Apply healing
        char.charSend(target, f"You heal {heal_per_tick} points of damage.")
        
        # Schedule next healing tick if duration remains
        if duration > 1:
            event.start_event(target, 5, regeneration_effect, 
                            target, heal_per_tick, duration - 1)
        else:
            # Effect ends
            char.charSend(target, "The regeneration effect fades.")
    
    # Example usage functions
    def cmd_poison_cloud(ch, cmd, arg):
        """Create a poison cloud with delayed effects."""
        
        rm = char.charGetRoom(ch)
        if not rm:
            return
        
        char.charSend(ch, "You create a poison cloud!")
        room.roomSendMessage(rm, "A noxious green cloud begins to form...")
        
        # Delayed poison effect
        event.start_event(rm, 3, delayed_explosion, rm, 25, 
                         "The poison cloud thickens and becomes deadly!")
    
    def cmd_healing_aura(ch, cmd, arg):
        """Create a healing aura effect."""
        
        char.charSend(ch, "You begin channeling a healing aura.")
        
        # Start regeneration effect
        regeneration_effect(ch, 5, 10)  # 5 HP per tick for 10 ticks
    
    mudsys.add_cmd("poison_cloud", None, cmd_poison_cloud, "wizard", 1)
    mudsys.add_cmd("healing_aura", None, cmd_healing_aura, "player", 1)

combat_event_system()
```

## Step 5: Advanced Event Patterns

Create sophisticated event management patterns:

```python
# Add to advanced_event_systems.py

class EventChain:
    """Create chains of conditional events."""
    
    def __init__(self, chain_id):
        self.chain_id = chain_id
        self.events = []
        self.current_index = 0
        self.is_active = False
    
    def add_conditional_event(self, delay, condition_func, success_callback, 
                            failure_callback=None, *args, **kwargs):
        """Add a conditional event to the chain."""
        
        event_data = {
            "delay": delay,
            "condition": condition_func,
            "success_callback": success_callback,
            "failure_callback": failure_callback,
            "args": args,
            "kwargs": kwargs
        }
        
        self.events.append(event_data)
    
    def start_chain(self, target):
        """Start executing the event chain."""
        
        if self.is_active:
            return False
        
        self.target = target
        self.is_active = True
        self.current_index = 0
        
        self.execute_next_event()
        return True
    
    def execute_next_event(self):
        """Execute the next event in the chain."""
        
        if self.current_index >= len(self.events):
            # Chain complete
            self.is_active = False
            return
        
        event_data = self.events[self.current_index]
        
        # Schedule the conditional check
        event.start_event(self.target, event_data["delay"], 
                         self.check_condition, event_data)
    
    def check_condition(self, event_data):
        """Check the condition for an event."""
        
        try:
            # Check the condition
            condition_met = event_data["condition"](*event_data["args"], **event_data["kwargs"])
            
            if condition_met:
                # Execute success callback
                if event_data["success_callback"]:
                    event_data["success_callback"](*event_data["args"], **event_data["kwargs"])
                
                # Move to next event
                self.current_index += 1
                self.execute_next_event()
            else:
                # Execute failure callback if provided
                if event_data["failure_callback"]:
                    event_data["failure_callback"](*event_data["args"], **event_data["kwargs"])
                
                # Chain fails
                self.is_active = False
        
        except Exception as e:
            mudsys.log_string(f"Error in event chain {self.chain_id}: {e}")
            self.is_active = False

def puzzle_solving_chain():
    """Create a complex puzzle-solving event chain."""
    
    def check_player_in_room(player, room_vnum):
        """Check if player is in a specific room."""
        player_room = char.charGetRoom(player)
        # In a real implementation, you'd check the room vnum
        return player_room is not None
    
    def check_player_has_item(player, item_name):
        """Check if player has a specific item."""
        # In a real implementation, you'd check player's inventory
        return True  # Simplified for example
    
    def puzzle_step_success(player, step_name):
        """Handle successful puzzle step."""
        char.charSend(player, f"Puzzle step '{step_name}' completed successfully!")
    
    def puzzle_step_failure(player, step_name):
        """Handle failed puzzle step."""
        char.charSend(player, f"Puzzle step '{step_name}' failed. Try again!")
    
    def start_puzzle_chain(player):
        """Start a complex puzzle chain."""
        
        chain = EventChain("temple_puzzle")
        
        # Step 1: Player must be in the temple within 30 seconds
        chain.add_conditional_event(30, check_player_in_room, puzzle_step_success, 
                                  puzzle_step_failure, player, "temple", "step1")
        
        # Step 2: Player must have the key within 60 seconds
        chain.add_conditional_event(60, check_player_has_item, puzzle_step_success,
                                  puzzle_step_failure, player, "ancient_key", "step2")
        
        # Step 3: Final check after 45 seconds
        chain.add_conditional_event(45, check_player_in_room, puzzle_step_success,
                                  puzzle_step_failure, player, "inner_sanctum", "step3")
        
        # Start the chain
        chain.start_chain(player)
        
        char.charSend(player, "The ancient puzzle has begun! You have limited time to complete each step.")
    
    def cmd_start_puzzle(ch, cmd, arg):
        """Command to start the puzzle chain."""
        start_puzzle_chain(ch)
    
    mudsys.add_cmd("start_puzzle", None, cmd_start_puzzle, "player", 1)

puzzle_solving_chain()

class EventScheduler:
    """Advanced event scheduling system."""
    
    def __init__(self):
        self.scheduled_events = {}
        self.event_counter = 0
    
    def schedule_event(self, delay, callback, *args, **kwargs):
        """Schedule a single event and return its ID."""
        
        self.event_counter += 1
        event_id = self.event_counter
        
        event_data = {
            "callback": callback,
            "args": args,
            "kwargs": kwargs,
            "scheduled_time": mudsys.current_time() + delay
        }
        
        self.scheduled_events[event_id] = event_data
        
        # Schedule the event
        event.start_event(None, delay, self.execute_scheduled_event, event_id)
        
        return event_id
    
    def cancel_event(self, event_id):
        """Cancel a scheduled event."""
        if event_id in self.scheduled_events:
            del self.scheduled_events[event_id]
    
    def execute_scheduled_event(self, event_id):
        """Execute a scheduled event."""
        
        if event_id not in self.scheduled_events:
            return
        
        event_data = self.scheduled_events[event_id]
        
        try:
            callback = event_data["callback"]
            args = event_data["args"]
            kwargs = event_data["kwargs"]
            
            callback(*args, **kwargs)
        
        except Exception as e:
            mudsys.log_string(f"Error executing scheduled event {event_id}: {e}")
        
        finally:
            # Remove the event
            del self.scheduled_events[event_id]
    
    def get_scheduled_events(self):
        """Get list of currently scheduled events."""
        return list(self.scheduled_events.keys())

# Global event scheduler
event_scheduler = EventScheduler()
```

## Step 6: Performance Optimization

Optimize event systems for better performance:

```python
# Add to advanced_event_systems.py

class EventPerformanceManager:
    """Manage performance for event systems."""
    
    @staticmethod
    def batch_events(event_list, batch_size=5):
        """Process events in batches to reduce load."""
        
        for i in range(0, len(event_list), batch_size):
            batch = event_list[i:i + batch_size]
            
            for event_func in batch:
                try:
                    event_func()
                except Exception as e:
                    mudsys.log_string(f"Error in batched event: {e}")
    
    @staticmethod
    def cleanup_expired_events():
        """Clean up expired event data."""
        
        current_time = mudsys.current_time()
        
        # Clean up quest system
        expired_quests = []
        for quest_key, quest_data in quest_system.active_quests.items():
            if quest_data["start_time"] + quest_data["time_limit"] < current_time:
                expired_quests.append(quest_key)
        
        for quest_key in expired_quests:
            del quest_system.active_quests[quest_key]
        
        # Clean up scheduled events
        expired_events = []
        for event_id, event_data in event_scheduler.scheduled_events.items():
            if event_data["scheduled_time"] < current_time - 3600:  # 1 hour old
                expired_events.append(event_id)
        
        for event_id in expired_events:
            del event_scheduler.scheduled_events[event_id]
    
    @staticmethod
    def monitor_event_load():
        """Monitor and log event system load."""
        
        active_quests = len(quest_system.active_quests)
        scheduled_events = len(event_scheduler.scheduled_events)
        recurring_events = len(recurring_manager.recurring_events)
        
        total_events = active_quests + scheduled_events + recurring_events
        
        if total_events > 100:  # Threshold for high load
            mudsys.log_string(f"High event load detected: {total_events} active events")
        
        return total_events

def setup_performance_monitoring():
    """Set up performance monitoring for event systems."""
    
    def performance_check():
        """Regular performance check."""
        
        # Monitor load
        EventPerformanceManager.monitor_event_load()
        
        # Clean up expired events
        EventPerformanceManager.cleanup_expired_events()
    
    # Schedule regular performance checks (every 10 minutes)
    recurring_manager.add_recurring_event("performance_check", None, 600, performance_check)

setup_performance_monitoring()

def cmd_event_status(ch, cmd, arg):
    """Command to check event system status."""
    
    if not char.charIsWizard(ch):
        char.charSend(ch, "You don't have permission to use this command.")
        return
    
    active_quests = len(quest_system.active_quests)
    scheduled_events = len(event_scheduler.scheduled_events)
    recurring_events = len(recurring_manager.recurring_events)
    
    char.charSend(ch, "Event System Status:")
    char.charSend(ch, f"Active Quests: {active_quests}")
    char.charSend(ch, f"Scheduled Events: {scheduled_events}")
    char.charSend(ch, f"Recurring Events: {recurring_events}")
    char.charSend(ch, f"Total Events: {active_quests + scheduled_events + recurring_events}")

mudsys.add_cmd("event_status", None, cmd_event_status, "wizard", 1)
```

## Best Practices for Event Systems

### 1. Always Handle Errors
Wrap event callbacks in try-catch blocks:

```python
def safe_event_callback(target, *args):
    try:
        # Your event logic here
        pass
    except Exception as e:
        mudsys.log_string(f"Error in event callback: {e}")
```

### 2. Clean Up Event Data
Remove expired or completed event data:

```python
def cleanup_event_data():
    # Remove old auxiliary data
    # Cancel unnecessary events
    # Clean up temporary states
    pass
```

### 3. Use Appropriate Delays
Don't overwhelm the system with too many rapid events:

```python
# Good: Reasonable delays
event.start_event(target, 5, callback)  # 5 seconds

# Bad: Too rapid
event.start_event(target, 0.1, callback)  # 0.1 seconds
```

### 4. Validate Event Targets
Always check that event targets still exist:

```python
def event_callback(target):
    if not target:
        return
    
    # Check if target still exists in the game
    if not char.charExists(target):  # Hypothetical function
        return
    
    # Your event logic here
```

## Next Steps

Now that you understand the event system:

1. **Complete task 4.2** and move on to **advanced scripting examples**
2. **Integrate events with your NPC, room, and object systems**
3. **Create complete game mechanics using event-driven design**

## Summary

You've learned to:
- Use the basic event system for timed actions
- Create complex event sequences and chains
- Build recurring events and schedules
- Implement event-driven game mechanics
- Use advanced event patterns like conditional chains
- Optimize event systems for performance

## Troubleshooting

**Events not firing?**
- Check that the target object still exists
- Verify the callback function is defined correctly
- Look for errors in mud logs

**Too many events causing lag?**
- Reduce event frequency
- Use batching for multiple similar events
- Clean up expired event data regularly

**Event sequences not working?**
- Verify each step in the sequence individually
- Check that conditions are being evaluated correctly
- Add debug logging to trace sequence execution

Ready for advanced scripting examples? You've completed the intermediate tutorials!