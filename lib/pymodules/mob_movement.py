'''
mob_movement.py

Handles autonomous NPC movement within zone boundaries.
Mobs wander randomly through exits that keep them in their home zone.
'''

import mudsys, mud, random, hooks
import char as mudchar
import room as mudroom

################################################################################
# Configuration
################################################################################

# Chance (0-100) that a mob will attempt to move each pulse
# Adjust based on desired activity level
WANDER_CHANCE = 40

# Mobs with these prototypes will NOT wander
NO_WANDER_PROTOTYPES = ["statue", "guard_post", "immobile"]

# How many consecutive failed movement attempts before giving up this pulse
MAX_FAILED_ATTEMPTS = 3

################################################################################
# Helper Functions
################################################################################

def get_mob_zone(mob):
    """
    Extract the zone key from a mob's current location.
    Returns the zone name (e.g., 'examples') or None if mob not in a room.
    """
    if not mob or not mob.room:
        return None
    
    # Get the room's prototype key (format: name@zone)
    room_proto = mob.room.proto
    if not room_proto or '@' not in room_proto:
        return None
    
    # Extract zone part after the @
    return room_proto.split('@')[-1]


def get_exit_destination_zone(exit_data, current_room):
    """
    Get the zone of where an exit leads.
    Returns the destination zone or None if it can't be determined.
    
    Args:
        exit_data: The EXIT_DATA object
        current_room: The room containing the exit
    
    Returns:
        Zone key (string) or None
    """
    if not exit_data or not current_room:
        return None
    
    try:
        # Get the destination key from the exit
        dest_key = exit_data.to
        
        # If it already has a @ symbol, extract the zone from it
        if '@' in dest_key:
            return dest_key.split('@')[-1]
        
        # Otherwise, use the current room's zone
        current_zone = get_mob_zone(current_room)
        return current_zone if current_zone else None
        
    except:
        return None


def get_valid_exits(mob):
    """
    Get all exits from the mob's current room that stay within its home zone.
    
    Args:
        mob: The mobile character
    
    Returns:
        List of exit directions (strings) that keep mob in zone, or empty list
    """
    if not mob or not mob.room:
        return []
    
    home_zone = get_mob_zone(mob)
    if not home_zone:
        return []
    
    valid_exits = []
    
    try:
        # Get all exit names from the room
        exit_names = mob.room.exits
        
        for exit_dir in exit_names:
            try:
                exit_obj = mob.room.exits[exit_dir]
                dest_zone = get_exit_destination_zone(exit_obj, mob.room)
                
                # If destination is in the same zone, it's valid
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
    Determine if a mob should attempt to wander this pulse.
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
        if mob.is_instance(proto):
            return False
    
    # Don't wander if not in a room
    if not mob.room:
        return False
    
    return True


def attempt_mob_movement(mob):
    """
    Attempt to move a mob to a random valid exit.
    
    Args:
        mob: The mobile character to move
    
    Returns:
        True if movement was successful, False otherwise
    """
    if not mob or not should_mob_wander(mob):
        return False
    
    # Get valid exits that keep mob in zone
    valid_exits = get_valid_exits(mob)
    if not valid_exits:
        return False
    
    try:
        # Pick a random exit
        chosen_exit = random.choice(valid_exits)
        
        # Get the exit object
        exit_obj = mob.room.exits[chosen_exit]
        if not exit_obj:
            return False
        
        # Build the destination key
        dest_key = exit_obj.to
        if '@' not in dest_key:
            current_zone = get_mob_zone(mob)
            dest_key = dest_key + '@' + current_zone
        
        # Get the destination room
        dest_room = mudroom.get_room(dest_key)
        if not dest_room:
            return False
        
        # Move the mob
        # Note: Use the room movement system
        # This assumes there's a way to move mobs between rooms
        try:
            # Try to move using room handlers
            old_room = mob.room
            mob.room = dest_room
            return True
        except:
            return False
    
    except:
        return False


################################################################################
# Pulse Hook
################################################################################

def mob_wander_pulse():
    """
    Called each game pulse to process mob wandering for all active NPCs.
    Iterates through all mobiles and attempts movement for those that should wander.
    """
    try:
        # Get all active mobiles
        all_mobs = mudchar.char_list()
        
        for mob in all_mobs:
            if mob and mob.is_npc:
                # Attempt movement with retry logic
                failed_attempts = 0
                while failed_attempts < MAX_FAILED_ATTEMPTS:
                    if attempt_mob_movement(mob):
                        break  # Success, move to next mob
                    failed_attempts += 1
    
    except Exception as e:
        mud.log_string("Error in mob_wander_pulse: %s" % str(e))


################################################################################
# Initialization
################################################################################

def init_mob_movement():
    """Initialize the mob movement system by registering pulse hooks."""
    try:
        # Register the pulse hook
        # This assumes there's a hook system for pulses
        hooks.add("pulse", mob_wander_pulse)
        mud.log_string("Mobile wandering system initialized.")
    except:
        mud.log_string("Warning: Could not initialize mob wandering system.")


# Initialize on module load
init_mob_movement()