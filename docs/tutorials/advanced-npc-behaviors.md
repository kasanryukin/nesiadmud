---
layout: default
title: Advanced NPC Behaviors
parent: Build Complexity
grand_parent: Tutorials
nav_order: 1
permalink: /tutorials/advanced-npc-behaviors/
---

# Advanced NPC Behaviors

Learn to create sophisticated NPC AI systems using auxiliary data, complex state machines, and advanced interaction patterns.

## Overview

This tutorial builds on the basic NPC creation skills to develop advanced AI behaviors. You'll create NPCs with memory, emotional states, complex decision-making, and sophisticated interaction patterns that make them feel truly alive.

## Prerequisites

- Completed [Your First NPC](your-first-npc/)
- Completed [Basic Triggers and Scripts](basic-triggers-scripts/)
- Understanding of [Auxiliary Data](/core-concepts/auxiliary-data/)
- Intermediate Python programming skills

## What You'll Learn

- Advanced state management for NPCs
- Creating NPC memory and relationship systems
- Implementing emotional and mood systems
- Building complex conversation trees
- Creating goal-oriented NPC behavior
- Performance optimization for complex NPCs

## Step 1: Advanced State Management

Let's create an NPC with a sophisticated state system that tracks multiple aspects of behavior:

```python
# File: lib/pymodules/advanced_npc_ai.py

import mudsys
import char
import room
import auxiliary
import random
import event

class NPCState:
    """Class to manage complex NPC state."""
    
    def __init__(self, npc):
        self.npc = npc
        self.npc_name = char.charGetName(npc)
    
    def get_state(self, key, default=None):
        """Get a state value from auxiliary data."""
        value = auxiliary.charGetAuxiliaryData(self.npc, key)
        return value if value is not None else default
    
    def set_state(self, key, value):
        """Set a state value in auxiliary data."""
        auxiliary.charSetAuxiliaryData(self.npc, key, str(value))
    
    def get_numeric_state(self, key, default=0):
        """Get a numeric state value."""
        value = self.get_state(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def modify_state(self, key, delta, min_val=None, max_val=None):
        """Modify a numeric state value by delta."""
        current = self.get_numeric_state(key, 0)
        new_value = current + delta
        
        if min_val is not None:
            new_value = max(new_value, min_val)
        if max_val is not None:
            new_value = min(new_value, max_val)
        
        self.set_state(key, new_value)
        return new_value

def advanced_guard_ai(ch, actor, arg):
    """Advanced guard NPC with multiple behavioral states."""
    
    if char.charIsNPC(actor):
        return
    
    state = NPCState(ch)
    actor_name = char.charGetName(actor)
    guard_name = char.charGetName(ch)
    
    # Get current behavioral state
    current_state = state.get_state("behavior_state", "patrol")
    alertness = state.get_numeric_state("alertness", 50)
    suspicion = state.get_numeric_state("suspicion_" + actor_name.lower(), 0)
    
    # Determine reaction based on state and suspicion
    if current_state == "patrol":
        if suspicion > 70:
            # Become alert
            state.set_state("behavior_state", "alert")
            char.charSendRoom(ch, "%s stops patrolling and focuses intently on %s." % (guard_name, actor_name))
            
        elif suspicion > 30:
            # Become watchful
            state.set_state("behavior_state", "watchful")
            char.charSendRoom(ch, "%s keeps a careful eye on %s while continuing to patrol." % (guard_name, actor_name))
            
    elif current_state == "alert":
        if suspicion > 90:
            # Become hostile
            state.set_state("behavior_state", "hostile")
            char.charSendRoom(ch, "%s draws their weapon and confronts %s!" % (guard_name, actor_name))
            char.charSend(actor, "%s says, 'You're under arrest! Surrender now!'" % guard_name)
            
        elif suspicion < 20:
            # Calm down
            state.set_state("behavior_state", "patrol")
            char.charSendRoom(ch, "%s relaxes and resumes normal patrol duties." % guard_name)
    
    # Log state changes for debugging
    mudsys.log_string("Guard %s: state=%s, alertness=%d, suspicion=%d" % 
                     (guard_name, current_state, alertness, suspicion))

def guard_observe_behavior(ch, actor, action_type):
    """Guard observes and evaluates player behavior."""
    
    if char.charIsNPC(actor):
        return
    
    state = NPCState(ch)
    actor_name = char.charGetName(actor)
    suspicion_key = "suspicion_" + actor_name.lower()
    
    # Different actions affect suspicion differently
    suspicion_changes = {
        "sneak": 15,      # Sneaking is very suspicious
        "hide": 10,       # Hiding is suspicious
        "steal": 25,      # Stealing is extremely suspicious
        "attack": 50,     # Attacking is cause for immediate action
        "normal_move": -2, # Normal movement reduces suspicion
        "talk_friendly": -5, # Friendly conversation reduces suspicion
        "help_citizen": -10  # Helping others reduces suspicion significantly
    }
    
    suspicion_change = suspicion_changes.get(action_type, 0)
    new_suspicion = state.modify_state(suspicion_key, suspicion_change, 0, 100)
    
    # Update overall alertness based on highest suspicion
    max_suspicion = 0
    # In a real implementation, you'd check all players' suspicion levels
    # For now, just use this player's suspicion
    state.set_state("alertness", min(100, max(25, new_suspicion)))
    
    return new_suspicion

# Register the advanced guard AI
mudsys.add_char_method("advanced_guard_ai", advanced_guard_ai)
mudsys.add_char_method("guard_observe", guard_observe_behavior)
```

## Step 2: NPC Memory and Relationship System

Create NPCs that remember past interactions and build relationships:

```python
# Add to advanced_npc_ai.py

class NPCMemory:
    """Manage NPC memory and relationships."""
    
    def __init__(self, npc):
        self.npc = npc
        self.state = NPCState(npc)
    
    def remember_interaction(self, player_name, interaction_type, details=""):
        """Record an interaction with a player."""
        
        # Get current interaction count
        interaction_key = "interactions_" + player_name.lower()
        count = self.state.get_numeric_state(interaction_key, 0)
        count += 1
        self.state.set_state(interaction_key, count)
        
        # Store the most recent interaction
        recent_key = "recent_interaction_" + player_name.lower()
        self.state.set_state(recent_key, interaction_type)
        
        # Update relationship based on interaction type
        self.update_relationship(player_name, interaction_type)
        
        # Store interaction history (keep last 5 interactions)
        history_key = "history_" + player_name.lower()
        history = self.state.get_state(history_key, "")
        
        if history:
            history_list = history.split(",")
        else:
            history_list = []
        
        history_list.append(interaction_type)
        if len(history_list) > 5:
            history_list = history_list[-5:]  # Keep only last 5
        
        self.state.set_state(history_key, ",".join(history_list))
    
    def update_relationship(self, player_name, interaction_type):
        """Update relationship score based on interaction."""
        
        relationship_key = "relationship_" + player_name.lower()
        current_relationship = self.state.get_numeric_state(relationship_key, 0)
        
        # Relationship changes based on interaction type
        relationship_changes = {
            "helped": 10,
            "friendly_chat": 5,
            "gave_gift": 15,
            "completed_quest": 20,
            "rude": -8,
            "threatened": -15,
            "attacked": -25,
            "stole_from": -30
        }
        
        change = relationship_changes.get(interaction_type, 0)
        new_relationship = self.state.modify_state(relationship_key, change, -100, 100)
        
        return new_relationship
    
    def get_relationship_level(self, player_name):
        """Get the relationship level with a player."""
        
        relationship = self.state.get_numeric_state("relationship_" + player_name.lower(), 0)
        
        if relationship >= 80:
            return "best_friend"
        elif relationship >= 60:
            return "good_friend"
        elif relationship >= 30:
            return "friend"
        elif relationship >= 10:
            return "acquaintance"
        elif relationship >= -10:
            return "neutral"
        elif relationship >= -30:
            return "dislike"
        elif relationship >= -60:
            return "enemy"
        else:
            return "hated_enemy"
    
    def get_interaction_count(self, player_name):
        """Get total interactions with a player."""
        return self.state.get_numeric_state("interactions_" + player_name.lower(), 0)

def shopkeeper_with_memory(ch, actor, arg):
    """Shopkeeper that remembers customers and adjusts behavior."""
    
    if char.charIsNPC(actor):
        return
    
    memory = NPCMemory(ch)
    actor_name = char.charGetName(actor)
    shopkeeper_name = char.charGetName(ch)
    
    # Remember this interaction
    memory.remember_interaction(actor_name, "visited_shop")
    
    # Get relationship info
    relationship_level = memory.get_relationship_level(actor_name)
    interaction_count = memory.get_interaction_count(actor_name)
    
    # Customize greeting based on relationship and history
    if relationship_level == "best_friend":
        greeting = "My dear friend %s! Welcome back! I always have the best deals for you." % actor_name
    elif relationship_level == "good_friend":
        greeting = "Ah, %s! Good to see you again, my friend. What can I do for you today?" % actor_name
    elif relationship_level == "friend":
        greeting = "Hello %s! Nice to see a familiar face. How can I help?" % actor_name
    elif relationship_level == "acquaintance":
        greeting = "Welcome back, %s. What brings you to my shop today?" % actor_name
    elif relationship_level == "neutral":
        if interaction_count == 1:
            greeting = "Welcome to my shop, %s. First time here, I believe?" % actor_name
        else:
            greeting = "Welcome, %s. How can I assist you?" % actor_name
    elif relationship_level == "dislike":
        greeting = "Oh, it's you again, %s. What do you want?" % actor_name
    elif relationship_level == "enemy":
        greeting = "I don't want any trouble, %s. State your business quickly." % actor_name
    else:  # hated_enemy
        greeting = "Get out of my shop, %s! I don't serve your kind!" % actor_name
        char.charSendRoom(ch, "%s glares angrily at %s." % (shopkeeper_name, actor_name))
        return
    
    char.charSendRoom(ch, "%s says, '%s'" % (shopkeeper_name, greeting))
    
    # Add relationship-based pricing hints
    if relationship_level in ["best_friend", "good_friend"]:
        char.charSend(actor, "%s whispers, 'I'll give you my special discount, of course.'" % shopkeeper_name)
    elif relationship_level in ["dislike", "enemy"]:
        char.charSend(actor, "%s mutters something about 'difficult customers' under their breath." % shopkeeper_name)

# Register the memory-based shopkeeper
mudsys.add_char_method("shopkeeper_memory", shopkeeper_with_memory)
```

## Step 3: Emotional and Mood Systems

Create NPCs with dynamic emotional states that affect their behavior:

```python
# Add to advanced_npc_ai.py

class NPCEmotions:
    """Manage NPC emotional states."""
    
    def __init__(self, npc):
        self.npc = npc
        self.state = NPCState(npc)
        
        # Initialize base emotional stats if they don't exist
        emotions = ["happiness", "anger", "fear", "sadness", "excitement"]
        for emotion in emotions:
            if self.state.get_state(emotion) is None:
                self.state.set_state(emotion, 50)  # Neutral starting point
    
    def get_emotion(self, emotion_name):
        """Get current level of an emotion (0-100)."""
        return self.state.get_numeric_state(emotion_name, 50)
    
    def modify_emotion(self, emotion_name, change, decay_others=True):
        """Modify an emotion level."""
        new_level = self.state.modify_state(emotion_name, change, 0, 100)
        
        # Emotional states can affect each other
        if decay_others:
            if emotion_name == "happiness" and change > 0:
                # Happiness reduces sadness and anger
                self.state.modify_state("sadness", -change//2, 0, 100)
                self.state.modify_state("anger", -change//3, 0, 100)
            elif emotion_name == "anger" and change > 0:
                # Anger reduces happiness and increases fear in others
                self.state.modify_state("happiness", -change//2, 0, 100)
            elif emotion_name == "fear" and change > 0:
                # Fear reduces excitement and happiness
                self.state.modify_state("excitement", -change//2, 0, 100)
                self.state.modify_state("happiness", -change//3, 0, 100)
        
        return new_level
    
    def get_dominant_emotion(self):
        """Get the currently dominant emotion."""
        emotions = {
            "happiness": self.get_emotion("happiness"),
            "anger": self.get_emotion("anger"),
            "fear": self.get_emotion("fear"),
            "sadness": self.get_emotion("sadness"),
            "excitement": self.get_emotion("excitement")
        }
        
        return max(emotions, key=emotions.get)
    
    def get_mood_description(self):
        """Get a description of the current mood."""
        dominant = self.get_dominant_emotion()
        level = self.get_emotion(dominant)
        
        if level > 80:
            intensity = "extremely"
        elif level > 65:
            intensity = "very"
        elif level > 55:
            intensity = "somewhat"
        else:
            intensity = "slightly"
        
        mood_descriptions = {
            "happiness": f"{intensity} cheerful",
            "anger": f"{intensity} irritated",
            "fear": f"{intensity} nervous",
            "sadness": f"{intensity} melancholy",
            "excitement": f"{intensity} energetic"
        }
        
        return mood_descriptions.get(dominant, "in a neutral mood")

def emotional_npc_heartbeat(ch):
    """Heartbeat function for NPCs with emotional systems."""
    
    emotions = NPCEmotions(ch)
    char_name = char.charGetName(ch)
    
    # Emotions naturally decay toward neutral over time
    emotion_names = ["happiness", "anger", "fear", "sadness", "excitement"]
    
    for emotion in emotion_names:
        current = emotions.get_emotion(emotion)
        if current > 50:
            emotions.modify_emotion(emotion, -1, decay_others=False)
        elif current < 50:
            emotions.modify_emotion(emotion, 1, decay_others=False)
    
    # Occasional emotional expressions based on dominant emotion
    if random.randint(1, 20) == 1:
        dominant = emotions.get_dominant_emotion()
        level = emotions.get_emotion(dominant)
        
        if level > 70:  # Only express strong emotions
            expressions = {
                "happiness": [
                    f"{char_name} hums a cheerful tune.",
                    f"{char_name} smiles broadly at nothing in particular.",
                    f"{char_name} seems to be in excellent spirits."
                ],
                "anger": [
                    f"{char_name} scowls and mutters under their breath.",
                    f"{char_name} clenches their fists in frustration.",
                    f"{char_name} looks around with an irritated expression."
                ],
                "fear": [
                    f"{char_name} glances around nervously.",
                    f"{char_name} jumps at a small sound.",
                    f"{char_name} seems on edge about something."
                ],
                "sadness": [
                    f"{char_name} sighs deeply.",
                    f"{char_name} looks downcast and melancholy.",
                    f"{char_name} stares off into the distance sadly."
                ],
                "excitement": [
                    f"{char_name} bounces slightly with energy.",
                    f"{char_name} looks around with bright, eager eyes.",
                    f"{char_name} seems barely able to contain their enthusiasm."
                ]
            }
            
            if dominant in expressions:
                expression = random.choice(expressions[dominant])
                char.charSendRoom(ch, expression)

def emotional_npc_interaction(ch, actor, interaction_type):
    """Handle interactions that affect NPC emotions."""
    
    if char.charIsNPC(actor):
        return
    
    emotions = NPCEmotions(ch)
    actor_name = char.charGetName(actor)
    char_name = char.charGetName(ch)
    
    # Different interactions affect emotions differently
    emotion_effects = {
        "complimented": {"happiness": 15, "sadness": -5},
        "insulted": {"anger": 20, "happiness": -10, "sadness": 5},
        "threatened": {"fear": 25, "anger": 10, "happiness": -15},
        "helped": {"happiness": 20, "excitement": 10},
        "ignored": {"sadness": 5, "happiness": -3},
        "surprised": {"excitement": 15, "fear": 5},
        "comforted": {"happiness": 10, "sadness": -15, "fear": -10}
    }
    
    if interaction_type in emotion_effects:
        effects = emotion_effects[interaction_type]
        
        for emotion, change in effects.items():
            emotions.modify_emotion(emotion, change)
        
        # Get the NPC's emotional response
        mood = emotions.get_mood_description()
        
        # Provide feedback about the emotional state change
        responses = {
            "complimented": f"{char_name} beams with pleasure at the compliment.",
            "insulted": f"{char_name}'s face darkens with anger.",
            "threatened": f"{char_name} takes a step back, looking frightened.",
            "helped": f"{char_name} looks grateful and pleased.",
            "surprised": f"{char_name} looks startled but intrigued.",
            "comforted": f"{char_name} seems to relax and feel better."
        }
        
        if interaction_type in responses:
            char.charSendRoom(ch, responses[interaction_type])
            char.charSend(actor, f"{char_name} seems {mood}.")

# Register emotional NPC functions
mudsys.add_char_method("emotional_heartbeat", emotional_npc_heartbeat)
mudsys.add_char_method("emotional_interaction", emotional_npc_interaction)
```

## Step 4: Complex Conversation Trees

Create sophisticated dialogue systems with branching conversations:

```python
# Add to advanced_npc_ai.py

class ConversationTree:
    """Manage complex conversation trees for NPCs."""
    
    def __init__(self, npc):
        self.npc = npc
        self.state = NPCState(npc)
        self.memory = NPCMemory(npc)
    
    def start_conversation(self, player, topic="greeting"):
        """Start a conversation with a player."""
        player_name = char.charGetName(player)
        
        # Set conversation state
        self.state.set_state(f"conversation_with_{player_name.lower()}", topic)
        self.state.set_state(f"conversation_step_{player_name.lower()}", "1")
        
        # Get appropriate response based on topic and relationship
        response = self.get_conversation_response(player, topic, "1")
        return response
    
    def continue_conversation(self, player, player_response):
        """Continue an ongoing conversation."""
        player_name = char.charGetName(player)
        
        current_topic = self.state.get_state(f"conversation_with_{player_name.lower()}")
        current_step = self.state.get_state(f"conversation_step_{player_name.lower()}", "1")
        
        if not current_topic:
            return self.start_conversation(player)
        
        # Process the player's response and determine next step
        next_step = self.process_response(player, current_topic, current_step, player_response)
        
        if next_step == "end":
            # End conversation
            self.state.set_state(f"conversation_with_{player_name.lower()}", "")
            return "It was nice talking with you!"
        
        # Update conversation state
        self.state.set_state(f"conversation_step_{player_name.lower()}", next_step)
        
        # Get response for next step
        return self.get_conversation_response(player, current_topic, next_step)
    
    def get_conversation_response(self, player, topic, step):
        """Get the appropriate response for a conversation step."""
        player_name = char.charGetName(player)
        relationship = self.memory.get_relationship_level(player_name)
        
        # Define conversation trees
        conversations = {
            "greeting": {
                "1": {
                    "neutral": "Hello there. What brings you here?",
                    "friend": f"Good to see you again, {player_name}! How have you been?",
                    "enemy": f"Oh, it's you, {player_name}. What do you want?"
                }
            },
            "quest_offer": {
                "1": {
                    "neutral": "I have a task that needs doing. Are you interested?",
                    "friend": f"I could use your help with something, {player_name}. Interested?",
                    "enemy": "I suppose even you might be useful for this task."
                },
                "2": {
                    "accepted": "Excellent! I need you to retrieve a lost artifact from the old ruins.",
                    "declined": "I understand. Perhaps another time.",
                    "more_info": "The artifact is a crystal orb that was stolen by bandits. It's very important to our village."
                },
                "3": {
                    "accepted": "The ruins are to the north. Be careful - they're dangerous.",
                    "questions": "What would you like to know more about?"
                }
            },
            "personal_story": {
                "1": {
                    "friend": "You know, I haven't always lived here. I used to be an adventurer like you.",
                    "neutral": "I don't usually share personal stories, but you seem trustworthy."
                },
                "2": {
                    "interested": "I traveled the world for years, seeking ancient knowledge and lost treasures.",
                    "not_interested": "Well, perhaps that's a story for another time."
                }
            }
        }
        
        # Get relationship category for response selection
        relationship_category = "neutral"
        if relationship in ["best_friend", "good_friend", "friend"]:
            relationship_category = "friend"
        elif relationship in ["enemy", "hated_enemy"]:
            relationship_category = "enemy"
        
        # Get the appropriate response
        if topic in conversations and step in conversations[topic]:
            step_responses = conversations[topic][step]
            if relationship_category in step_responses:
                return step_responses[relationship_category]
            elif "neutral" in step_responses:
                return step_responses["neutral"]
        
        return "I'm not sure what to say about that."
    
    def process_response(self, player, topic, step, player_response):
        """Process player response and determine next conversation step."""
        response_lower = player_response.lower()
        
        # Simple keyword-based response processing
        if topic == "quest_offer" and step == "1":
            if any(word in response_lower for word in ["yes", "accept", "sure", "okay"]):
                return "2"
            elif any(word in response_lower for word in ["no", "decline", "not interested"]):
                return "end"
            elif any(word in response_lower for word in ["info", "more", "tell me", "what"]):
                return "2"
        
        elif topic == "quest_offer" and step == "2":
            if any(word in response_lower for word in ["yes", "accept", "do it"]):
                # Remember that player accepted quest
                self.memory.remember_interaction(char.charGetName(player), "accepted_quest")
                return "3"
            elif any(word in response_lower for word in ["question", "ask", "more"]):
                return "3"
        
        elif topic == "personal_story" and step == "1":
            if any(word in response_lower for word in ["interested", "tell me", "continue", "yes"]):
                return "2"
            else:
                return "end"
        
        # Default: continue conversation or end
        return "end"

def conversation_npc_speech(ch, actor, speech):
    """Handle speech-based conversations with advanced NPCs."""
    
    if char.charIsNPC(actor):
        return
    
    conversation = ConversationTree(ch)
    actor_name = char.charGetName(actor)
    npc_name = char.charGetName(ch)
    
    # Check if we're in an ongoing conversation
    current_topic = conversation.state.get_state(f"conversation_with_{actor_name.lower()}")
    
    if current_topic:
        # Continue existing conversation
        response = conversation.continue_conversation(actor, speech)
    else:
        # Start new conversation based on what the player said
        speech_lower = speech.lower()
        
        if any(word in speech_lower for word in ["hello", "hi", "greetings"]):
            response = conversation.start_conversation(actor, "greeting")
        elif any(word in speech_lower for word in ["quest", "task", "job", "help"]):
            response = conversation.start_conversation(actor, "quest_offer")
        elif any(word in speech_lower for word in ["story", "past", "history", "yourself"]):
            response = conversation.start_conversation(actor, "personal_story")
        else:
            # Generic response
            response = "I'm not sure what you mean by that."
    
    # Send the response
    char.charSendRoom(ch, f"{npc_name} says, '{response}'")
    
    # Remember this interaction
    conversation.memory.remember_interaction(actor_name, "friendly_chat")

# Register conversation system
mudsys.add_char_method("conversation_speech", conversation_npc_speech)
```

## Step 5: Goal-Oriented Behavior

Create NPCs that pursue goals and adapt their behavior accordingly:

```python
# Add to advanced_npc_ai.py

class NPCGoals:
    """Manage NPC goals and goal-oriented behavior."""
    
    def __init__(self, npc):
        self.npc = npc
        self.state = NPCState(npc)
    
    def set_goal(self, goal_type, priority=50, details=None):
        """Set a new goal for the NPC."""
        goal_data = {
            "type": goal_type,
            "priority": priority,
            "details": details or {},
            "progress": 0,
            "created_time": mudsys.current_time()
        }
        
        # Store goal (simplified - in reality you'd want a more complex goal system)
        self.state.set_state("current_goal", goal_type)
        self.state.set_state("goal_priority", priority)
        self.state.set_state("goal_progress", 0)
        
        return goal_data
    
    def get_current_goal(self):
        """Get the NPC's current goal."""
        goal_type = self.state.get_state("current_goal")
        if not goal_type:
            return None
        
        return {
            "type": goal_type,
            "priority": self.state.get_numeric_state("goal_priority", 50),
            "progress": self.state.get_numeric_state("goal_progress", 0)
        }
    
    def update_goal_progress(self, progress_delta):
        """Update progress toward current goal."""
        current_progress = self.state.get_numeric_state("goal_progress", 0)
        new_progress = min(100, current_progress + progress_delta)
        self.state.set_state("goal_progress", new_progress)
        
        if new_progress >= 100:
            self.complete_goal()
        
        return new_progress
    
    def complete_goal(self):
        """Complete the current goal and set a new one."""
        completed_goal = self.state.get_state("current_goal")
        
        # Clear current goal
        self.state.set_state("current_goal", "")
        self.state.set_state("goal_progress", 0)
        
        # Set a new goal based on NPC type and situation
        self.choose_new_goal()
        
        return completed_goal
    
    def choose_new_goal(self):
        """Choose a new goal based on NPC's situation."""
        # This would be customized based on NPC type
        possible_goals = [
            ("patrol_area", 60),
            ("socialize", 40),
            ("maintain_equipment", 30),
            ("rest", 20)
        ]
        
        # Choose goal based on weighted random selection
        total_weight = sum(weight for _, weight in possible_goals)
        choice = random.randint(1, total_weight)
        
        current_weight = 0
        for goal, weight in possible_goals:
            current_weight += weight
            if choice <= current_weight:
                self.set_goal(goal, weight)
                break

def goal_oriented_npc_heartbeat(ch):
    """Heartbeat for NPCs with goal-oriented behavior."""
    
    goals = NPCGoals(ch)
    char_name = char.charGetName(ch)
    
    current_goal = goals.get_current_goal()
    if not current_goal:
        goals.choose_new_goal()
        current_goal = goals.get_current_goal()
    
    if not current_goal:
        return
    
    goal_type = current_goal["type"]
    progress = current_goal["progress"]
    
    # Execute behavior based on current goal
    if goal_type == "patrol_area":
        if random.randint(1, 10) == 1:  # Occasionally show patrol behavior
            actions = [
                f"{char_name} looks around the area carefully.",
                f"{char_name} checks the perimeter.",
                f"{char_name} pauses to listen for any unusual sounds."
            ]
            action = random.choice(actions)
            char.charSendRoom(ch, action)
            goals.update_goal_progress(5)
    
    elif goal_type == "socialize":
        # Look for players to interact with
        rm = char.charGetRoom(ch)
        if rm:
            chars_in_room = room.roomGetChars(rm)
            players = [c for c in chars_in_room if not char.charIsNPC(c) and c != ch]
            
            if players and random.randint(1, 15) == 1:
                target_player = random.choice(players)
                player_name = char.charGetName(target_player)
                
                greetings = [
                    f"{char_name} nods friendly at {player_name}.",
                    f"{char_name} says, 'Nice day, isn't it, {player_name}?'",
                    f"{char_name} smiles at {player_name}."
                ]
                
                greeting = random.choice(greetings)
                char.charSendRoom(ch, greeting)
                goals.update_goal_progress(10)
    
    elif goal_type == "maintain_equipment":
        if random.randint(1, 12) == 1:
            actions = [
                f"{char_name} inspects their equipment carefully.",
                f"{char_name} polishes their gear.",
                f"{char_name} adjusts their equipment."
            ]
            action = random.choice(actions)
            char.charSendRoom(ch, action)
            goals.update_goal_progress(8)
    
    elif goal_type == "rest":
        if random.randint(1, 8) == 1:
            actions = [
                f"{char_name} stretches and relaxes.",
                f"{char_name} takes a moment to rest.",
                f"{char_name} sits down briefly to recover."
            ]
            action = random.choice(actions)
            char.charSendRoom(ch, action)
            goals.update_goal_progress(15)

# Register goal-oriented behavior
mudsys.add_char_method("goal_oriented_heartbeat", goal_oriented_npc_heartbeat)
```

## Step 6: Performance Optimization

Optimize complex NPC systems for better performance:

```python
# Add to advanced_npc_ai.py

class NPCPerformanceManager:
    """Manage performance for complex NPC systems."""
    
    @staticmethod
    def should_process_npc(ch, base_chance=10):
        """Determine if an NPC should process complex AI this heartbeat."""
        
        # Don't process if no players are around
        rm = char.charGetRoom(ch)
        if not rm:
            return False
        
        chars_in_room = room.roomGetChars(rm)
        players_present = any(not char.charIsNPC(c) for c in chars_in_room)
        
        if not players_present:
            return False
        
        # Use random chance to distribute processing load
        return random.randint(1, 100) <= base_chance
    
    @staticmethod
    def cleanup_old_data(ch, max_age_hours=24):
        """Clean up old auxiliary data to prevent memory bloat."""
        
        # This would implement cleanup of old interaction data
        # For now, just a placeholder
        current_time = mudsys.current_time()
        
        # In a real implementation, you'd iterate through auxiliary data
        # and remove entries older than max_age_hours
        pass
    
    @staticmethod
    def batch_process_npcs(npc_list, process_function):
        """Process multiple NPCs in batches to spread load."""
        
        batch_size = 5  # Process 5 NPCs per call
        
        for i in range(0, len(npc_list), batch_size):
            batch = npc_list[i:i + batch_size]
            for npc in batch:
                try:
                    process_function(npc)
                except Exception as e:
                    mudsys.log_string(f"Error processing NPC {char.charGetName(npc)}: {e}")

def optimized_complex_npc_heartbeat(ch):
    """Optimized heartbeat for complex NPCs."""
    
    # Only process complex AI occasionally
    if not NPCPerformanceManager.should_process_npc(ch, 15):
        return
    
    try:
        # Run the various AI systems
        emotional_npc_heartbeat(ch)
        goal_oriented_npc_heartbeat(ch)
        
        # Occasionally clean up old data
        if random.randint(1, 100) == 1:
            NPCPerformanceManager.cleanup_old_data(ch)
    
    except Exception as e:
        mudsys.log_string(f"Error in complex NPC heartbeat for {char.charGetName(ch)}: {e}")

# Register optimized heartbeat
mudsys.add_char_method("optimized_complex_heartbeat", optimized_complex_npc_heartbeat)
```

## Best Practices for Advanced NPC AI

### 1. Layer Complexity Gradually
Start with simple behaviors and add complexity incrementally:

```python
# Good: Layered approach
def simple_npc_ai(ch, actor, arg):
    # Basic interaction
    pass

def enhanced_npc_ai(ch, actor, arg):
    # Call simple AI first
    simple_npc_ai(ch, actor, arg)
    # Add enhanced features
    pass
```

### 2. Use State Machines
Organize complex behaviors with clear state transitions:

```python
def state_machine_npc(ch):
    current_state = get_npc_state(ch, "ai_state", "idle")
    
    if current_state == "idle":
        # Idle behavior
        pass
    elif current_state == "alert":
        # Alert behavior
        pass
    # etc.
```

### 3. Balance Realism and Performance
Don't make NPCs too complex if it impacts game performance:

```python
# Use random chances to limit processing
if random.randint(1, 20) == 1:
    # Complex behavior
    pass
```

### 4. Provide Debug Tools
Create commands to inspect NPC state:

```python
def cmd_npc_debug(ch, cmd, arg):
    """Debug command to inspect NPC state."""
    # Implementation for debugging NPC AI
    pass
```

## Next Steps

Now that you understand advanced NPC behaviors:

1. **Try [Complex Room Interactions](complex-room-interactions/)** for environmental AI
2. **Learn [Using the Event System](using-event-system/)** for timed NPC behaviors
3. **Explore [Object Scripting](object-scripting-item-types/)** for interactive items

## Summary

You've learned to:
- Create sophisticated NPC state management systems
- Implement memory and relationship systems
- Build emotional and mood systems for NPCs
- Design complex conversation trees
- Create goal-oriented NPC behavior
- Optimize performance for complex AI systems

## Troubleshooting

**NPCs behaving erratically?**
- Check state transitions in your AI logic
- Add debug logging to trace behavior
- Verify auxiliary data is being stored correctly

**Performance issues with complex NPCs?**
- Reduce heartbeat frequency for complex operations
- Use random chances to distribute processing load
- Clean up old auxiliary data regularly

**Memory/relationship systems not working?**
- Verify auxiliary data keys are consistent
- Check that interaction types are being recorded correctly
- Test with debug commands to inspect NPC state

Ready for more advanced topics? Continue with [Complex Room Interactions](complex-room-interactions/)!