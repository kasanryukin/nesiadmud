'''
mob_movement.py

Handles autonomous NPC movement within zone boundaries.
Designed to be called from heartbeat triggers on mobs with wanderer prototype.

Usage in OLC trigger:
  attempt_wander(me)
'''

import random

################################################################################
# Configuration
################################################################################

# Chance (0-100) that a mob will attempt to move on this heartbeat
# Adjust based on desired activity level (default: 40% per heartbeat)
WANDER_CHANCE = 100

# Mobs with these prototypes will NOT wander even if they have the trigger
NO_WANDER_PROTOTYPES = ["statue", "immobile", "shopkeeper"]

################################################################################
# Helper Functions
################################################################################

def get_mob_zone(mob):
    """
    Extract the zone key from a mob's current location.
    
    Args:
        mob: The mobile character
    
    Returns:
        Zone name (string) or None if mob not in a room
    
    Example:
        zone = get_mob_zone(mob)  # Returns "examples" from "tavern@examples"
    """
    if not mob or not mob.room:
        return None
    
    try:
        # Get the room's prototype key (format: name@zone)
        room_proto = mob.room.proto
        if not room_proto or '@' not in room_proto:
            return None
        
        # Extract zone part after the @
        return room_proto.split('@')[-1]
    except:
        return None


def get_exit_destination_zone(exit_obj, current_room):
    """
    Get the zone that an exit leads to.
    
    Args:
        exit_obj: The Exit object
        current_room: The room containing the exit
    
    Returns:
        Zone key (string) or None if zone can't be determined
    """
    if not exit_obj or not current_room:
        return None
    
    try:
        # Get the destination proto from the exit
        dest_proto = exit_obj.destproto
        
        if not dest_proto:
            return None
        
        # If destination already has @ symbol, extract zone from it
        if '@' in dest_proto:
            return dest_proto.split('@')[-1]
        
        # Otherwise, assume destination is in the same zone as current room
        return get_mob_zone(current_room)
        
    except:
        return None


def get_valid_exits(mob):
    """
    Get all exits from the mob's current room that stay within its home zone.
    
    Args:
        mob: The mobile character
    
    Returns:
        List of exit direction names (strings) that keep mob in zone
    """
    if not mob or not mob.room:
        return []
    
    home_zone = get_mob_zone(mob)
    if not home_zone:
        return []
    
    valid_exits = []
    
    try:
        # Get all exit names from the room (returns Python list)
        exit_names = mob.room.exits
        
        for exit_dir in exit_names:
            try:
                # Get the exit object
                exit_obj = mob.room.exits[exit_dir]
                if not exit_obj:
                    continue
                
                # Check if destination is in the same zone
                dest_zone = get_exit_destination_zone(exit_obj, mob.room)
                
                if dest_zone == home_zone:
                    valid_exits.append(exit_dir)
            except:
                # Skip exits that cause errors
                continue
    except:
        pass
    
    return valid_exits


def should_mob_wander(mob):
    """
    Determine if a mob should attempt to wander this heartbeat.
    Checks: wander chance, prototype restrictions, mob state.
    
    Args:
        mob: The mobile character
    
    Returns:
        True if mob should wander, False otherwise
    """
    if not mob:
        return False
    
    # Don't wander if chance check fails
    if random.randint(1, 100) > WANDER_CHANCE:
        return False
    
    # Don't wander if mob is a player character
    if mob.is_pc:
        return False
    
    # Don't wander if mob has a no-wander prototype
    for proto in NO_WANDER_PROTOTYPES:
        try:
            if mob.is_instance(proto):
                return False
        except:
            pass
    
    # Don't wander if not in a room
    if not mob.room:
        return False
    
    return True


################################################################################
# Main Movement Function (Called from Heartbeat Trigger)
################################################################################

def attempt_wander(mob):
    """
    Main function called from heartbeat trigger. Attempts to move a mob to a
    random valid exit within its home zone.
    
    Args:
        mob: The mobile character (passed as 'me' from trigger)
    
    Returns:
        True if movement was successful, False otherwise
    
    Usage in OLC trigger:
        attempt_wander(me)
    """
    if not mob or not should_mob_wander(mob):
        return False
    
    # Get valid exits that keep mob in zone
    valid_exits = get_valid_exits(mob)
    if not valid_exits:
        return False
    
    try:
        # Pick a random exit
        chosen_exit_dir = random.choice(valid_exits)
        
        # Get the exit object
        exit_obj = mob.room.exits[chosen_exit_dir]
        if not exit_obj:
            return False
        
        # Get the destination room
        dest_room = exit_obj.dest
        if not dest_room:
            return False
        
        # Move the mob to the new room
        # This triggers the "char_to_room" hook and all related systems
        mob.room = dest_room
        return True
        
    except:
        return False