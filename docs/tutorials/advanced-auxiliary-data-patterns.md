---
layout: default
title: Advanced Auxiliary Data Patterns
parent: Create Systems
grand_parent: Tutorials
nav_order: 1
permalink: /tutorials/advanced-auxiliary-data-patterns/
---

# Advanced Auxiliary Data Patterns

*This tutorial is currently being developed and will be available soon.*

## Coming Soon

This tutorial will cover sophisticated auxiliary data techniques for complex game systems, including:

- Advanced data relationships and hierarchies
- Performance optimization strategies
- Complex state management patterns
- Integration with game systems

## Prerequisites

- Completed [Start with the Basics](../start-with-basics/) tutorials
- Understanding of [Auxiliary Data](/core-concepts/auxiliary-data/) concepts
- Experience with auxiliary data classes and storage system

## What You'll Learn

- Creating complex auxiliary data class hierarchies
- Managing data relationships between different game objects
- Performance optimization techniques for auxiliary data
- Advanced patterns for game system integration

*Check back soon for the complete tutorial, or see the [Examples section](/examples/auxiliary-data/) for working code examples.*

## Pattern 1: Hierarchical Data Structures

Use auxiliary data to create complex nested data structures for sophisticated game mechanics.

### Character Skill Trees

```python
# Advanced skill tree system using nested auxiliary data
import auxiliary
import json
import char

def initialize_skill_tree(character):
    """Initialize a complex skill tree structure."""
    
    skill_tree = {
        "combat": {
            "melee": {
                "level": 0,
                "experience": 0,
                "max_level": 100,
                "prerequisites": [],
                "bonuses": {
                    "damage_multiplier": 1.0,
                    "accuracy_bonus": 0
                },
                "abilities": {
                    "power_strike": {"unlocked": False, "level_required": 10},
                    "whirlwind": {"unlocked": False, "level_required": 25},
                    "berserker_rage": {"unlocked": False, "level_required": 50}
                }
            },
            "ranged": {
                "level": 0,
                "experience": 0,
                "max_level": 100,
                "prerequisites": [],
                "bonuses": {
                    "range_bonus": 0,
                    "critical_chance": 0.05
                },
                "abilities": {
                    "aimed_shot": {"unlocked": False, "level_required": 15},
                    "multi_shot": {"unlocked": False, "level_required": 30},
                    "piercing_arrow": {"unlocked": False, "level_required": 45}
                }
            }
        },
        "magic": {
            "elemental": {
                "fire": {"level": 0, "experience": 0, "spells": {}},
                "water": {"level": 0, "experience": 0, "spells": {}},
                "earth": {"level": 0, "experience": 0, "spells": {}},
                "air": {"level": 0, "experience": 0, "spells": {}}
            },
            "divine": {
                "healing": {"level": 0, "experience": 0, "spells": {}},
                "protection": {"level": 0, "experience": 0, "spells": {}},
                "blessing": {"level": 0, "experience": 0, "spells": {}}
            }
        },
        "crafting": {
            "smithing": {"level": 0, "recipes": [], "specializations": []},
            "alchemy": {"level": 0, "recipes": [], "research_points": 0},
            "enchanting": {"level": 0, "known_enchantments": [], "power_level": 1}
        }
    }
    
    auxiliary.charSetAuxiliaryData(character, "skill_tree", json.dumps(skill_tree))

def get_skill_data(character, skill_path):
    """Get data for a specific skill using dot notation path."""
    
    skill_tree_str = auxiliary.charGetAuxiliaryData(character, "skill_tree")
    if not skill_tree_str:
        return None
    
    try:
        skill_tree = json.loads(skill_tree_str)
        
        # Navigate the path (e.g., "combat.melee.level")
        current = skill_tree
        for part in skill_path.split('.'):
            if part in current:
                current = current[part]
            else:
                return None
        
        return current
    except (json.JSONDecodeError, KeyError):
        return None

def modify_skill_data(character, skill_path, value):
    """Modify a specific skill value using dot notation path."""
    
    skill_tree_str = auxiliary.charGetAuxiliaryData(character, "skill_tree")
    if not skill_tree_str:
        return False
    
    try:
        skill_tree = json.loads(skill_tree_str)
        
        # Navigate to parent and set the final key
        path_parts = skill_path.split('.')
        current = skill_tree
        
        for part in path_parts[:-1]:
            if part in current:
                current = current[part]
            else:
                return False
        
        # Set the final value
        current[path_parts[-1]] = value
        
        # Save back to auxiliary data
        auxiliary.charSetAuxiliaryData(character, "skill_tree", json.dumps(skill_tree))
        return True
        
    except (json.JSONDecodeError, KeyError):
        return False

def advance_skill(character, skill_path, experience_gained):
    """Advanced skill progression with automatic level calculation."""
    
    current_exp = get_skill_data(character, f"{skill_path}.experience") or 0
    current_level = get_skill_data(character, f"{skill_path}.level") or 0
    max_level = get_skill_data(character, f"{skill_path}.max_level") or 100
    
    new_exp = current_exp + experience_gained
    
    # Calculate new level (exponential curve)
    new_level = min(int((new_exp / 100) ** 0.5), max_level)
    
    # Update experience and level
    modify_skill_data(character, f"{skill_path}.experience", new_exp)
    
    if new_level > current_level:
        modify_skill_data(character, f"{skill_path}.level", new_level)
        
        # Check for ability unlocks
        check_ability_unlocks(character, skill_path, new_level)
        
        char.charSend(character, f"Your {skill_path.replace('.', ' ')} skill increased to level {new_level}!")
        return True
    
    return False

def check_ability_unlocks(character, skill_path, new_level):
    """Check and unlock abilities based on skill level."""
    
    abilities = get_skill_data(character, f"{skill_path}.abilities")
    if not abilities:
        return
    
    for ability_name, ability_data in abilities.items():
        if not ability_data.get("unlocked", False) and new_level >= ability_data.get("level_required", 999):
            modify_skill_data(character, f"{skill_path}.abilities.{ability_name}.unlocked", True)
            char.charSend(character, f"You've unlocked the ability: {ability_name.replace('_', ' ').title()}!")
```

## Pattern 2: Data Relationships and References

Create complex relationships between different auxiliary data sets.

### Guild System with Member Relationships

```python
# Complex guild system with member relationships
import auxiliary
import json
import char
import mudsys

class GuildManager:
    """Manages guild relationships and hierarchies."""
    
    def __init__(self):
        self.guild_cache = {}
    
    def create_guild(self, guild_name, founder):
        """Create a new guild with founder as leader."""
        
        guild_id = f"guild_{guild_name.lower().replace(' ', '_')}"
        
        guild_data = {
            "name": guild_name,
            "founded_date": mudsys.current_time(),
            "founder": char.charGetName(founder).lower(),
            "description": "",
            "motto": "",
            "ranks": {
                "leader": {
                    "level": 10,
                    "permissions": ["invite", "kick", "promote", "demote", "edit_guild", "manage_ranks"],
                    "members": [char.charGetName(founder).lower()]
                },
                "officer": {
                    "level": 5,
                    "permissions": ["invite", "kick", "promote_to_member"],
                    "members": []
                },
                "member": {
                    "level": 1,
                    "permissions": ["use_guild_chat"],
                    "members": []
                }
            },
            "resources": {
                "gold": 0,
                "reputation": 0,
                "territory": []
            },
            "relationships": {
                "allies": [],
                "enemies": [],
                "neutral": []
            }
        }
        
        # Store guild data
        auxiliary.worldSetAuxiliaryData(guild_id, json.dumps(guild_data))
        
        # Update founder's character data
        self.set_character_guild(founder, guild_id, "leader")
        
        return guild_id
    
    def set_character_guild(self, character, guild_id, rank):
        """Set a character's guild membership."""
        
        char_name = char.charGetName(character).lower()
        
        # Get existing character guild data
        guild_data_str = auxiliary.charGetAuxiliaryData(character, "guild_membership")
        
        if guild_data_str:
            try:
                guild_data = json.loads(guild_data_str)
            except json.JSONDecodeError:
                guild_data = {}
        else:
            guild_data = {}
        
        # Update membership
        guild_data.update({
            "guild_id": guild_id,
            "rank": rank,
            "join_date": mudsys.current_time(),
            "contributions": {
                "gold_donated": 0,
                "missions_completed": 0,
                "members_recruited": 0
            },
            "permissions": self.get_rank_permissions(guild_id, rank)
        })
        
        auxiliary.charSetAuxiliaryData(character, "guild_membership", json.dumps(guild_data))
    
    def get_guild_data(self, guild_id):
        """Get guild data with caching."""
        
        if guild_id in self.guild_cache:
            return self.guild_cache[guild_id]
        
        guild_data_str = auxiliary.worldGetAuxiliaryData(guild_id)
        if not guild_data_str:
            return None
        
        try:
            guild_data = json.loads(guild_data_str)
            self.guild_cache[guild_id] = guild_data
            return guild_data
        except json.JSONDecodeError:
            return None
    
    def get_character_guild_info(self, character):
        """Get comprehensive guild information for a character."""
        
        guild_data_str = auxiliary.charGetAuxiliaryData(character, "guild_membership")
        if not guild_data_str:
            return None
        
        try:
            char_guild_data = json.loads(guild_data_str)
            guild_id = char_guild_data.get("guild_id")
            
            if not guild_id:
                return None
            
            guild_data = self.get_guild_data(guild_id)
            if not guild_data:
                return None
            
            # Combine character and guild data
            return {
                "character_data": char_guild_data,
                "guild_data": guild_data,
                "rank_info": guild_data["ranks"].get(char_guild_data["rank"], {}),
                "member_count": sum(len(rank_data["members"]) for rank_data in guild_data["ranks"].values())
            }
            
        except (json.JSONDecodeError, KeyError):
            return None
    
    def get_rank_permissions(self, guild_id, rank):
        """Get permissions for a specific rank."""
        
        guild_data = self.get_guild_data(guild_id)
        if not guild_data:
            return []
        
        return guild_data.get("ranks", {}).get(rank, {}).get("permissions", [])
    
    def has_permission(self, character, permission):
        """Check if character has a specific guild permission."""
        
        guild_info = self.get_character_guild_info(character)
        if not guild_info:
            return False
        
        permissions = guild_info["character_data"].get("permissions", [])
        return permission in permissions

# Global guild manager instance
guild_manager = GuildManager()
```

## Pattern 3: Dynamic Behavior Modification

Use auxiliary data to modify object behavior dynamically.

### Adaptive NPC Behavior System

```python
# NPCs that adapt their behavior based on stored interaction history
import auxiliary
import json
import char
import random

class AdaptiveNPCBehavior:
    """System for NPCs that learn and adapt based on player interactions."""
    
    def __init__(self, npc):
        self.npc = npc
        self.load_behavior_data()
    
    def load_behavior_data(self):
        """Load NPC's behavioral data."""
        
        behavior_str = auxiliary.charGetAuxiliaryData(self.npc, "adaptive_behavior")
        
        if behavior_str:
            try:
                self.behavior_data = json.loads(behavior_str)
            except json.JSONDecodeError:
                self.behavior_data = self.create_default_behavior()
        else:
            self.behavior_data = self.create_default_behavior()
    
    def create_default_behavior(self):
        """Create default behavior patterns."""
        
        return {
            "personality_traits": {
                "friendliness": 50,  # 0-100 scale
                "trust": 50,
                "aggression": 30,
                "curiosity": 60,
                "helpfulness": 40
            },
            "interaction_history": {},  # player_name -> interaction data
            "learned_responses": {},    # situation -> preferred response
            "mood_modifiers": {
                "current_mood": "neutral",
                "mood_duration": 0,
                "mood_factors": []
            },
            "relationship_memory": {},  # player_name -> relationship data
            "behavioral_patterns": {
                "greeting_style": "formal",
                "conversation_depth": "surface",
                "trust_threshold": 60,
                "aggression_trigger": 80
            }
        }
    
    def save_behavior_data(self):
        """Save behavioral data back to auxiliary storage."""
        
        auxiliary.charSetAuxiliaryData(self.npc, "adaptive_behavior", json.dumps(self.behavior_data))
    
    def record_interaction(self, player, interaction_type, outcome):
        """Record an interaction and update NPC behavior."""
        
        player_name = char.charGetName(player).lower()
        
        # Initialize player history if needed
        if player_name not in self.behavior_data["interaction_history"]:
            self.behavior_data["interaction_history"][player_name] = {
                "total_interactions": 0,
                "positive_interactions": 0,
                "negative_interactions": 0,
                "interaction_types": {},
                "last_interaction": mudsys.current_time(),
                "relationship_score": 50  # Start neutral
            }
        
        history = self.behavior_data["interaction_history"][player_name]
        
        # Update interaction counts
        history["total_interactions"] += 1
        history["last_interaction"] = mudsys.current_time()
        
        if interaction_type not in history["interaction_types"]:
            history["interaction_types"][interaction_type] = {"count": 0, "success_rate": 0.5}
        
        history["interaction_types"][interaction_type]["count"] += 1
        
        # Update relationship based on outcome
        if outcome == "positive":
            history["positive_interactions"] += 1
            history["relationship_score"] = min(100, history["relationship_score"] + 2)
            self.adjust_personality_trait("friendliness", 1)
            self.adjust_personality_trait("trust", 1)
        elif outcome == "negative":
            history["negative_interactions"] += 1
            history["relationship_score"] = max(0, history["relationship_score"] - 3)
            self.adjust_personality_trait("trust", -1)
            if interaction_type == "combat":
                self.adjust_personality_trait("aggression", 2)
        
        # Update success rate for interaction type
        interaction_data = history["interaction_types"][interaction_type]
        success_count = interaction_data.get("success_count", 0)
        if outcome == "positive":
            success_count += 1
        
        interaction_data["success_count"] = success_count
        interaction_data["success_rate"] = success_count / interaction_data["count"]
        
        # Learn behavioral patterns
        self.learn_from_interaction(player_name, interaction_type, outcome)
        
        self.save_behavior_data()
    
    def adjust_personality_trait(self, trait, adjustment):
        """Adjust a personality trait within bounds."""
        
        current = self.behavior_data["personality_traits"][trait]
        new_value = max(0, min(100, current + adjustment))
        self.behavior_data["personality_traits"][trait] = new_value
    
    def learn_from_interaction(self, player_name, interaction_type, outcome):
        """Learn preferred responses based on interaction outcomes."""
        
        situation_key = f"{interaction_type}_{outcome}"
        
        if situation_key not in self.behavior_data["learned_responses"]:
            self.behavior_data["learned_responses"][situation_key] = {
                "response_weights": {},
                "total_occurrences": 0
            }
        
        learned = self.behavior_data["learned_responses"][situation_key]
        learned["total_occurrences"] += 1
        
        # Determine what response worked
        if outcome == "positive":
            current_mood = self.behavior_data["mood_modifiers"]["current_mood"]
            response_key = f"{current_mood}_response"
            
            if response_key not in learned["response_weights"]:
                learned["response_weights"][response_key] = 0
            
            learned["response_weights"][response_key] += 1
    
    def get_response_for_situation(self, player, situation):
        """Get the most appropriate response based on learned behavior."""
        
        player_name = char.charGetName(player).lower()
        
        # Get relationship data
        relationship_score = 50  # Default neutral
        if player_name in self.behavior_data["interaction_history"]:
            relationship_score = self.behavior_data["interaction_history"][player_name]["relationship_score"]
        
        # Check learned responses
        situation_key = f"{situation}_positive"  # Assume we want positive outcome
        
        if situation_key in self.behavior_data["learned_responses"]:
            learned = self.behavior_data["learned_responses"][situation_key]
            
            if learned["response_weights"]:
                # Choose response based on weights
                responses = list(learned["response_weights"].keys())
                weights = list(learned["response_weights"].values())
                
                # Weighted random selection
                total_weight = sum(weights)
                if total_weight > 0:
                    r = random.randint(1, total_weight)
                    current_weight = 0
                    
                    for response, weight in zip(responses, weights):
                        current_weight += weight
                        if r <= current_weight:
                            return self.generate_response(response, relationship_score)
        
        # Fall back to personality-based response
        return self.generate_personality_response(situation, relationship_score)
    
    def generate_response(self, response_type, relationship_score):
        """Generate actual response text based on type and relationship."""
        
        # This would contain actual response generation logic
        # For now, return a placeholder
        return f"[{response_type} response for relationship level {relationship_score}]"
    
    def generate_personality_response(self, situation, relationship_score):
        """Generate response based on current personality traits."""
        
        traits = self.behavior_data["personality_traits"]
        
        if situation == "greeting":
            if relationship_score > 70:
                return "Welcome back, my friend! It's always good to see you."
            elif relationship_score < 30:
                return "Oh... it's you again."
            else:
                return "Hello there."
        
        # Add more situation-specific responses based on personality
        return "I'm not sure how to respond to that."

# Usage in NPC trigger
def npc_talk_trigger(npc, player, speech):
    """Example NPC talk trigger using adaptive behavior."""
    
    behavior = AdaptiveNPCBehavior(npc)
    
    # Determine interaction type
    speech_lower = speech.lower()
    
    if "hello" in speech_lower or "hi" in speech_lower:
        response = behavior.get_response_for_situation(player, "greeting")
        behavior.record_interaction(player, "greeting", "positive")
    elif "help" in speech_lower:
        response = behavior.get_response_for_situation(player, "help_request")
        behavior.record_interaction(player, "help_request", "positive")
    else:
        response = behavior.get_response_for_situation(player, "general_talk")
        behavior.record_interaction(player, "general_talk", "neutral")
    
    char.charSendRoom(npc, f"{char.charGetName(npc)} says, '{response}'")
```

## Pattern 4: Performance Optimization with Caching

Implement sophisticated caching strategies for frequently accessed auxiliary data.

### Multi-Level Caching System

```python
# Advanced caching system for auxiliary data
import auxiliary
import json
import time
import weakref

class AuxiliaryDataCache:
    """Multi-level caching system for auxiliary data."""
    
    def __init__(self):
        self.memory_cache = {}      # Fast in-memory cache
        self.object_cache = {}      # Weak references to game objects
        self.dirty_keys = set()     # Keys that need to be written back
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "evictions": 0
        }
        self.max_cache_size = 1000
        self.cache_timeout = 300    # 5 minutes
    
    def get_cached_data(self, obj, key, use_cache=True):
        """Get auxiliary data with multi-level caching."""
        
        if not use_cache:
            return self._get_raw_data(obj, key)
        
        cache_key = self._make_cache_key(obj, key)
        current_time = time.time()
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            cache_entry = self.memory_cache[cache_key]
            
            # Check if cache entry is still valid
            if current_time - cache_entry["timestamp"] < self.cache_timeout:
                self.cache_stats["hits"] += 1
                return cache_entry["data"]
            else:
                # Cache expired, remove it
                del self.memory_cache[cache_key]
        
        # Cache miss - get from auxiliary data
        self.cache_stats["misses"] += 1
        raw_data = self._get_raw_data(obj, key)
        
        # Store in cache
        self._store_in_cache(cache_key, raw_data, current_time)
        
        return raw_data
    
    def set_cached_data(self, obj, key, data, write_through=False):
        """Set auxiliary data with caching."""
        
        cache_key = self._make_cache_key(obj, key)
        current_time = time.time()
        
        # Update cache
        self._store_in_cache(cache_key, data, current_time)
        
        if write_through:
            # Write immediately
            self._write_raw_data(obj, key, data)
            self.cache_stats["writes"] += 1
        else:
            # Mark as dirty for later write
            self.dirty_keys.add((obj, key, data))
    
    def flush_dirty_data(self):
        """Write all dirty data to auxiliary storage."""
        
        for obj, key, data in self.dirty_keys:
            self._write_raw_data(obj, key, data)
            self.cache_stats["writes"] += 1
        
        self.dirty_keys.clear()
    
    def _make_cache_key(self, obj, key):
        """Create a unique cache key for an object/key combination."""
        
        # Use object ID and key to create unique identifier
        obj_id = id(obj)
        return f"{obj_id}_{key}"
    
    def _get_raw_data(self, obj, key):
        """Get raw auxiliary data without caching."""
        
        if hasattr(obj, 'charGetAuxiliaryData'):
            return auxiliary.charGetAuxiliaryData(obj, key)
        elif hasattr(obj, 'roomGetAuxiliaryData'):
            return auxiliary.roomGetAuxiliaryData(obj, key)
        elif hasattr(obj, 'objGetAuxiliaryData'):
            return auxiliary.objGetAuxiliaryData(obj, key)
        else:
            return auxiliary.worldGetAuxiliaryData(key)
    
    def _write_raw_data(self, obj, key, data):
        """Write raw auxiliary data without caching."""
        
        if hasattr(obj, 'charSetAuxiliaryData'):
            auxiliary.charSetAuxiliaryData(obj, key, data)
        elif hasattr(obj, 'roomSetAuxiliaryData'):
            auxiliary.roomSetAuxiliaryData(obj, key, data)
        elif hasattr(obj, 'objSetAuxiliaryData'):
            auxiliary.objSetAuxiliaryData(obj, key, data)
        else:
            auxiliary.worldSetAuxiliaryData(key, data)
    
    def _store_in_cache(self, cache_key, data, timestamp):
        """Store data in memory cache with size management."""
        
        # Check if we need to evict old entries
        if len(self.memory_cache) >= self.max_cache_size:
            self._evict_old_entries()
        
        self.memory_cache[cache_key] = {
            "data": data,
            "timestamp": timestamp,
            "access_count": 1
        }
    
    def _evict_old_entries(self):
        """Evict old cache entries using LRU strategy."""
        
        current_time = time.time()
        entries_to_remove = []
        
        # Find expired entries first
        for cache_key, entry in self.memory_cache.items():
            if current_time - entry["timestamp"] > self.cache_timeout:
                entries_to_remove.append(cache_key)
        
        # If not enough expired entries, remove least recently used
        if len(entries_to_remove) < self.max_cache_size // 4:
            sorted_entries = sorted(
                self.memory_cache.items(),
                key=lambda x: (x[1]["timestamp"], x[1]["access_count"])
            )
            
            additional_removals = self.max_cache_size // 4 - len(entries_to_remove)
            for cache_key, _ in sorted_entries[:additional_removals]:
                if cache_key not in entries_to_remove:
                    entries_to_remove.append(cache_key)
        
        # Remove selected entries
        for cache_key in entries_to_remove:
            del self.memory_cache[cache_key]
            self.cache_stats["evictions"] += 1
    
    def get_cache_stats(self):
        """Get cache performance statistics."""
        
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total_requests,
            "cache_size": len(self.memory_cache),
            "dirty_keys": len(self.dirty_keys),
            **self.cache_stats
        }

# Global cache instance
aux_cache = AuxiliaryDataCache()

# Convenience functions
def get_cached_aux_data(obj, key):
    """Get auxiliary data with caching."""
    return aux_cache.get_cached_data(obj, key)

def set_cached_aux_data(obj, key, data, write_through=False):
    """Set auxiliary data with caching."""
    aux_cache.set_cached_data(obj, key, data, write_through)

def flush_aux_cache():
    """Flush all cached auxiliary data."""
    aux_cache.flush_dirty_data()
```

## Pattern 5: Data Validation and Integrity

Implement robust data validation for auxiliary data systems.

### Schema Validation System

```python
# Schema validation for auxiliary data
import json
import auxiliary

class AuxiliaryDataValidator:
    """Validates auxiliary data against predefined schemas."""
    
    def __init__(self):
        self.schemas = {}
        self.validation_errors = []
    
    def register_schema(self, data_type, schema):
        """Register a validation schema for a data type."""
        
        self.schemas[data_type] = schema
    
    def validate_data(self, data_type, data):
        """Validate data against registered schema."""
        
        if data_type not in self.schemas:
            return True, []  # No schema = no validation
        
        schema = self.schemas[data_type]
        self.validation_errors = []
        
        try:
            if isinstance(data, str):
                data = json.loads(data)
        except json.JSONDecodeError:
            return False, ["Invalid JSON format"]
        
        is_valid = self._validate_against_schema(data, schema, "")
        return is_valid, self.validation_errors
    
    def _validate_against_schema(self, data, schema, path):
        """Recursively validate data against schema."""
        
        is_valid = True
        
        # Check required fields
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    self.validation_errors.append(f"Missing required field: {path}.{field}")
                    is_valid = False
        
        # Check field types and constraints
        if "properties" in schema:
            for field, field_schema in schema["properties"].items():
                if field in data:
                    field_path = f"{path}.{field}" if path else field
                    
                    if not self._validate_field(data[field], field_schema, field_path):
                        is_valid = False
        
        return is_valid
    
    def _validate_field(self, value, field_schema, path):
        """Validate a single field against its schema."""
        
        # Type validation
        expected_type = field_schema.get("type")
        if expected_type:
            if expected_type == "string" and not isinstance(value, str):
                self.validation_errors.append(f"Field {path} must be a string")
                return False
            elif expected_type == "number" and not isinstance(value, (int, float)):
                self.validation_errors.append(f"Field {path} must be a number")
                return False
            elif expected_type == "integer" and not isinstance(value, int):
                self.validation_errors.append(f"Field {path} must be an integer")
                return False
            elif expected_type == "boolean" and not isinstance(value, bool):
                self.validation_errors.append(f"Field {path} must be a boolean")
                return False
            elif expected_type == "array" and not isinstance(value, list):
                self.validation_errors.append(f"Field {path} must be an array")
                return False
            elif expected_type == "object" and not isinstance(value, dict):
                self.validation_errors.append(f"Field {path} must be an object")
                return False
        
        # Range validation for numbers
        if isinstance(value, (int, float)):
            if "minimum" in field_schema and value < field_schema["minimum"]:
                self.validation_errors.append(f"Field {path} must be >= {field_schema['minimum']}")
                return False
            if "maximum" in field_schema and value > field_schema["maximum"]:
                self.validation_errors.append(f"Field {path} must be <= {field_schema['maximum']}")
                return False
        
        # String length validation
        if isinstance(value, str):
            if "minLength" in field_schema and len(value) < field_schema["minLength"]:
                self.validation_errors.append(f"Field {path} must be at least {field_schema['minLength']} characters")
                return False
            if "maxLength" in field_schema and len(value) > field_schema["maxLength"]:
                self.validation_errors.append(f"Field {path} must be at most {field_schema['maxLength']} characters")
                return False
        
        # Enum validation
        if "enum" in field_schema and value not in field_schema["enum"]:
            self.validation_errors.append(f"Field {path} must be one of: {field_schema['enum']}")
            return False
        
        # Nested object validation
        if expected_type == "object" and "properties" in field_schema:
            return self._validate_against_schema(value, field_schema, path)
        
        return True

# Global validator instance
aux_validator = AuxiliaryDataValidator()

# Register common schemas
aux_validator.register_schema("character_stats", {
    "type": "object",
    "required": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"],
    "properties": {
        "strength": {"type": "integer", "minimum": 1, "maximum": 100},
        "dexterity": {"type": "integer", "minimum": 1, "maximum": 100},
        "constitution": {"type": "integer", "minimum": 1, "maximum": 100},
        "intelligence": {"type": "integer", "minimum": 1, "maximum": 100},
        "wisdom": {"type": "integer", "minimum": 1, "maximum": 100},
        "charisma": {"type": "integer", "minimum": 1, "maximum": 100},
        "bonus_points": {"type": "integer", "minimum": 0}
    }
})

aux_validator.register_schema("guild_membership", {
    "type": "object",
    "required": ["guild_id", "rank", "join_date"],
    "properties": {
        "guild_id": {"type": "string", "minLength": 1},
        "rank": {"type": "string", "enum": ["leader", "officer", "member", "recruit"]},
        "join_date": {"type": "integer", "minimum": 0},
        "contributions": {
            "type": "object",
            "properties": {
                "gold_donated": {"type": "integer", "minimum": 0},
                "missions_completed": {"type": "integer", "minimum": 0},
                "members_recruited": {"type": "integer", "minimum": 0}
            }
        }
    }
})

def validate_and_set_aux_data(obj, key, data, data_type=None):
    """Validate and set auxiliary data."""
    
    if data_type:
        is_valid, errors = aux_validator.validate_data(data_type, data)
        
        if not is_valid:
            error_msg = "Validation errors: " + "; ".join(errors)
            raise ValueError(error_msg)
    
    # Convert to JSON string if needed
    if not isinstance(data, str):
        data = json.dumps(data)
    
    # Set the data
    if hasattr(obj, 'charSetAuxiliaryData'):
        auxiliary.charSetAuxiliaryData(obj, key, data)
    elif hasattr(obj, 'roomSetAuxiliaryData'):
        auxiliary.roomSetAuxiliaryData(obj, key, data)
    elif hasattr(obj, 'objSetAuxiliaryData'):
        auxiliary.objSetAuxiliaryData(obj, key, data)
    else:
        auxiliary.worldSetAuxiliaryData(key, data)
```

## Summary

These advanced auxiliary data patterns demonstrate:

1. **Hierarchical Data Structures** - Complex nested data for sophisticated systems
2. **Data Relationships** - Creating connections between different data sets
3. **Dynamic Behavior Modification** - Using data to change object behavior
4. **Performance Optimization** - Multi-level caching for frequently accessed data
5. **Data Validation** - Ensuring data integrity with schema validation

These patterns form the foundation for building complex, maintainable game systems that scale well and provide rich player experiences.

## Next Steps

- Study the [Complex Prototype Inheritance](../complex-prototype-inheritance/) patterns
- Learn [Debugging and Troubleshooting](../debugging-troubleshooting/) techniques
- Apply these patterns in your own advanced systems