---
layout: default
title: Complex Room Interactions
parent: Build Complexity
grand_parent: Tutorials
nav_order: 2
permalink: /tutorials/complex-room-interactions/
---

# Complex Room Interactions

Learn to create sophisticated environmental systems with dynamic room behaviors, interactive elements, and complex trigger interactions.

## Overview

This tutorial builds on basic room creation to develop advanced environmental systems. You'll create rooms with dynamic weather, interactive puzzles, environmental hazards, and complex multi-room systems that respond intelligently to player actions.

## Prerequisites

- Completed [Building Your First Room](building-your-first-room/)
- Completed [Basic Triggers and Scripts](basic-triggers-scripts/)
- Understanding of [Auxiliary Data](/core-concepts/auxiliary-data/)
- Intermediate Python programming skills

## What You'll Learn

- Creating dynamic environmental systems
- Building interactive room puzzles
- Implementing environmental hazards and effects
- Creating multi-room interactive systems
- Managing complex room state
- Performance optimization for room systems

## Step 1: Dynamic Environmental Systems

Let's create a room with a sophisticated weather system that affects gameplay:

```python
# File: lib/pymodules/complex_room_systems.py

import mudsys
import char
import room
import auxiliary
import random
import event

class EnvironmentalSystem:
    """Manage complex environmental effects for rooms."""
    
    def __init__(self, rm):
        self.room = rm
        self.room_name = room.roomGetName(rm)
    
    def get_room_state(self, key, default=None):
        """Get room state from auxiliary data."""
        value = auxiliary.roomGetAuxiliaryData(self.room, key)
        return value if value is not None else default
    
    def set_room_state(self, key, value):
        """Set room state in auxiliary data."""
        auxiliary.roomSetAuxiliaryData(self.room, key, str(value))
    
    def get_numeric_state(self, key, default=0):
        """Get numeric room state."""
        value = self.get_room_state(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def modify_state(self, key, delta, min_val=None, max_val=None):
        """Modify numeric room state."""
        current = self.get_numeric_state(key, 0)
        new_value = current + delta
        
        if min_val is not None:
            new_value = max(new_value, min_val)
        if max_val is not None:
            new_value = min(new_value, max_val)
        
        self.set_room_state(key, new_value)
        return new_value

def dynamic_weather_system(rm):
    """Advanced weather system that affects room conditions."""
    
    env = EnvironmentalSystem(rm)
    
    # Weather parameters (0-100 scale)
    temperature = env.get_numeric_state("temperature", 70)
    humidity = env.get_numeric_state("humidity", 50)
    wind_speed = env.get_numeric_state("wind_speed", 20)
    precipitation = env.get_numeric_state("precipitation", 0)
    
    # Weather changes over time
    if random.randint(1, 10) == 1:  # Change weather occasionally
        # Temperature changes
        temp_change = random.randint(-3, 3)
        new_temp = env.modify_state("temperature", temp_change, 0, 120)
        
        # Humidity changes (affected by temperature)
        humidity_change = random.randint(-5, 5)
        if new_temp > 80:
            humidity_change += 2  # Hot weather increases humidity
        elif new_temp < 40:
            humidity_change -= 2  # Cold weather decreases humidity
        
        new_humidity = env.modify_state("humidity", humidity_change, 0, 100)
        
        # Wind speed changes
        wind_change = random.randint(-5, 5)
        new_wind = env.modify_state("wind_speed", wind_change, 0, 100)
        
        # Precipitation (affected by humidity and temperature)
        precip_change = 0
        if new_humidity > 80 and new_temp > 32:
            precip_change = random.randint(0, 10)  # Rain likely
        elif new_humidity > 90 and new_temp < 32:
            precip_change = random.randint(0, 8)   # Snow likely
        else:
            precip_change = random.randint(-5, 2)  # Generally decreasing
        
        new_precip = env.modify_state("precipitation", precip_change, 0, 100)
        
        # Apply weather effects to players in the room
        apply_weather_effects(rm, new_temp, new_humidity, new_wind, new_precip)

def apply_weather_effects(rm, temperature, humidity, wind_speed, precipitation):
    """Apply weather effects to players in the room."""
    
    chars_in_room = room.roomGetChars(rm)
    players = [c for c in chars_in_room if not char.charIsNPC(c)]
    
    if not players:
        return
    
    # Determine weather description and effects
    weather_desc = get_weather_description(temperature, humidity, wind_speed, precipitation)
    
    # Send weather updates occasionally
    if random.randint(1, 15) == 1:
        room.roomSendMessage(rm, weather_desc)
    
    # Apply gameplay effects
    for player in players:
        apply_weather_to_player(player, temperature, humidity, wind_speed, precipitation)

def get_weather_description(temperature, humidity, wind_speed, precipitation):
    """Generate weather description based on conditions."""
    
    descriptions = []
    
    # Temperature descriptions
    if temperature > 90:
        descriptions.append("The air shimmers with intense heat")
    elif temperature > 75:
        descriptions.append("The weather is pleasantly warm")
    elif temperature > 50:
        descriptions.append("The temperature is comfortable")
    elif temperature > 32:
        descriptions.append("There's a chill in the air")
    else:
        descriptions.append("The cold is biting and harsh")
    
    # Precipitation descriptions
    if precipitation > 80:
        if temperature > 32:
            descriptions.append("Heavy rain pounds down relentlessly")
        else:
            descriptions.append("Snow falls heavily, reducing visibility")
    elif precipitation > 50:
        if temperature > 32:
            descriptions.append("Steady rain falls from the cloudy sky")
        else:
            descriptions.append("Light snow drifts down gently")
    elif precipitation > 20:
        descriptions.append("A light drizzle mists the area")
    
    # Wind descriptions
    if wind_speed > 70:
        descriptions.append("Fierce winds howl and buffet everything")
    elif wind_speed > 40:
        descriptions.append("Strong winds blow steadily")
    elif wind_speed > 20:
        descriptions.append("A gentle breeze stirs the air")
    
    if descriptions:
        return ". ".join(descriptions) + "."
    else:
        return "The weather is calm and unremarkable."

def apply_weather_to_player(player, temperature, humidity, wind_speed, precipitation):
    """Apply weather effects to individual players."""
    
    player_name = char.charGetName(player)
    
    # Extreme weather effects
    if temperature > 100 and random.randint(1, 20) == 1:
        char.charSend(player, "The extreme heat makes you feel dizzy and weak.")
        # In a real implementation, this might affect player stats
        
    elif temperature < 20 and random.randint(1, 25) == 1:
        char.charSend(player, "The bitter cold numbs your fingers and toes.")
        
    if precipitation > 80 and wind_speed > 60 and random.randint(1, 30) == 1:
        char.charSend(player, "The storm is so intense you can barely see or hear anything!")
        # This might affect player's ability to see room descriptions or hear speech
        
    # Beneficial weather effects
    if 65 <= temperature <= 75 and humidity < 60 and wind_speed < 30 and precipitation == 0:
        if random.randint(1, 50) == 1:
            char.charSend(player, "The perfect weather makes you feel refreshed and energized.")

# Register weather system
mudsys.add_room_method("dynamic_weather", dynamic_weather_system)
```

## Step 2: Interactive Room Puzzles

Create complex puzzles that span multiple interactions:

```python
# Add to complex_room_systems.py

class RoomPuzzleSystem:
    """Manage complex room-based puzzles."""
    
    def __init__(self, rm):
        self.room = rm
        self.env = EnvironmentalSystem(rm)
    
    def initialize_puzzle(self, puzzle_type):
        """Initialize a puzzle in the room."""
        self.env.set_room_state("puzzle_type", puzzle_type)
        self.env.set_room_state("puzzle_state", "initialized")
        self.env.set_room_state("puzzle_progress", 0)
        
        # Initialize puzzle-specific data
        if puzzle_type == "crystal_alignment":
            self.initialize_crystal_puzzle()
        elif puzzle_type == "elemental_balance":
            self.initialize_elemental_puzzle()
    
    def initialize_crystal_puzzle(self):
        """Initialize the crystal alignment puzzle."""
        # Set up 5 crystals with random initial positions
        crystal_positions = []
        for i in range(5):
            position = random.randint(0, 7)  # 8 possible positions
            crystal_positions.append(str(position))
        
        self.env.set_room_state("crystal_positions", ",".join(crystal_positions))
        
        # Set the target pattern (solution)
        target_pattern = "2,4,6,1,3"  # Specific pattern needed to solve
        self.env.set_room_state("crystal_target", target_pattern)
        
        # Track which crystals have been moved
        self.env.set_room_state("crystals_moved", "0,0,0,0,0")
    
    def initialize_elemental_puzzle(self):
        """Initialize the elemental balance puzzle."""
        # Set up elemental energies (fire, water, earth, air)
        elements = ["fire", "water", "earth", "air"]
        for element in elements:
            # Random starting energy level (0-100)
            energy = random.randint(20, 80)
            self.env.set_room_state(f"energy_{element}", energy)
        
        # Set target balance (all elements should be around 50)
        self.env.set_room_state("target_balance", 50)
        self.env.set_room_state("balance_tolerance", 10)

def crystal_puzzle_interaction(rm, actor, action, target):
    """Handle interactions with the crystal alignment puzzle."""
    
    puzzle = RoomPuzzleSystem(rm)
    actor_name = char.charGetName(actor)
    
    # Check if this is a crystal puzzle room
    puzzle_type = puzzle.env.get_room_state("puzzle_type")
    if puzzle_type != "crystal_alignment":
        return False
    
    # Handle crystal-related actions
    if action == "touch" and target and "crystal" in target.lower():
        # Determine which crystal (1-5)
        crystal_num = None
        for i in range(1, 6):
            if str(i) in target or ["first", "second", "third", "fourth", "fifth"][i-1] in target.lower():
                crystal_num = i
                break
        
        if crystal_num is None:
            char.charSend(actor, "Which crystal do you want to touch? (first, second, third, fourth, or fifth)")
            return True
        
        # Move the crystal
        return move_crystal(rm, actor, crystal_num)
    
    elif action == "look" and target and "crystal" in target.lower():
        return describe_crystals(rm, actor)
    
    elif action == "examine" and target and "pattern" in target.lower():
        return show_crystal_pattern(rm, actor)
    
    return False

def move_crystal(rm, actor, crystal_num):
    """Move a specific crystal in the puzzle."""
    
    puzzle = RoomPuzzleSystem(rm)
    actor_name = char.charGetName(actor)
    
    # Get current crystal positions
    positions_str = puzzle.env.get_room_state("crystal_positions", "0,0,0,0,0")
    positions = [int(x) for x in positions_str.split(",")]
    
    # Move the crystal to the next position (rotate through 8 positions)
    old_position = positions[crystal_num - 1]
    new_position = (old_position + 1) % 8
    positions[crystal_num - 1] = new_position
    
    # Update positions
    puzzle.env.set_room_state("crystal_positions", ",".join(str(x) for x in positions))
    
    # Mark this crystal as moved
    moved_str = puzzle.env.get_room_state("crystals_moved", "0,0,0,0,0")
    moved = [int(x) for x in moved_str.split(",")]
    moved[crystal_num - 1] = 1
    puzzle.env.set_room_state("crystals_moved", ",".join(str(x) for x in moved))
    
    # Describe the movement
    position_names = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]
    char.charSend(actor, f"You touch the {['first', 'second', 'third', 'fourth', 'fifth'][crystal_num-1]} crystal. It glows briefly and rotates to face {position_names[new_position]}.")
    char.charSendRoom(actor, f"{actor_name} touches a crystal, causing it to glow and rotate.")
    
    # Check if puzzle is solved
    check_crystal_puzzle_solution(rm, actor)
    
    return True

def check_crystal_puzzle_solution(rm, actor):
    """Check if the crystal puzzle has been solved."""
    
    puzzle = RoomPuzzleSystem(rm)
    
    # Get current and target positions
    current_str = puzzle.env.get_room_state("crystal_positions", "0,0,0,0,0")
    target_str = puzzle.env.get_room_state("crystal_target", "2,4,6,1,3")
    
    if current_str == target_str:
        # Puzzle solved!
        puzzle.env.set_room_state("puzzle_state", "solved")
        
        room.roomSendMessage(rm, "The crystals suddenly blaze with brilliant light!")
        room.roomSendMessage(rm, "The crystal pattern is complete! A hidden passage opens in the north wall!")
        
        # Create the new exit (this would need actual exit creation code)
        char.charSend(actor, "Congratulations! You have solved the Crystal Alignment puzzle!")
        
        # Log the achievement
        mudsys.log_string(f"Player {char.charGetName(actor)} solved the crystal alignment puzzle!")
        
        return True
    
    return False

def describe_crystals(rm, actor):
    """Describe the current state of the crystals."""
    
    puzzle = RoomPuzzleSystem(rm)
    
    positions_str = puzzle.env.get_room_state("crystal_positions", "0,0,0,0,0")
    positions = [int(x) for x in positions_str.split(",")]
    
    position_names = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]
    crystal_names = ["first", "second", "third", "fourth", "fifth"]
    
    description = "The five crystals are arranged in a circle around the room:\n"
    
    for i, position in enumerate(positions):
        crystal_color = ["red", "blue", "green", "yellow", "purple"][i]
        description += f"The {crystal_names[i]} ({crystal_color}) crystal faces {position_names[position]}.\n"
    
    char.charSend(actor, description)
    char.charSend(actor, "You can 'touch <crystal>' to rotate them. Try to find the correct pattern!")
    
    return True

# Register crystal puzzle functions
mudsys.add_room_method("crystal_puzzle", crystal_puzzle_interaction)
```

## Step 3: Environmental Hazards and Effects

Create rooms with dangerous or beneficial environmental effects:

```python
# Add to complex_room_systems.py

class EnvironmentalHazards:
    """Manage environmental hazards and effects."""
    
    def __init__(self, rm):
        self.room = rm
        self.env = EnvironmentalSystem(rm)
    
    def initialize_hazards(self, hazard_types):
        """Initialize environmental hazards in the room."""
        self.env.set_room_state("hazard_types", ",".join(hazard_types))
        
        for hazard in hazard_types:
            self.env.set_room_state(f"hazard_{hazard}_intensity", 50)
            self.env.set_room_state(f"hazard_{hazard}_last_trigger", 0)

def volcanic_chamber_hazards(rm):
    """Manage hazards in a volcanic chamber."""
    
    hazards = EnvironmentalHazards(rm)
    
    # Get current hazard levels
    lava_intensity = hazards.env.get_numeric_state("hazard_lava_intensity", 30)
    gas_intensity = hazards.env.get_numeric_state("hazard_gas_intensity", 20)
    heat_intensity = hazards.env.get_numeric_state("hazard_heat_intensity", 60)
    
    # Hazard levels fluctuate over time
    if random.randint(1, 8) == 1:
        # Lava activity changes
        lava_change = random.randint(-10, 15)
        new_lava = hazards.env.modify_state("hazard_lava_intensity", lava_change, 0, 100)
        
        # Gas levels affected by lava activity
        gas_change = lava_change // 2 + random.randint(-5, 5)
        new_gas = hazards.env.modify_state("hazard_gas_intensity", gas_change, 0, 100)
        
        # Heat affected by both lava and gas
        heat_change = (lava_change + gas_change) // 3 + random.randint(-3, 3)
        new_heat = hazards.env.modify_state("hazard_heat_intensity", heat_change, 20, 100)
        
        # Announce significant changes
        if abs(lava_change) > 10:
            if lava_change > 0:
                room.roomSendMessage(rm, "The lava bubbles more violently, sending up sprays of molten rock!")
            else:
                room.roomSendMessage(rm, "The lava calms somewhat, though it still glows menacingly.")
        
        if new_gas > 70 and random.randint(1, 3) == 1:
            room.roomSendMessage(rm, "Toxic gases hiss from cracks in the volcanic rock!")
        
        if new_heat > 85 and random.randint(1, 4) == 1:
            room.roomSendMessage(rm, "The intense heat makes the air shimmer and waver.")
    
    # Apply hazard effects to players
    chars_in_room = room.roomGetChars(rm)
    players = [c for c in chars_in_room if not char.charIsNPC(c)]
    
    for player in players:
        apply_volcanic_hazards(player, new_lava, new_gas, new_heat)

def apply_volcanic_hazards(player, lava_intensity, gas_intensity, heat_intensity):
    """Apply volcanic hazards to a player."""
    
    player_name = char.charGetName(player)
    
    # Lava hazards
    if lava_intensity > 80 and random.randint(1, 20) == 1:
        char.charSend(player, "A spray of lava barely misses you! You feel the intense heat on your skin.")
        char.charSendRoom(player, f"{player_name} dodges a spray of molten lava!")
        # In a real implementation, this might cause damage
    
    elif lava_intensity > 60 and random.randint(1, 30) == 1:
        char.charSend(player, "The bubbling lava makes you nervous. You step back from the edge.")
    
    # Gas hazards
    if gas_intensity > 70 and random.randint(1, 15) == 1:
        char.charSend(player, "You cough as toxic gases burn your throat and lungs!")
        char.charSendRoom(player, f"{player_name} coughs violently from the toxic gases.")
        # This might cause poison damage or status effects
    
    elif gas_intensity > 50 and random.randint(1, 25) == 1:
        char.charSend(player, "The acrid smell of volcanic gases makes your eyes water.")
    
    # Heat hazards
    if heat_intensity > 90 and random.randint(1, 12) == 1:
        char.charSend(player, "The extreme heat is overwhelming! You feel dizzy and weak.")
        # This might cause fatigue or heat exhaustion
    
    elif heat_intensity > 75 and random.randint(1, 20) == 1:
        char.charSend(player, "Sweat pours down your face from the intense heat.")

def healing_spring_benefits(rm):
    """Manage beneficial effects from a healing spring."""
    
    env = EnvironmentalSystem(rm)
    
    # Get spring power level
    spring_power = env.get_numeric_state("spring_power", 70)
    
    # Spring power fluctuates slightly
    if random.randint(1, 10) == 1:
        power_change = random.randint(-5, 5)
        new_power = env.modify_state("spring_power", power_change, 30, 100)
        
        if new_power > 90 and random.randint(1, 5) == 1:
            room.roomSendMessage(rm, "The healing spring glows with exceptional power!")
        elif new_power < 40 and random.randint(1, 5) == 1:
            room.roomSendMessage(rm, "The healing spring's glow seems dimmer than usual.")
    
    # Apply healing effects
    chars_in_room = room.roomGetChars(rm)
    players = [c for c in chars_in_room if not char.charIsNPC(c)]
    
    for player in players:
        apply_healing_spring_effects(player, new_power)

def apply_healing_spring_effects(player, spring_power):
    """Apply healing spring effects to a player."""
    
    player_name = char.charGetName(player)
    
    # Healing effects based on spring power
    if spring_power > 80 and random.randint(1, 8) == 1:
        char.charSend(player, "The magical spring's mist envelops you, healing your wounds!")
        char.charSendRoom(player, f"Healing mist swirls around {player_name}.")
        # This would actually heal the player
    
    elif spring_power > 60 and random.randint(1, 12) == 1:
        char.charSend(player, "You feel refreshed by the spring's gentle energy.")
    
    elif spring_power > 40 and random.randint(1, 20) == 1:
        char.charSend(player, "The spring's presence makes you feel slightly better.")
    
    # Cleansing effects
    if spring_power > 70 and random.randint(1, 15) == 1:
        char.charSend(player, "The spring's pure energy cleanses you of ailments.")
        # This might cure poison, disease, or other negative effects

# Register hazard systems
mudsys.add_room_method("volcanic_hazards", volcanic_chamber_hazards)
mudsys.add_room_method("healing_spring", healing_spring_benefits)
```

## Step 4: Multi-Room Interactive Systems

Create systems that span multiple connected rooms:

```python
# Add to complex_room_systems.py

class MultiRoomSystem:
    """Manage systems that span multiple rooms."""
    
    def __init__(self, system_id):
        self.system_id = system_id
        self.rooms = []
    
    def add_room(self, rm):
        """Add a room to this multi-room system."""
        self.rooms.append(rm)
        
        # Mark the room as part of this system
        env = EnvironmentalSystem(rm)
        env.set_room_state("multi_room_system", self.system_id)
    
    def get_system_state(self, key, default=None):
        """Get system-wide state (stored in first room)."""
        if not self.rooms:
            return default
        
        env = EnvironmentalSystem(self.rooms[0])
        return env.get_room_state(f"system_{self.system_id}_{key}", default)
    
    def set_system_state(self, key, value):
        """Set system-wide state (stored in first room)."""
        if not self.rooms:
            return
        
        env = EnvironmentalSystem(self.rooms[0])
        env.set_room_state(f"system_{self.system_id}_{key}", value)
    
    def broadcast_to_system(self, message):
        """Send a message to all rooms in the system."""
        for rm in self.rooms:
            room.roomSendMessage(rm, message)

def temple_pressure_plate_system(rm, actor, action):
    """Multi-room pressure plate puzzle system."""
    
    # Get the system this room belongs to
    env = EnvironmentalSystem(rm)
    system_id = env.get_room_state("multi_room_system")
    
    if not system_id or system_id != "temple_pressure_plates":
        return False
    
    if action != "step" and action != "stand":
        return False
    
    actor_name = char.charGetName(actor)
    
    # Get room's plate number
    plate_number = env.get_numeric_state("plate_number", 0)
    if plate_number == 0:
        return False
    
    # Create multi-room system instance
    system = MultiRoomSystem("temple_pressure_plates")
    # In a real implementation, you'd load all rooms in the system
    system.add_room(rm)
    
    # Record that this plate has been activated
    current_sequence = system.get_system_state("activation_sequence", "")
    if current_sequence:
        sequence_list = current_sequence.split(",")
    else:
        sequence_list = []
    
    # Add this plate to the sequence
    sequence_list.append(str(plate_number))
    system.set_system_state("activation_sequence", ",".join(sequence_list))
    
    # Announce the activation
    char.charSend(actor, f"You step on the pressure plate. It glows with ancient energy!")
    char.charSendRoom(actor, f"{actor_name} steps on a glowing pressure plate.")
    
    # Check if the sequence is correct
    correct_sequence = "1,3,2,4"  # The correct order
    current_sequence = ",".join(sequence_list)
    
    if current_sequence == correct_sequence:
        # Puzzle solved!
        system.broadcast_to_system("The temple trembles as ancient mechanisms activate!")
        system.broadcast_to_system("A hidden chamber opens in the center of the temple!")
        system.set_system_state("puzzle_solved", "true")
        
        mudsys.log_string(f"Player {actor_name} solved the temple pressure plate puzzle!")
        
    elif len(sequence_list) >= 4:
        # Wrong sequence, reset
        system.set_system_state("activation_sequence", "")
        system.broadcast_to_system("The pressure plates dim and reset. Try again!")
    
    return True

def magical_barrier_network(rm):
    """Network of magical barriers that affect each other."""
    
    env = EnvironmentalSystem(rm)
    system_id = env.get_room_state("multi_room_system")
    
    if system_id != "barrier_network":
        return
    
    # Get this room's barrier strength
    barrier_strength = env.get_numeric_state("barrier_strength", 100)
    barrier_id = env.get_numeric_state("barrier_id", 1)
    
    # Barriers fluctuate and affect each other
    if random.randint(1, 15) == 1:
        # This barrier's strength changes
        strength_change = random.randint(-5, 5)
        new_strength = env.modify_state("barrier_strength", strength_change, 0, 100)
        
        # Announce significant changes
        if new_strength <= 0 and barrier_strength > 0:
            room.roomSendMessage(rm, "The magical barrier flickers and fails!")
            # This barrier failing might affect others in the network
            affect_connected_barriers(rm, barrier_id, -20)
            
        elif new_strength >= 100 and barrier_strength < 100:
            room.roomSendMessage(rm, "The magical barrier blazes with full power!")
            # This barrier at full power might strengthen others
            affect_connected_barriers(rm, barrier_id, 10)
        
        elif abs(strength_change) > 3:
            if strength_change > 0:
                room.roomSendMessage(rm, "The magical barrier grows stronger.")
            else:
                room.roomSendMessage(rm, "The magical barrier weakens.")

def affect_connected_barriers(source_room, source_barrier_id, effect_strength):
    """Affect other barriers in the network."""
    
    # In a real implementation, you'd find all connected rooms
    # For now, this is a placeholder that would propagate effects
    # to other rooms in the barrier network
    
    mudsys.log_string(f"Barrier {source_barrier_id} affecting network with strength {effect_strength}")

# Register multi-room systems
mudsys.add_room_method("pressure_plate_system", temple_pressure_plate_system)
mudsys.add_room_method("barrier_network", magical_barrier_network)
```

## Step 5: Performance Optimization for Complex Rooms

Optimize room systems for better performance:

```python
# Add to complex_room_systems.py

class RoomPerformanceManager:
    """Manage performance for complex room systems."""
    
    @staticmethod
    def should_process_room_effects(rm, base_chance=20):
        """Determine if room effects should process this heartbeat."""
        
        # Don't process if no players are present
        chars_in_room = room.roomGetChars(rm)
        players_present = any(not char.charIsNPC(c) for c in chars_in_room)
        
        if not players_present:
            return False
        
        # Use random chance to distribute processing load
        return random.randint(1, 100) <= base_chance
    
    @staticmethod
    def cleanup_room_data(rm, max_age_hours=48):
        """Clean up old room auxiliary data."""
        
        # This would implement cleanup of old room data
        # For now, just a placeholder
        current_time = mudsys.current_time()
        
        # Clean up old interaction logs, temporary states, etc.
        pass
    
    @staticmethod
    def batch_process_rooms(room_list, process_function):
        """Process multiple rooms in batches."""
        
        batch_size = 3  # Process 3 rooms per call
        
        for i in range(0, len(room_list), batch_size):
            batch = room_list[i:i + batch_size]
            for rm in batch:
                try:
                    process_function(rm)
                except Exception as e:
                    room_name = room.roomGetName(rm) if rm else "Unknown"
                    mudsys.log_string(f"Error processing room {room_name}: {e}")

def optimized_complex_room_heartbeat(rm):
    """Optimized heartbeat for complex room systems."""
    
    # Only process complex effects occasionally
    if not RoomPerformanceManager.should_process_room_effects(rm, 25):
        return
    
    try:
        # Get room's system types
        env = EnvironmentalSystem(rm)
        system_types = env.get_room_state("system_types", "")
        
        if not system_types:
            return
        
        systems = system_types.split(",")
        
        # Process each system type
        for system_type in systems:
            if system_type == "weather":
                dynamic_weather_system(rm)
            elif system_type == "volcanic":
                volcanic_chamber_hazards(rm)
            elif system_type == "healing":
                healing_spring_benefits(rm)
            elif system_type == "barrier_network":
                magical_barrier_network(rm)
        
        # Occasionally clean up old data
        if random.randint(1, 200) == 1:
            RoomPerformanceManager.cleanup_room_data(rm)
    
    except Exception as e:
        room_name = room.roomGetName(rm) if rm else "Unknown"
        mudsys.log_string(f"Error in complex room heartbeat for {room_name}: {e}")

# Register optimized heartbeat
mudsys.add_room_method("optimized_complex_heartbeat", optimized_complex_room_heartbeat)
```

## Step 6: Room System Configuration

Create a system to easily configure complex room behaviors:

```python
# Add to complex_room_systems.py

def configure_room_systems(rm, config):
    """Configure complex systems for a room based on configuration."""
    
    env = EnvironmentalSystem(rm)
    
    # Set up system types
    system_types = []
    
    if "weather" in config:
        system_types.append("weather")
        weather_config = config["weather"]
        
        # Initialize weather parameters
        env.set_room_state("temperature", weather_config.get("initial_temp", 70))
        env.set_room_state("humidity", weather_config.get("initial_humidity", 50))
        env.set_room_state("wind_speed", weather_config.get("initial_wind", 20))
        env.set_room_state("precipitation", weather_config.get("initial_precip", 0))
    
    if "hazards" in config:
        hazard_config = config["hazards"]
        
        if "volcanic" in hazard_config:
            system_types.append("volcanic")
            env.set_room_state("hazard_lava_intensity", hazard_config["volcanic"].get("lava", 30))
            env.set_room_state("hazard_gas_intensity", hazard_config["volcanic"].get("gas", 20))
            env.set_room_state("hazard_heat_intensity", hazard_config["volcanic"].get("heat", 60))
    
    if "benefits" in config:
        benefit_config = config["benefits"]
        
        if "healing" in benefit_config:
            system_types.append("healing")
            env.set_room_state("spring_power", benefit_config["healing"].get("power", 70))
    
    if "puzzles" in config:
        puzzle_config = config["puzzles"]
        
        if "crystal_alignment" in puzzle_config:
            puzzle = RoomPuzzleSystem(rm)
            puzzle.initialize_puzzle("crystal_alignment")
    
    # Store system types for the heartbeat function
    env.set_room_state("system_types", ",".join(system_types))

# Example configuration function
def setup_example_rooms():
    """Set up example rooms with complex systems."""
    
    # This would be called during mud initialization
    # to set up rooms with complex systems
    
    # Example configurations
    volcanic_chamber_config = {
        "weather": {
            "initial_temp": 95,
            "initial_humidity": 30,
            "initial_wind": 10,
            "initial_precip": 0
        },
        "hazards": {
            "volcanic": {
                "lava": 60,
                "gas": 40,
                "heat": 85
            }
        }
    }
    
    healing_grove_config = {
        "weather": {
            "initial_temp": 75,
            "initial_humidity": 60,
            "initial_wind": 15,
            "initial_precip": 10
        },
        "benefits": {
            "healing": {
                "power": 80
            }
        }
    }
    
    puzzle_chamber_config = {
        "puzzles": {
            "crystal_alignment": {}
        }
    }
    
    # In a real implementation, you'd apply these configs to actual rooms
    mudsys.log_string("Complex room systems configured")

# Command to configure room systems (for wizards)
def cmd_configure_room(ch, cmd, arg):
    """Command to configure complex room systems."""
    
    if not char.charIsWizard(ch):
        char.charSend(ch, "You don't have permission to use this command.")
        return
    
    if not arg:
        char.charSend(ch, "Usage: configure_room <system_type>")
        char.charSend(ch, "Available systems: weather, volcanic, healing, crystal_puzzle")
        return
    
    rm = char.charGetRoom(ch)
    if not rm:
        char.charSend(ch, "You must be in a room to configure it.")
        return
    
    system_type = arg.lower().strip()
    
    if system_type == "weather":
        config = {"weather": {"initial_temp": 70, "initial_humidity": 50}}
        configure_room_systems(rm, config)
        char.charSend(ch, "Weather system configured for this room.")
        
    elif system_type == "volcanic":
        config = {"hazards": {"volcanic": {"lava": 50, "gas": 30, "heat": 70}}}
        configure_room_systems(rm, config)
        char.charSend(ch, "Volcanic hazard system configured for this room.")
        
    elif system_type == "healing":
        config = {"benefits": {"healing": {"power": 75}}}
        configure_room_systems(rm, config)
        char.charSend(ch, "Healing spring system configured for this room.")
        
    elif system_type == "crystal_puzzle":
        config = {"puzzles": {"crystal_alignment": {}}}
        configure_room_systems(rm, config)
        char.charSend(ch, "Crystal alignment puzzle configured for this room.")
        
    else:
        char.charSend(ch, "Unknown system type. Available: weather, volcanic, healing, crystal_puzzle")

mudsys.add_cmd("configure_room", None, cmd_configure_room, "wizard", 1)
```

## Best Practices for Complex Room Systems

### 1. Layer Complexity Gradually
Start with simple effects and add complexity over time:

```python
# Good: Start simple, add complexity
def simple_weather_room(rm):
    # Basic weather messages
    pass

def complex_weather_room(rm):
    # Call simple version first
    simple_weather_room(rm)
    # Add complex interactions
    pass
```

### 2. Use State Machines for Complex Interactions
Organize room states clearly:

```python
def room_state_machine(rm):
    current_state = get_room_state(rm, "room_state", "normal")
    
    if current_state == "normal":
        # Normal room behavior
        pass
    elif current_state == "puzzle_active":
        # Puzzle-solving behavior
        pass
    # etc.
```

### 3. Balance Immersion and Performance
Don't overwhelm players or the system:

```python
# Use random chances to limit message frequency
if random.randint(1, 30) == 1:
    # Atmospheric message
    pass
```

### 4. Provide Debug and Configuration Tools
Make it easy to test and adjust room systems:

```python
def cmd_room_debug(ch, cmd, arg):
    """Debug command for room systems."""
    # Show current room state, active systems, etc.
    pass
```

## Next Steps

Now that you understand complex room interactions:

1. **Try [Object Scripting and Item Types](object-scripting-item-types/)** for interactive items
2. **Learn [Using the Event System](using-event-system/)** for timed room effects
3. **Explore advanced system integration** for complete game mechanics

## Summary

You've learned to:
- Create dynamic environmental systems with weather and hazards
- Build complex interactive puzzles spanning multiple interactions
- Implement environmental hazards and beneficial effects
- Create multi-room systems with interconnected behaviors
- Optimize performance for complex room systems
- Configure and debug room systems effectively

## Troubleshooting

**Room effects not working?**
- Check that system types are properly configured
- Verify auxiliary data is being stored correctly
- Look for errors in mud logs

**Performance issues with complex rooms?**
- Reduce heartbeat frequency for expensive operations
- Use random chances to limit effect frequency
- Clean up old auxiliary data regularly

**Multi-room systems not synchronizing?**
- Verify all rooms are properly configured as part of the system
- Check that system state is being stored in a consistent location
- Test individual room components before connecting them

Ready for more advanced scripting? Continue with [Object Scripting and Item Types](object-scripting-item-types/)!